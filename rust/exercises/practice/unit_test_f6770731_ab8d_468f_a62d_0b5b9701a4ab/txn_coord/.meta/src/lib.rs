use std::collections::HashMap;
use std::sync::{Arc, Mutex, mpsc};
use std::time::{Duration, Instant};
use std::fs::{OpenOptions, File};
use std::io::{Write, BufRead, BufReader};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Vote {
    Commit,
    Abort,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TransactionOutcome {
    Commit,
    Abort,
}

#[derive(Debug, Clone)]
pub struct Operation {
    pub resource_id: u64,
    pub op_id: u64,
}

pub trait ResourceManager: Send + Sync {
    fn prepare(&self, txn_id: u64, op_id: u64) -> Vote;
    fn commit(&self, txn_id: u64);
    fn abort(&self, txn_id: u64);
}

pub struct TransactionManager {
    timeout: Duration,
    log_file: String,
    resource_managers: Mutex<HashMap<u64, Arc<dyn ResourceManager>>>,
}

impl TransactionManager {
    pub fn new(timeout: Duration, log_file: &str) -> Self {
        // Truncate any existing log file.
        let _ = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(log_file);

        TransactionManager {
            timeout,
            log_file: log_file.to_string(),
            resource_managers: Mutex::new(HashMap::new()),
        }
    }

    pub fn register_resource_manager(&self, resource_id: u64, manager: Arc<dyn ResourceManager>) {
        let mut rms = self.resource_managers.lock().unwrap();
        rms.insert(resource_id, manager);
    }

    fn log_event(&self, event: &str) {
        if let Ok(mut file) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.log_file)
        {
            let _ = writeln!(file, "{}", event);
        }
    }

    pub fn submit_transaction(&self, txn_id: u64, ops: Vec<Operation>) -> TransactionOutcome {
        self.log_event(&format!("START {}", txn_id));

        // Prepare phase: spawn a thread for each operation to call prepare.
        let (tx, rx) = mpsc::channel();
        let mut handles = Vec::new();
        let rms = self.resource_managers.lock().unwrap().clone();

        for op in ops.iter() {
            let tx_clone = tx.clone();
            let rm_option = rms.get(&op.resource_id).cloned();
            let op_clone = op.clone();
            let txn_id_clone = txn_id;
            let timeout = self.timeout;

            self.log_event(&format!("PREPARE {} {} {}", txn_id, op.resource_id, op.op_id));
            let handle = std::thread::spawn(move || {
                let start = Instant::now();
                if let Some(rm) = rm_option {
                    let vote = rm.prepare(txn_id_clone, op_clone.op_id);
                    // If prepare takes longer than allowed timeout, simulate timeout by returning Abort.
                    if start.elapsed() > timeout {
                        let _ = tx_clone.send((op_clone.resource_id, Vote::Abort));
                    } else {
                        let _ = tx_clone.send((op_clone.resource_id, vote));
                    }
                } else {
                    // Missing resource manager defaults to abort.
                    let _ = tx_clone.send((op_clone.resource_id, Vote::Abort));
                }
            });
            handles.push(handle);
        }
        drop(tx);

        let mut final_vote = Vote::Commit;
        let start_time = Instant::now();
        let num_ops = ops.len();
        let mut received_count = 0;

        while received_count < num_ops {
            let elapsed = start_time.elapsed();
            let remaining = if self.timeout > elapsed {
                self.timeout - elapsed
            } else {
                Duration::from_secs(0)
            };

            match rx.recv_timeout(remaining) {
                Ok((_res_id, vote)) => {
                    received_count += 1;
                    if vote == Vote::Abort {
                        final_vote = Vote::Abort;
                    }
                }
                Err(_) => {
                    final_vote = Vote::Abort;
                    break;
                }
            }
        }

        for handle in handles {
            let _ = handle.join();
        }

        let rms = self.resource_managers.lock().unwrap().clone();
        if final_vote == Vote::Commit {
            for op in ops.iter() {
                if let Some(rm) = rms.get(&op.resource_id) {
                    self.log_event(&format!("COMMIT {} {}", txn_id, op.resource_id));
                    rm.commit(txn_id);
                }
            }
            self.log_event(&format!("COMMIT_TXN {}", txn_id));
            TransactionOutcome::Commit
        } else {
            for op in ops.iter() {
                if let Some(rm) = rms.get(&op.resource_id) {
                    self.log_event(&format!("ABORT {} {}", txn_id, op.resource_id));
                    rm.abort(txn_id);
                }
            }
            self.log_event(&format!("ABORT_TXN {}", txn_id));
            TransactionOutcome::Abort
        }
    }

    pub fn recover(log_file: &str) -> Self {
        // On recovery, read and replay the log events.
        if let Ok(file) = File::open(log_file) {
            let reader = BufReader::new(file);
            for line in reader.lines() {
                if let Ok(event) = line {
                    println!("Recovered log event: {}", event);
                }
            }
        }
        TransactionManager::new(Duration::from_millis(100), log_file)
    }
}