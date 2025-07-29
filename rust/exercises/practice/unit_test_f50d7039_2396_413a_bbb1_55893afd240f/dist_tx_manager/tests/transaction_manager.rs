use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;

use dist_tx_manager::{KeyValueStore, TransactionManager};

#[derive(Default)]
struct DummyStore {
    data: Arc<Mutex<HashMap<String, String>>>,
}

impl DummyStore {
    fn new() -> Self {
        DummyStore {
            data: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}

impl KeyValueStore for DummyStore {
    fn get(&self, key: &str) -> Option<String> {
        let map = self.data.lock().unwrap();
        map.get(key).cloned()
    }

    fn put(&mut self, key: &str, value: String) {
        let mut map = self.data.lock().unwrap();
        map.insert(key.to_string(), value);
    }
}

fn create_transaction_manager(num_nodes: usize) -> TransactionManager {
    // Create a vector of dummy stores to simulate the distributed key-value store.
    let mut stores: Vec<Box<dyn KeyValueStore + Send>> = Vec::with_capacity(num_nodes);
    for _ in 0..num_nodes {
        stores.push(Box::new(DummyStore::new()));
    }
    TransactionManager::new(stores)
}

#[test]
fn test_single_transaction_commit() {
    let mut txn_manager = create_transaction_manager(3);
    let tid = txn_manager.begin_transaction();

    // Stage multiple PUT operations across different keys.
    txn_manager.put(tid, "apple".to_string(), "red".to_string()).unwrap();
    txn_manager.put(tid, "banana".to_string(), "yellow".to_string()).unwrap();
    txn_manager.put(tid, "grape".to_string(), "purple".to_string()).unwrap();

    // Commit the transaction. All nodes should apply the changes.
    txn_manager.commit_transaction(tid).unwrap();

    // Verify that the changes are visible via direct GET calls.
    assert_eq!(txn_manager.get("apple".to_string()), Some("red".to_string()));
    assert_eq!(txn_manager.get("banana".to_string()), Some("yellow".to_string()));
    assert_eq!(txn_manager.get("grape".to_string()), Some("purple".to_string()));
}

#[test]
fn test_transaction_abort() {
    let mut txn_manager = create_transaction_manager(2);
    let tid = txn_manager.begin_transaction();

    txn_manager.put(tid, "key1".to_string(), "value1".to_string()).unwrap();
    txn_manager.put(tid, "key2".to_string(), "value2".to_string()).unwrap();

    // Abort the transaction. Changes should not be applied.
    txn_manager.abort_transaction(tid).unwrap();

    // Verify that no changes are visible.
    assert_eq!(txn_manager.get("key1".to_string()), None);
    assert_eq!(txn_manager.get("key2".to_string()), None);
}

#[test]
fn test_invalid_transaction() {
    let mut txn_manager = create_transaction_manager(2);

    // Attempt to use a non-existent transaction id.
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
    let mut txn_manager = create_transaction_manager(4);

    let tid1 = txn_manager.begin_transaction();
    let tid2 = txn_manager.begin_transaction();

    txn_manager.put(tid1, "a".to_string(), "1".to_string()).unwrap();
    txn_manager.put(tid2, "b".to_string(), "2".to_string()).unwrap();

    // Commit first transaction and abort the second one.
    txn_manager.commit_transaction(tid1).unwrap();
    txn_manager.abort_transaction(tid2).unwrap();

    assert_eq!(txn_manager.get("a".to_string()), Some("1".to_string()));
    assert_eq!(txn_manager.get("b".to_string()), None);
}

#[test]
fn test_concurrent_transactions() {
    let txn_manager = Arc::new(Mutex::new(create_transaction_manager(5)));

    // Spawn multiple threads to perform transactions concurrently.
    let mut handles = vec![];
    for i in 0..10 {
        let txn_manager_clone = Arc::clone(&txn_manager);
        let handle = thread::spawn(move || {
            let mut manager = txn_manager_clone.lock().unwrap();
            let tid = manager.begin_transaction();
            let key = format!("key{}", i);
            let value = format!("value{}", i);
            manager.put(tid, key.clone(), value.clone()).unwrap();
            // Even numbered transactions commit; odd numbered transactions abort.
            if i % 2 == 0 {
                manager.commit_transaction(tid).unwrap();
            } else {
                manager.abort_transaction(tid).unwrap();
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let manager = txn_manager.lock().unwrap();
    // Verify committed changes for even indices and absence for odd indices.
    for i in 0..10 {
        let key = format!("key{}", i);
        if i % 2 == 0 {
            assert_eq!(manager.get(key), Some(format!("value{}", i)));
        } else {
            assert_eq!(manager.get(key), None);
        }
    }
}

#[test]
fn test_get_does_not_affect_transaction() {
    let mut txn_manager = create_transaction_manager(3);

    // First, commit an initial value using a transaction.
    let tid1 = txn_manager.begin_transaction();
    txn_manager.put(tid1, "init".to_string(), "start".to_string()).unwrap();
    txn_manager.commit_transaction(tid1).unwrap();

    // Begin a new transaction and stage an update without committing.
    let tid2 = txn_manager.begin_transaction();
    txn_manager.put(tid2, "init".to_string(), "update".to_string()).unwrap();

    // The GET operation should return the committed value and ignore the uncommitted change.
    assert_eq!(txn_manager.get("init".to_string()), Some("start".to_string()));

    // Abort the staged transaction.
    txn_manager.abort_transaction(tid2).unwrap();
}