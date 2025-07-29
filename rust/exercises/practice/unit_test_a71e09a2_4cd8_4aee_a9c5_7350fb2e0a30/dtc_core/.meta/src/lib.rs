use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};
use std::thread;
use std::sync::mpsc;

pub trait Resource: Send + Sync {
    fn prepare(&self) -> Result<bool, String>;
    fn commit(&self) -> Result<(), String>;
    fn rollback(&self) -> Result<(), String>;
}

pub struct TransactionCoordinator {
    // mapping from transaction id to its enlisted resources
    transactions: Mutex<HashMap<u64, Vec<Arc<dyn Resource + Send + Sync>>>>,
    id_counter: AtomicU64,
}

impl TransactionCoordinator {
    pub fn new() -> Self {
        TransactionCoordinator {
            transactions: Mutex::new(HashMap::new()),
            id_counter: AtomicU64::new(1),
        }
    }

    pub fn begin_transaction(&self) -> u64 {
        let tx_id = self.id_counter.fetch_add(1, Ordering::SeqCst);
        let mut txs = self.transactions.lock().unwrap();
        txs.insert(tx_id, Vec::new());
        println!("Transaction {} started", tx_id);
        tx_id
    }

    pub fn enlist_resource(&self, tx_id: u64, resource: Arc<dyn Resource + Send + Sync>) -> Result<(), String> {
        let mut txs = self.transactions.lock().unwrap();
        if let Some(resources) = txs.get_mut(&tx_id) {
            resources.push(resource);
            println!("Resource enlisted to transaction {}", tx_id);
            Ok(())
        } else {
            Err(format!("Transaction {} not found", tx_id))
        }
    }

    pub fn prepare_transaction(&self, tx_id: u64, timeout: Duration) -> Result<(), String> {
        let resources = {
            let txs = self.transactions.lock().unwrap();
            match txs.get(&tx_id) {
                Some(res_list) => res_list.clone(),
                None => return Err(format!("Transaction {} not found", tx_id)),
            }
        };

        // Prepare each resource concurrently and collect the results.
        let mut handles = Vec::new();
        for resource in resources.iter() {
            let res_clone = resource.clone();
            let (sender, receiver) = mpsc::channel();
            let handle = thread::spawn(move || {
                let result = res_clone.prepare();
                let _ = sender.send(result);
            });
            handles.push((handle, receiver));
        }

        let start = Instant::now();
        for (handle, receiver) in handles {
            let remaining = timeout.checked_sub(start.elapsed()).unwrap_or(Duration::from_secs(0));
            match receiver.recv_timeout(remaining) {
                Ok(prepare_result) => {
                    match prepare_result {
                        Ok(true) => {
                            // resource is prepared
                        },
                        Ok(false) => {
                            println!("Resource preparation returned false, rolling back transaction {}", tx_id);
                            let _ = self.rollback_transaction(tx_id);
                            return Err("A resource could not prepare the transaction".to_string());
                        },
                        Err(e) => {
                            println!("Resource returned error during preparation: {}, rolling back transaction {}", e, tx_id);
                            let _ = self.rollback_transaction(tx_id);
                            return Err(format!("Error during resource prepare: {}", e));
                        },
                    }
                },
                Err(_) => {
                    println!("Resource preparation timed out, rolling back transaction {}", tx_id);
                    let _ = self.rollback_transaction(tx_id);
                    return Err("Resource preparation timed out".to_string());
                }
            }
        }
        println!("Transaction {} prepared successfully", tx_id);
        Ok(())
    }

    pub fn commit_transaction(&self, tx_id: u64) -> Result<(), String> {
        let resources = {
            let mut txs = self.transactions.lock().unwrap();
            match txs.remove(&tx_id) {
                Some(res_list) => res_list,
                None => return Err(format!("Transaction {} not found", tx_id)),
            }
        };

        let mut commit_error = None;
        for resource in resources.iter() {
            match resource.commit() {
                Ok(()) => {
                    // Commit succeeded for resource.
                },
                Err(e) => {
                    commit_error = Some(e);
                    break;
                },
            }
        }
        if let Some(err) = commit_error {
            println!("Commit error encountered in transaction {}: {}. Initiating rollback.", tx_id, err);
            // If commit fails for any resource, rollback remaining resources.
            let _ = self.rollback_transaction(tx_id);
            return Err(format!("Commit failed: {}", err));
        }
        println!("Transaction {} committed successfully", tx_id);
        Ok(())
    }

    pub fn rollback_transaction(&self, tx_id: u64) -> Result<(), String> {
        let resources = {
            let mut txs = self.transactions.lock().unwrap();
            // Even if transaction not found, we can consider it already rolled back.
            txs.remove(&tx_id).unwrap_or(Vec::new())
        };

        let mut rollback_errors = Vec::new();
        for resource in resources.iter() {
            if let Err(e) = resource.rollback() {
                rollback_errors.push(e);
            }
        }
        if rollback_errors.is_empty() {
            println!("Transaction {} rolled back successfully", tx_id);
            Ok(())
        } else {
            let error_msg = rollback_errors.join(", ");
            println!("Rollback encountered errors in transaction {}: {}", tx_id, error_msg);
            Err(error_msg)
        }
    }
}