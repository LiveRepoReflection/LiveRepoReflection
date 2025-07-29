use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

pub struct DistTxKv {
    node_count: usize,
    committed: HashMap<String, String>,
    transactions: HashMap<u64, Transaction>,
    next_tid: u64,
    nodes: Vec<bool>,
}

struct Transaction {
    id: u64,
    snapshot: HashMap<String, String>,
    local_writes: HashMap<String, String>,
}

impl DistTxKv {
    pub fn new(node_count: usize) -> Self {
        let nodes = vec![true; node_count];
        DistTxKv {
            node_count,
            committed: HashMap::new(),
            transactions: HashMap::new(),
            next_tid: 1,
            nodes,
        }
    }

    pub fn begin_transaction(&mut self) -> u64 {
        let tid = self.next_tid;
        self.next_tid += 1;
        let snapshot = self.committed.clone();
        let txn = Transaction {
            id: tid,
            snapshot,
            local_writes: HashMap::new(),
        };
        self.transactions.insert(tid, txn);
        tid
    }

    pub fn read(&self, tid: u64, key: String) -> Option<String> {
        if let Some(txn) = self.transactions.get(&tid) {
            if let Some(val) = txn.local_writes.get(&key) {
                return Some(val.clone());
            } else {
                return txn.snapshot.get(&key).cloned();
            }
        }
        None
    }

    pub fn write(&mut self, tid: u64, key: String, value: String) {
        if let Some(txn) = self.transactions.get_mut(&tid) {
            txn.local_writes.insert(key, value);
        }
    }

    pub fn commit_transaction(&mut self, tid: u64) -> bool {
        // Retrieve the transaction
        if let Some(txn) = self.transactions.get(&tid) {
            // Check node availability for each key written in this transaction.
            for key in txn.local_writes.keys() {
                let node = Self::node_for_key(key, self.node_count);
                if !self.nodes[node] {
                    return false;
                }
            }
            // Check for conflicts: each key written should have the same value in the snapshot as in the global store.
            for (key, _) in &txn.local_writes {
                let committed_val = self.committed.get(key);
                let snapshot_val = txn.snapshot.get(key);
                if committed_val != snapshot_val {
                    return false;
                }
            }
        } else {
            return false;
        }
        // Commit the transaction: apply local writes to the global store.
        if let Some(txn) = self.transactions.remove(&tid) {
            for (key, value) in txn.local_writes {
                self.committed.insert(key, value);
            }
            return true;
        }
        false
    }

    pub fn rollback_transaction(&mut self, tid: u64) {
        self.transactions.remove(&tid);
    }

    pub fn fail_node(&mut self, node_id: usize) {
        if node_id < self.nodes.len() {
            self.nodes[node_id] = false;
        }
    }

    pub fn recover_node(&mut self, node_id: usize) {
        if node_id < self.nodes.len() {
            self.nodes[node_id] = true;
        }
    }

    fn node_for_key(key: &String, node_count: usize) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        let hash = hasher.finish();
        (hash as usize) % node_count
    }
}