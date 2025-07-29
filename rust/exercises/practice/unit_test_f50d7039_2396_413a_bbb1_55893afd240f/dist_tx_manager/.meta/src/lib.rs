use std::collections::HashMap;
use std::sync::{Mutex, atomic::{AtomicU64, Ordering}};

pub trait KeyValueStore {
    fn get(&self, key: &str) -> Option<String>;
    fn put(&mut self, key: &str, value: String);
}

enum TransactionStatus {
    Active,
    Committed,
    Aborted,
}

struct TransactionData {
    tid: u64,
    // Mapping from node id to a vector of (key, value) staged for that node.
    changes: HashMap<usize, Vec<(String, String)>>,
    status: TransactionStatus,
}

pub struct TransactionManager {
    // Each node is wrapped in a Mutex to allow safe concurrent access.
    nodes: Vec<Mutex<Box<dyn KeyValueStore + Send>>>,
    // Transactions are stored in a Mutex protected HashMap.
    transactions: Mutex<HashMap<u64, TransactionData>>,
    // Monotonically increasing transaction id counter.
    next_tid: AtomicU64,
}

impl TransactionManager {
    pub fn new(stores: Vec<Box<dyn KeyValueStore + Send>>) -> Self {
        let nodes = stores.into_iter().map(|store| Mutex::new(store)).collect();
        TransactionManager {
            nodes,
            transactions: Mutex::new(HashMap::new()),
            next_tid: AtomicU64::new(1),
        }
    }

    pub fn begin_transaction(&self) -> u64 {
        let tid = self.next_tid.fetch_add(1, Ordering::SeqCst);
        let tx_data = TransactionData {
            tid,
            changes: HashMap::new(),
            status: TransactionStatus::Active,
        };
        let mut tx_map = self.transactions.lock().unwrap();
        tx_map.insert(tid, tx_data);
        tid
    }

    pub fn put(&self, tid: u64, key: String, value: String) -> Result<(), String> {
        let node_id = self.hash_key(&key);
        let mut tx_map = self.transactions.lock().unwrap();
        if let Some(tx) = tx_map.get_mut(&tid) {
            match tx.status {
                TransactionStatus::Active => {
                    tx.changes.entry(node_id).or_insert_with(Vec::new).push((key, value));
                    Ok(())
                }
                _ => Err("Transaction is not active".to_string()),
            }
        } else {
            Err("Invalid transaction id".to_string())
        }
    }

    pub fn commit_transaction(&self, tid: u64) -> Result<(), String> {
        let mut tx_map = self.transactions.lock().unwrap();
        let tx = tx_map.get_mut(&tid).ok_or_else(|| "Invalid transaction id".to_string())?;
        match tx.status {
            TransactionStatus::Active => {
                // Phase 1: Prepare phase - simulate logging changes.
                for (&node_id, _changes) in tx.changes.iter() {
                    if node_id >= self.nodes.len() {
                        tx.status = TransactionStatus::Aborted;
                        return Err("Invalid node id encountered during prepare phase".to_string());
                    }
                    // Simulate durability: In a real system, the node would log the changes.
                    // Here we assume that logging always succeeds.
                }
                // Phase 2: Commit phase - apply the changes.
                for (&node_id, changes) in tx.changes.iter() {
                    let mut node = self.nodes[node_id].lock().unwrap();
                    for (key, value) in changes.iter() {
                        node.put(key, value.clone());
                    }
                }
                tx.status = TransactionStatus::Committed;
                Ok(())
            }
            _ => Err("Transaction is not active".to_string()),
        }
    }

    pub fn abort_transaction(&self, tid: u64) -> Result<(), String> {
        let mut tx_map = self.transactions.lock().unwrap();
        let tx = tx_map.get_mut(&tid).ok_or_else(|| "Invalid transaction id".to_string())?;
        match tx.status {
            TransactionStatus::Active => {
                tx.status = TransactionStatus::Aborted;
                tx.changes.clear();
                Ok(())
            }
            _ => Err("Transaction is not active".to_string()),
        }
    }

    pub fn get(&self, key: String) -> Option<String> {
        let node_id = self.hash_key(&key);
        let node = self.nodes[node_id].lock().unwrap();
        node.get(&key)
    }

    fn hash_key(&self, key: &str) -> usize {
        // Simple hash function: multiply each byte by 31 and add them.
        let mut hash: usize = 0;
        for b in key.bytes() {
            hash = hash.wrapping_mul(31).wrapping_add(b as usize);
        }
        hash % self.nodes.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Arc, Mutex};
    use std::thread;

    // Simple in-memory dummy key-value store which implements KeyValueStore.
    pub struct DummyStore {
        data: HashMap<String, String>,
    }

    impl DummyStore {
        pub fn new() -> Self {
            DummyStore {
                data: HashMap::new(),
            }
        }
    }

    impl KeyValueStore for DummyStore {
        fn get(&self, key: &str) -> Option<String> {
            self.data.get(key).cloned()
        }

        fn put(&mut self, key: &str, value: String) {
            self.data.insert(key.to_string(), value);
        }
    }

    fn create_transaction_manager(num_nodes: usize) -> TransactionManager {
        let mut stores: Vec<Box<dyn KeyValueStore + Send>> = Vec::with_capacity(num_nodes);
        for _ in 0..num_nodes {
            stores.push(Box::new(DummyStore::new()));
        }
        TransactionManager::new(stores)
    }

    #[test]
    fn test_single_transaction_commit() {
        let txn_manager = create_transaction_manager(3);
        let tid = txn_manager.begin_transaction();

        txn_manager.put(tid, "apple".to_string(), "red".to_string()).unwrap();
        txn_manager.put(tid, "banana".to_string(), "yellow".to_string()).unwrap();
        txn_manager.put(tid, "grape".to_string(), "purple".to_string()).unwrap();

        txn_manager.commit_transaction(tid).unwrap();

        assert_eq!(txn_manager.get("apple".to_string()), Some("red".to_string()));
        assert_eq!(txn_manager.get("banana".to_string()), Some("yellow".to_string()));
        assert_eq!(txn_manager.get("grape".to_string()), Some("purple".to_string()));
    }

    #[test]
    fn test_transaction_abort() {
        let txn_manager = create_transaction_manager(2);
        let tid = txn_manager.begin_transaction();

        txn_manager.put(tid, "key1".to_string(), "value1".to_string()).unwrap();
        txn_manager.put(tid, "key2".to_string(), "value2".to_string()).unwrap();

        txn_manager.abort_transaction(tid).unwrap();

        assert_eq!(txn_manager.get("key1".to_string()), None);
        assert_eq!(txn_manager.get("key2".to_string()), None);
    }

    #[test]
    fn test_invalid_transaction() {
        let txn_manager = create_transaction_manager(2);

        let invalid_tid = 9999;
        let result = txn_manager.put(invalid_tid, "key".to_string(), "value".to_string());
        assert!(result.is_err());

        let commit_result = txn_manager.commit_transaction(invalid_tid);
        assert!(commit_result.is_err());

        let abort_result = txn_manager.abort_transaction(invalid_tid);
        assert!(abort_result.is_err());
    }

    #[test]
    fn test_multiple_transactions() {
        let txn_manager = create_transaction_manager(4);

        let tid1 = txn_manager.begin_transaction();
        let tid2 = txn_manager.begin_transaction();

        txn_manager.put(tid1, "a".to_string(), "1".to_string()).unwrap();
        txn_manager.put(tid2, "b".to_string(), "2".to_string()).unwrap();

        txn_manager.commit_transaction(tid1).unwrap();
        txn_manager.abort_transaction(tid2).unwrap();

        assert_eq!(txn_manager.get("a".to_string()), Some("1".to_string()));
        assert_eq!(txn_manager.get("b".to_string()), None);
    }

    #[test]
    fn test_concurrent_transactions() {
        let txn_manager = Arc::new(create_transaction_manager(5));

        let mut handles = vec![];
        for i in 0..10 {
            let txn_manager_clone = Arc::clone(&txn_manager);
            let handle = thread::spawn(move || {
                let tid = txn_manager_clone.begin_transaction();
                let key = format!("key{}", i);
                let value = format!("value{}", i);
                txn_manager_clone.put(tid, key.clone(), value.clone()).unwrap();
                if i % 2 == 0 {
                    txn_manager_clone.commit_transaction(tid).unwrap();
                } else {
                    txn_manager_clone.abort_transaction(tid).unwrap();
                }
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }

        for i in 0..10 {
            let key = format!("key{}", i);
            if i % 2 == 0 {
                assert_eq!(txn_manager.get(key), Some(format!("value{}", i)));
            } else {
                assert_eq!(txn_manager.get(key), None);
            }
        }
    }

    #[test]
    fn test_get_does_not_affect_transaction() {
        let txn_manager = create_transaction_manager(3);

        let tid1 = txn_manager.begin_transaction();
        txn_manager.put(tid1, "init".to_string(), "start".to_string()).unwrap();
        txn_manager.commit_transaction(tid1).unwrap();

        let tid2 = txn_manager.begin_transaction();
        txn_manager.put(tid2, "init".to_string(), "update".to_string()).unwrap();

        assert_eq!(txn_manager.get("init".to_string()), Some("start".to_string()));

        txn_manager.abort_transaction(tid2).unwrap();
    }
}