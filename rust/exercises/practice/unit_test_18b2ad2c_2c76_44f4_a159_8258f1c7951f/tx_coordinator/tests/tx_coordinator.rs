use std::collections::HashSet;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;
use tx_coordinator::{TransactionCoordinator, TransactionState};

#[test]
fn test_basic_transaction_lifecycle() {
    let coordinator = TransactionCoordinator::new();
    
    // Begin a new transaction
    let tx_id = coordinator.begin_transaction();
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Active));
    
    // Enlist resources
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    assert!(coordinator.enlist_resource(tx_id, "database_2").is_ok());
    
    // Prepare transaction
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Prepared));
    
    // Commit transaction
    assert!(coordinator.commit_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Committed));
}

#[test]
fn test_abort_transaction() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    
    assert!(coordinator.abort_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Aborted));
}

#[test]
fn test_enlist_resource_errors() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    
    // Test duplicate resource enlistment
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_err());
    
    // Test enlistment with invalid transaction ID
    let invalid_tx_id = tx_id + 999;
    assert!(coordinator.enlist_resource(invalid_tx_id, "database_2").is_err());
}

#[test]
fn test_prepare_transaction_errors() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    
    // Prepare with no enlisted resources should still work
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    
    // Prepare an already prepared transaction
    assert!(coordinator.prepare_transaction(tx_id).is_err());
    
    // Prepare an invalid transaction
    let invalid_tx_id = tx_id + 999;
    assert!(coordinator.prepare_transaction(invalid_tx_id).is_err());
}

#[test]
fn test_commit_transaction_errors() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    
    // Cannot commit an unprepared transaction
    assert!(coordinator.commit_transaction(tx_id).is_err());
    
    // Prepare the transaction
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    
    // Now commit should work
    assert!(coordinator.commit_transaction(tx_id).is_ok());
    
    // Cannot commit an already committed transaction
    assert!(coordinator.commit_transaction(tx_id).is_err());
    
    // Cannot commit an invalid transaction
    let invalid_tx_id = tx_id + 999;
    assert!(coordinator.commit_transaction(invalid_tx_id).is_err());
}

#[test]
fn test_abort_after_prepare() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    
    // Can abort a prepared transaction
    assert!(coordinator.abort_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Aborted));
}

#[test]
fn test_abort_committed_transaction_fails() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert!(coordinator.commit_transaction(tx_id).is_ok());
    
    // Cannot abort a committed transaction
    assert!(coordinator.abort_transaction(tx_id).is_err());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Committed));
}

#[test]
fn test_multiple_transactions() {
    let coordinator = TransactionCoordinator::new();
    
    // Start two transactions
    let tx_id1 = coordinator.begin_transaction();
    let tx_id2 = coordinator.begin_transaction();
    
    // Enlist different resources
    assert!(coordinator.enlist_resource(tx_id1, "database_1").is_ok());
    assert!(coordinator.enlist_resource(tx_id2, "database_2").is_ok());
    
    // Prepare and commit first transaction
    assert!(coordinator.prepare_transaction(tx_id1).is_ok());
    assert!(coordinator.commit_transaction(tx_id1).is_ok());
    
    // Abort second transaction
    assert!(coordinator.abort_transaction(tx_id2).is_ok());
    
    assert_eq!(coordinator.get_transaction_state(tx_id1), Some(TransactionState::Committed));
    assert_eq!(coordinator.get_transaction_state(tx_id2), Some(TransactionState::Aborted));
}

#[test]
fn test_concurrent_transactions() {
    let coordinator = Arc::new(TransactionCoordinator::new());
    let num_threads = 10;
    let num_transactions_per_thread = 10;
    
    let barrier = Arc::new(Barrier::new(num_threads));
    let tx_ids: Arc<std::sync::Mutex<HashSet<u64>>> = Arc::new(std::sync::Mutex::new(HashSet::new()));
    
    // Spawn multiple threads to create and manage transactions
    let mut handles = Vec::new();
    for thread_id in 0..num_threads {
        let coordinator_clone = Arc::clone(&coordinator);
        let barrier_clone = Arc::clone(&barrier);
        let tx_ids_clone = Arc::clone(&tx_ids);
        
        let handle = thread::spawn(move || {
            barrier_clone.wait(); // Synchronize threads to start at the same time
            
            for i in 0..num_transactions_per_thread {
                let tx_id = coordinator_clone.begin_transaction();
                {
                    let mut tx_ids_set = tx_ids_clone.lock().unwrap();
                    tx_ids_set.insert(tx_id);
                }
                
                let rm_name = format!("database_{}_{}", thread_id, i);
                assert!(coordinator_clone.enlist_resource(tx_id, &rm_name).is_ok());
                
                // Add a small delay to increase chances of thread interleaving
                thread::sleep(Duration::from_millis(1));
                
                assert!(coordinator_clone.prepare_transaction(tx_id).is_ok());
                
                // Some transactions commit, others abort
                if i % 2 == 0 {
                    assert!(coordinator_clone.commit_transaction(tx_id).is_ok());
                    assert_eq!(coordinator_clone.get_transaction_state(tx_id), Some(TransactionState::Committed));
                } else {
                    assert!(coordinator_clone.abort_transaction(tx_id).is_ok());
                    assert_eq!(coordinator_clone.get_transaction_state(tx_id), Some(TransactionState::Aborted));
                }
            }
        });
        
        handles.push(handle);
    }
    
    // Join all threads
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Verify transaction IDs are unique
    let tx_ids_set = tx_ids.lock().unwrap();
    assert_eq!(tx_ids_set.len(), num_threads * num_transactions_per_thread);
}

#[test]
fn test_transaction_state_after_invalid_operations() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id, "database_1").is_ok());
    
    // Invalid operation: commit without prepare
    assert!(coordinator.commit_transaction(tx_id).is_err());
    
    // State should still be active
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Active));
    
    // Now prepare and check state
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Prepared));
    
    // Invalid operation: enlist after prepare
    assert!(coordinator.enlist_resource(tx_id, "database_2").is_err());
    
    // State should still be prepared
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Prepared));
}

#[test]
fn test_transaction_id_uniqueness() {
    let coordinator = TransactionCoordinator::new();
    let mut tx_ids = HashSet::new();
    
    for _ in 0..100 {
        let tx_id = coordinator.begin_transaction();
        assert!(!tx_ids.contains(&tx_id), "Transaction ID {} is not unique", tx_id);
        tx_ids.insert(tx_id);
    }
}

#[test]
fn test_nonexistent_transaction() {
    let coordinator = TransactionCoordinator::new();
    
    // Try operations on a non-existent transaction
    let invalid_tx_id = 999999;
    assert!(coordinator.enlist_resource(invalid_tx_id, "database_1").is_err());
    assert!(coordinator.prepare_transaction(invalid_tx_id).is_err());
    assert!(coordinator.commit_transaction(invalid_tx_id).is_err());
    assert!(coordinator.abort_transaction(invalid_tx_id).is_err());
    assert_eq!(coordinator.get_transaction_state(invalid_tx_id), None);
}

#[test]
fn test_commit_transaction_with_multiple_resources() {
    let coordinator = TransactionCoordinator::new();
    
    let tx_id = coordinator.begin_transaction();
    
    // Enlist multiple resources
    for i in 1..=5 {
        let rm_name = format!("database_{}", i);
        assert!(coordinator.enlist_resource(tx_id, &rm_name).is_ok());
    }
    
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert!(coordinator.commit_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Committed));
}

#[test]
fn test_concurrent_operations_on_same_transaction() {
    let coordinator = Arc::new(TransactionCoordinator::new());
    let tx_id = coordinator.begin_transaction();
    
    // Enlist a resource first
    assert!(coordinator.enlist_resource(tx_id, "shared_database").is_ok());
    
    // Create multiple threads that try to enlist different resources to the same transaction
    let mut handles = Vec::new();
    for i in 0..5 {
        let coordinator_clone = Arc::clone(&coordinator);
        let resource_name = format!("resource_{}", i);
        
        let handle = thread::spawn(move || {
            coordinator_clone.enlist_resource(tx_id, &resource_name)
        });
        
        handles.push(handle);
    }
    
    // Join threads and check results
    for handle in handles {
        let result = handle.join().unwrap();
        assert!(result.is_ok(), "Failed to enlist resource: {:?}", result.err());
    }
    
    // Continue with transaction
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert!(coordinator.commit_transaction(tx_id).is_ok());
}

#[test]
fn test_transaction_states_sequence() {
    let coordinator = TransactionCoordinator::new();
    
    // Start a transaction and check its state
    let tx_id = coordinator.begin_transaction();
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Active));
    
    // Enlist a resource
    assert!(coordinator.enlist_resource(tx_id, "database").is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Active));
    
    // Prepare transaction
    assert!(coordinator.prepare_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Prepared));
    
    // Commit transaction
    assert!(coordinator.commit_transaction(tx_id).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id), Some(TransactionState::Committed));
}

#[test]
fn test_abort_at_different_states() {
    let coordinator = TransactionCoordinator::new();
    
    // Abort from Active state
    let tx_id1 = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id1, "db1").is_ok());
    assert!(coordinator.abort_transaction(tx_id1).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id1), Some(TransactionState::Aborted));
    
    // Abort from Prepared state
    let tx_id2 = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id2, "db2").is_ok());
    assert!(coordinator.prepare_transaction(tx_id2).is_ok());
    assert!(coordinator.abort_transaction(tx_id2).is_ok());
    assert_eq!(coordinator.get_transaction_state(tx_id2), Some(TransactionState::Aborted));
    
    // Cannot abort from Committed state
    let tx_id3 = coordinator.begin_transaction();
    assert!(coordinator.enlist_resource(tx_id3, "db3").is_ok());
    assert!(coordinator.prepare_transaction(tx_id3).is_ok());
    assert!(coordinator.commit_transaction(tx_id3).is_ok());
    assert!(coordinator.abort_transaction(tx_id3).is_err());
    assert_eq!(coordinator.get_transaction_state(tx_id3), Some(TransactionState::Committed));
}