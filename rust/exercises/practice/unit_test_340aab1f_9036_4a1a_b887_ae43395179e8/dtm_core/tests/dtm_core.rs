use std::sync::{Arc, Mutex};
use std::thread;
use dtm_core::{DistributedTransactionManager, TransactionStatus};

#[test]
fn test_begin_and_get_status() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Check that a new transaction is in Pending state.
    assert_eq!(dtm.get_transaction_status(tx).unwrap(), TransactionStatus::Pending);
}

#[test]
fn test_register_resource_and_prepare() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Register two different resources for different services.
    assert!(dtm.register_resource(tx, "res1".to_string(), "InventoryService".to_string()).is_ok());
    assert!(dtm.register_resource(tx, "res2".to_string(), "PaymentService".to_string()).is_ok());
    // Prepare the transaction; after preparation, status should be Prepared.
    assert!(dtm.prepare(tx).is_ok());
    assert_eq!(dtm.get_transaction_status(tx).unwrap(), TransactionStatus::Prepared);
}

#[test]
fn test_commit_without_prepare() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Attempting commit without calling prepare should fail.
    assert!(dtm.commit(tx).is_err());
}

#[test]
fn test_commit_after_prepare() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Register a resource and then prepare the transaction.
    assert!(dtm.register_resource(tx, "res1".to_string(), "InventoryService".to_string()).is_ok());
    assert!(dtm.prepare(tx).is_ok());
    // Commit should succeed after being prepared.
    assert!(dtm.commit(tx).is_ok());
    assert_eq!(dtm.get_transaction_status(tx).unwrap(), TransactionStatus::Committed);
}

#[test]
fn test_rollback_pending() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Rollback a transaction in Pending state.
    assert!(dtm.rollback(tx).is_ok());
    assert_eq!(dtm.get_transaction_status(tx).unwrap(), TransactionStatus::RolledBack);
}

#[test]
fn test_rollback_prepared() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Register a resource and prepare the transaction.
    assert!(dtm.register_resource(tx, "res1".to_string(), "ShippingService".to_string()).is_ok());
    assert!(dtm.prepare(tx).is_ok());
    // Rollback the prepared transaction.
    assert!(dtm.rollback(tx).is_ok());
    assert_eq!(dtm.get_transaction_status(tx).unwrap(), TransactionStatus::RolledBack);
}

#[test]
fn test_double_register_resource() {
    let mut dtm = DistributedTransactionManager::new();
    let tx = dtm.begin_transaction();
    // Register the same resource once.
    assert!(dtm.register_resource(tx, "res1".to_string(), "InventoryService".to_string()).is_ok());
    // Attempt to register the same resource a second time should return an error.
    assert!(dtm.register_resource(tx, "res1".to_string(), "InventoryService".to_string()).is_err());
}

#[test]
fn test_non_existent_transaction() {
    let mut dtm = DistributedTransactionManager::new();
    let fake_tx = 9999;
    // Operations on a non-existent transaction should return an error.
    assert!(dtm.get_transaction_status(fake_tx).is_err());
    assert!(dtm.commit(fake_tx).is_err());
    assert!(dtm.rollback(fake_tx).is_err());
    assert!(dtm.register_resource(fake_tx, "resX".to_string(), "PaymentService".to_string()).is_err());
}

#[test]
fn test_concurrent_transactions() {
    let dtm = Arc::new(Mutex::new(DistributedTransactionManager::new()));
    let mut handles = Vec::new();
    for _ in 0..10 {
        let dtm_clone = Arc::clone(&dtm);
        let handle = thread::spawn(move || {
            let tx;
            {
                let mut manager = dtm_clone.lock().unwrap();
                tx = manager.begin_transaction();
                assert!(manager.register_resource(tx, "res".to_string(), "ConcurrentService".to_string()).is_ok());
                assert!(manager.prepare(tx).is_ok());
            }
            {
                let mut manager = dtm_clone.lock().unwrap();
                assert!(manager.commit(tx).is_ok());
                assert_eq!(manager.get_transaction_status(tx).unwrap(), TransactionStatus::Committed);
            }
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
}