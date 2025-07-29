use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::thread;
use std::sync::mpsc::{self, RecvTimeoutError};

/// Operation type indicates whether the transaction should increment or decrement the node state.
#[derive(Clone, Copy)]
pub enum Operation {
    Increment,
    Decrement,
}

/// TransactionOutcome indicates whether the transaction was successfully committed or aborted.
#[derive(Debug, PartialEq, Eq)]
pub enum TransactionOutcome {
    Committed,
    Aborted,
}

/// Node represents a participant in the distributed transaction.
pub struct Node {
    id: usize,
    state: Mutex<i64>,
    pending_delta: Mutex<Option<i64>>,
    backup_state: Mutex<Option<i64>>,
    prepare_fail_prob: f64,
    commit_fail_prob: f64,
    prepare_delay: Duration,
}

impl Node {
    /// Create a new node with given id, initial state, prepare failure probability, and commit failure probability.
    pub fn new(id: usize, initial_state: i64, prepare_fail_prob: f64, commit_fail_prob: f64) -> Self {
        Self {
            id,
            state: Mutex::new(initial_state),
            pending_delta: Mutex::new(None),
            backup_state: Mutex::new(None),
            prepare_fail_prob,
            commit_fail_prob,
            prepare_delay: Duration::from_millis(0),
        }
    }

    /// Create a new node with a specified delay in the prepare phase.
    pub fn new_with_delay(id: usize, initial_state: i64, prepare_fail_prob: f64, commit_fail_prob: f64, delay: Duration) -> Self {
        Self {
            id,
            state: Mutex::new(initial_state),
            pending_delta: Mutex::new(None),
            backup_state: Mutex::new(None),
            prepare_fail_prob,
            commit_fail_prob,
            prepare_delay: delay,
        }
    }
    
    /// Simulate the prepare phase.
    /// Returns true if node is ready to commit, false otherwise.
    pub fn prepare(&self, op: Operation, delta: i64) -> bool {
        // Simulate delay in prepare phase.
        thread::sleep(self.prepare_delay);
        
        let mut state_lock = self.state.lock().unwrap();
        // Determine adjusted delta based on operation.
        let adjusted_delta = match op {
            Operation::Increment => delta,
            Operation::Decrement => {
                if *state_lock < delta {
                    return false;
                }
                -delta
            }
        };

        // Simulate random failure in prepare phase.
        if rand_f64() < self.prepare_fail_prob {
            return false;
        }
        
        // Set backup state and record the pending delta.
        {
            let mut backup_lock = self.backup_state.lock().unwrap();
            *backup_lock = Some(*state_lock);
        }
        {
            let mut pending_lock = self.pending_delta.lock().unwrap();
            *pending_lock = Some(adjusted_delta);
        }
        
        true
    }
    
    /// Simulate the commit phase.
    /// Returns true if commit succeeded, false otherwise.
    pub fn commit(&self, _op: Operation, _delta: i64) -> bool {
        // Simulate random failure in commit phase.
        if rand_f64() < self.commit_fail_prob {
            return false;
        }
        let mut state_lock = self.state.lock().unwrap();
        let mut pending_lock = self.pending_delta.lock().unwrap();
        let mut backup_lock = self.backup_state.lock().unwrap();
        
        if let Some(pending) = *pending_lock {
            if let Some(backup) = *backup_lock {
                *state_lock = backup + pending;
            }
        }
        
        *pending_lock = None;
        *backup_lock = None;
        true
    }
    
    /// Simulate the abort phase which rolls back the prepared changes.
    pub fn abort(&self, _op: Operation, _delta: i64) {
        let mut pending_lock = self.pending_delta.lock().unwrap();
        let mut backup_lock = self.backup_state.lock().unwrap();
        *pending_lock = None;
        *backup_lock = None;
    }
    
    /// Get the current state value of the node.
    pub fn get_state(&self) -> i64 {
        *self.state.lock().unwrap()
    }
}

/// Coordinator orchestrates the two-phase commit transaction.
pub struct Coordinator {
    nodes: Mutex<HashMap<usize, Arc<Node>>>,
    prepare_timeout: Duration,
}

impl Coordinator {
    /// Create a new coordinator with a specified timeout for the prepare phase.
    pub fn new(prepare_timeout: Duration) -> Self {
        Self {
            nodes: Mutex::new(HashMap::new()),
            prepare_timeout,
        }
    }
    
    /// Adds a node to the coordinator.
    pub fn add_node(&mut self, node: Node) {
        let mut nodes_lock = self.nodes.lock().unwrap();
        nodes_lock.insert(node.id, Arc::new(node));
    }
    
    /// Retrieve the state of a node by id.
    pub fn get_node_state(&self, node_id: usize) -> i64 {
        let nodes_lock = self.nodes.lock().unwrap();
        if let Some(node) = nodes_lock.get(&node_id) {
            node.get_state()
        } else {
            0
        }
    }
    
    /// Execute a transaction on the specified nodes using the 2PC protocol.
    pub fn execute_transaction(&self, op: Operation, delta: i64, node_ids: Vec<usize>) -> TransactionOutcome {
        let nodes_lock = self.nodes.lock().unwrap();
        let mut nodes_to_participate = Vec::new();
        for id in node_ids.iter() {
            if let Some(node) = nodes_lock.get(id) {
                nodes_to_participate.push(Arc::clone(node));
            }
        }
        drop(nodes_lock);
        
        // Phase 1: Prepare
        let (tx, rx) = mpsc::channel();
        for node in nodes_to_participate.iter() {
            let tx_clone = tx.clone();
            let node_clone = Arc::clone(node);
            let op_copy = op;
            thread::spawn(move || {
                let res = node_clone.prepare(op_copy, delta);
                tx_clone.send((node_clone.id, res)).unwrap();
            });
        }
        drop(tx);
        
        let mut prepare_results = std::collections::HashMap::new();
        for _ in 0..nodes_to_participate.len() {
            match rx.recv_timeout(self.prepare_timeout) {
                Ok((node_id, res)) => {
                    prepare_results.insert(node_id, res);
                },
                Err(RecvTimeoutError::Timeout) => {
                    prepare_results.insert(0, false);
                },
                Err(_) => {
                    prepare_results.insert(0, false);
                }
            }
        }
        
        if prepare_results.values().any(|&v| v == false) {
            // Abort the transaction if any prepare fails.
            let (tx_abort, rx_abort) = mpsc::channel();
            for node in nodes_to_participate.iter() {
                let tx_clone = tx_abort.clone();
                let node_clone = Arc::clone(node);
                let op_copy = op;
                thread::spawn(move || {
                    node_clone.abort(op_copy, delta);
                    tx_clone.send(node_clone.id).unwrap();
                });
            }
            drop(tx_abort);
            for _ in 0..nodes_to_participate.len() {
                let _ = rx_abort.recv();
            }
            return TransactionOutcome::Aborted;
        }
        
        // Phase 2: Commit
        let (tx_commit, rx_commit) = mpsc::channel();
        for node in nodes_to_participate.iter() {
            let tx_clone = tx_commit.clone();
            let node_clone = Arc::clone(node);
            let op_copy = op;
            thread::spawn(move || {
                let res = node_clone.commit(op_copy, delta);
                tx_clone.send((node_clone.id, res)).unwrap();
            });
        }
        drop(tx_commit);
        
        let mut commit_results = std::collections::HashMap::new();
        for _ in 0..nodes_to_participate.len() {
            if let Ok((node_id, res)) = rx_commit.recv() {
                commit_results.insert(node_id, res);
            }
        }
        
        if commit_results.values().any(|&v| v == false) {
            // Rollback if any commit fails.
            let (tx_abort, rx_abort) = mpsc::channel();
            for node in nodes_to_participate.iter() {
                let tx_clone = tx_abort.clone();
                let node_clone = Arc::clone(node);
                let op_copy = op;
                thread::spawn(move || {
                    node_clone.abort(op_copy, delta);
                    tx_clone.send(node_clone.id).unwrap();
                });
            }
            drop(tx_abort);
            for _ in 0..nodes_to_participate.len() {
                let _ = rx_abort.recv();
            }
            return TransactionOutcome::Aborted;
        }
        TransactionOutcome::Committed
    }
}

/// A simple pseudo-random number generator function returning a value between 0.0 and 1.0.
fn rand_f64() -> f64 {
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    let nanos = now.subsec_nanos() as u64;
    ((nanos % 1000) as f64) / 1000.0
}