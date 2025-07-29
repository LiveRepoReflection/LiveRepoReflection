use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicBool, Ordering};

/// Enum representing an operation in a transaction.
#[derive(Debug, Clone)]
pub enum Operation {
    Read {
        node_id: usize,
        key: String,
    },
    Write {
        node_id: usize,
        key: String,
        value: String,
    },
    Delete {
        node_id: usize,
        key: String,
    },
}

/// Struct representing a transaction.
#[derive(Debug, Clone)]
pub struct Transaction {
    pub id: u64,
    pub operations: Vec<Operation>,
}

/// Enum representing the result of a transaction.
#[derive(Debug, PartialEq, Eq)]
pub enum TransactionResult {
    Committed,
    Aborted,
}

/// Worker node that simulates data storage and two-phase commit.
pub struct Worker {
    pub id: usize,
    data: Mutex<HashMap<String, String>>,
    /// Staging area for transactions.
    staging: Mutex<HashMap<u64, HashMap<String, Option<String>>>>,
    /// Available indicates if the worker is up.
    available: AtomicBool,
}

impl Worker {
    pub fn new(id: usize) -> Worker {
        Worker {
            id,
            data: Mutex::new(HashMap::new()),
            staging: Mutex::new(HashMap::new()),
            available: AtomicBool::new(true),
        }
    }

    /// Simulate the prepare phase for a transaction.
    /// It records the intended changes in the staging area.
    /// For Read operations, it does nothing (but checks availability).
    /// Returns true if preparation is successful, false otherwise.
    pub fn prepare(&self, tx_id: u64, ops: &[Operation]) -> bool {
        if !self.available.load(Ordering::SeqCst) {
            return false;
        }
        let mut staging_map = self.staging.lock().unwrap();
        let mut changes: HashMap<String, Option<String>> = HashMap::new();
        for op in ops {
            match op {
                Operation::Write { key, value, .. } => {
                    changes.insert(key.clone(), Some(value.clone()));
                }
                Operation::Delete { key, .. } => {
                    changes.insert(key.clone(), None);
                }
                Operation::Read { key, .. } => {
                    // For read, we simulate the operation by checking if the key exists.
                    // This does not affect the staging area.
                    let data = self.data.lock().unwrap();
                    let _ = data.get(key);
                }
            }
        }
        // Record the staging changes for this transaction.
        staging_map.insert(tx_id, changes);
        true
    }

    /// Commit the transaction by applying the staged changes to the main data store.
    pub fn commit(&self, tx_id: u64) {
        let mut staging_map = self.staging.lock().unwrap();
        if let Some(changes) = staging_map.remove(&tx_id) {
            let mut data_map = self.data.lock().unwrap();
            for (key, opt_value) in changes {
                match opt_value {
                    Some(val) => {
                        data_map.insert(key, val);
                    }
                    None => {
                        data_map.remove(&key);
                    }
                }
            }
        }
    }

    /// Abort the transaction and discard any staged changes.
    pub fn abort(&self, tx_id: u64) {
        let mut staging_map = self.staging.lock().unwrap();
        staging_map.remove(&tx_id);
    }

    /// Simulate a worker node failure.
    pub fn fail(&self) {
        self.available.store(false, Ordering::SeqCst);
    }

    /// Get the current data store (clone for read-only purposes).
    pub fn get_data(&self) -> HashMap<String, String> {
        let data = self.data.lock().unwrap();
        data.clone()
    }
}

/// Coordinator that manages transactions across multiple worker nodes.
pub struct Coordinator {
    workers: Vec<Arc<Worker>>,
    logs: Mutex<Vec<String>>,
}

impl Coordinator {
    /// Create a new coordinator with a specified number of worker nodes.
    pub fn new(num_workers: usize) -> Coordinator {
        let mut workers = Vec::with_capacity(num_workers);
        for id in 0..num_workers {
            workers.push(Arc::new(Worker::new(id)));
        }
        Coordinator {
            workers,
            logs: Mutex::new(Vec::new()),
        }
    }

    /// Execute a transaction using two-phase commit protocol.
    pub fn execute_transaction(&self, tx: Transaction) -> TransactionResult {
        self.log(&format!("Transaction {} started", tx.id));
        // Group operations by worker id.
        let mut ops_by_worker: HashMap<usize, Vec<Operation>> = HashMap::new();
        for op in tx.operations.iter() {
            let node_id = match op {
                Operation::Read { node_id, .. } => *node_id,
                Operation::Write { node_id, .. } => *node_id,
                Operation::Delete { node_id, .. } => *node_id,
            };
            ops_by_worker.entry(node_id).or_insert_with(Vec::new).push(op.clone());
        }
        let mut prepared_workers = Vec::new();
        // Phase 1: Prepare.
        for (node_id, ops) in ops_by_worker.iter() {
            if let Some(worker) = self.workers.get(*node_id) {
                self.log(&format!("Sending prepare to worker {} for transaction {}", node_id, tx.id));
                let success = worker.prepare(tx.id, ops);
                if success {
                    self.log(&format!("Worker {} prepared transaction {}", node_id, tx.id));
                    prepared_workers.push(worker.clone());
                } else {
                    self.log(&format!("Worker {} failed to prepare transaction {}", node_id, tx.id));
                    // Abort all previously prepared workers.
                    for w in prepared_workers.iter() {
                        w.abort(tx.id);
                        self.log(&format!("Sent abort to worker {} for transaction {}", w.id, tx.id));
                    }
                    self.log(&format!("Transaction {} aborted", tx.id));
                    return TransactionResult::Aborted;
                }
            } else {
                // Worker not found, abort.
                self.log(&format!("Worker {} not found for transaction {}", node_id, tx.id));
                for w in prepared_workers.iter() {
                    w.abort(tx.id);
                    self.log(&format!("Sent abort to worker {} for transaction {}", w.id, tx.id));
                }
                self.log(&format!("Transaction {} aborted", tx.id));
                return TransactionResult::Aborted;
            }
        }
        // Phase 2: Commit.
        for worker in prepared_workers.iter() {
            worker.commit(tx.id);
            self.log(&format!("Worker {} committed transaction {}", worker.id, tx.id));
        }
        self.log(&format!("Transaction {} committed", tx.id));
        TransactionResult::Committed
    }

    /// Get a clone of the data stored in a specified worker.
    pub fn get_worker_data(&self, worker_id: usize) -> Option<HashMap<String, String>> {
        self.workers.get(worker_id).map(|worker| worker.get_data())
    }

    /// Return a clone of the logs.
    pub fn get_logs(&self) -> Vec<String> {
        let logs = self.logs.lock().unwrap();
        logs.clone()
    }

    /// Simulate a worker failure by setting it to unavailable.
    pub fn simulate_worker_failure(&self, worker_id: usize) {
        if let Some(worker) = self.workers.get(worker_id) {
            worker.fail();
            self.log(&format!("Worker {} has been set to failure", worker_id));
        }
    }

    fn log(&self, message: &str) {
        let mut logs = self.logs.lock().unwrap();
        logs.push(message.to_string());
    }
}