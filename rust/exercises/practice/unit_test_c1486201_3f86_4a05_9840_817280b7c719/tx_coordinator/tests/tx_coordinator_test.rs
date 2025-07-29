use tx_coordinator::*;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;

#[test]
fn test_new_coordinator() {
    let coordinator = Coordinator::new();
    assert!(coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).is_ok());
}

#[test]
fn test_begin_transaction() {
    let coordinator = Coordinator::new();
    
    // First time should succeed
    assert!(coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).is_ok());
    
    // Second time with same ID should fail
    assert_eq!(
        coordinator.begin_transaction(1, vec!["node3".to_string()]),
        Err("Transaction already exists".to_string())
    );
    
    // Different ID should succeed
    assert!(coordinator.begin_transaction(2, vec!["node3".to_string()]).is_ok());
    
    // Empty nodes list should succeed
    assert!(coordinator.begin_transaction(3, vec![]).is_ok());
}

#[test]
fn test_prepare() {
    let coordinator = Coordinator::new();
    coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).unwrap();
    
    // Valid prepare
    assert!(coordinator.prepare(1, "node1").is_ok());
    
    // Prepare the same node twice
    assert_eq!(
        coordinator.prepare(1, "node1"),
        Err("Node already prepared".to_string())
    );
    
    // Prepare non-existent transaction
    assert_eq!(
        coordinator.prepare(999, "node1"),
        Err("Transaction not found".to_string())
    );
    
    // Prepare node not in transaction
    assert_eq!(
        coordinator.prepare(1, "node3"),
        Err("Node not in transaction".to_string())
    );
}

#[test]
fn test_commit_transaction() {
    let coordinator = Coordinator::new();
    coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).unwrap();
    
    // Try to commit before all nodes prepared
    assert_eq!(
        coordinator.commit_transaction(1),
        Err("Not all nodes prepared".to_string())
    );
    
    // Prepare all nodes
    coordinator.prepare(1, "node1").unwrap();
    coordinator.prepare(1, "node2").unwrap();
    
    // Now commit should succeed
    assert!(coordinator.commit_transaction(1).is_ok());
    
    // Commit non-existent transaction
    assert_eq!(
        coordinator.commit_transaction(999),
        Err("Transaction not found".to_string())
    );
    
    // Commit the same transaction again
    assert!(coordinator.commit_transaction(1).is_ok());  // Idempotent
}

#[test]
fn test_rollback_transaction() {
    let coordinator = Coordinator::new();
    coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).unwrap();
    
    // Prepare some nodes
    coordinator.prepare(1, "node1").unwrap();
    
    // Rollback should succeed even if not all nodes prepared
    assert!(coordinator.rollback_transaction(1).is_ok());
    
    // Rollback non-existent transaction
    assert_eq!(
        coordinator.rollback_transaction(999),
        Err("Transaction not found".to_string())
    );
    
    // Rollback the same transaction again
    assert!(coordinator.rollback_transaction(1).is_ok());  // Idempotent
}

#[test]
fn test_get_transaction_status() {
    let coordinator = Coordinator::new();
    
    // Non-existent transaction
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::NotFound
    );
    
    coordinator.begin_transaction(1, vec!["node1".to_string(), "node2".to_string()]).unwrap();
    
    // Pending transaction
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Pending
    );
    
    // Partially prepared
    coordinator.prepare(1, "node1").unwrap();
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Pending
    );
    
    // Fully prepared
    coordinator.prepare(1, "node2").unwrap();
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Prepared
    );
    
    // Committed
    coordinator.commit_transaction(1).unwrap();
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Committed
    );
    
    // Test rollback status
    coordinator.begin_transaction(2, vec!["node1".to_string()]).unwrap();
    coordinator.rollback_transaction(2).unwrap();
    assert_eq!(
        coordinator.get_transaction_status(2).unwrap(),
        TransactionStatus::RolledBack
    );
}

#[test]
fn test_empty_transaction() {
    let coordinator = Coordinator::new();
    coordinator.begin_transaction(1, vec![]).unwrap();
    
    // Empty transaction should be considered fully prepared
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Prepared
    );
    
    // Should be able to commit an empty transaction
    assert!(coordinator.commit_transaction(1).is_ok());
}

#[test]
fn test_concurrency() {
    let coordinator = Arc::new(Coordinator::new());
    let num_threads = 10;
    let barrier = Arc::new(Barrier::new(num_threads));
    
    // Setup a transaction with multiple nodes
    coordinator.begin_transaction(1, vec![
        "node1".to_string(), "node2".to_string(), "node3".to_string(),
        "node4".to_string(), "node5".to_string()
    ]).unwrap();
    
    let mut handles = vec![];
    
    // Create threads that will try to prepare nodes
    for i in 0..num_threads {
        let coordinator_clone = Arc::clone(&coordinator);
        let barrier_clone = Arc::clone(&barrier);
        let node_id = format!("node{}", (i % 5) + 1);
        
        let handle = thread::spawn(move || {
            barrier_clone.wait(); // Synchronize threads to start at the same time
            
            // Try to prepare node (only one thread per node should succeed)
            let result = coordinator_clone.prepare(1, &node_id);
            
            // Sleep a bit to increase chance of race conditions
            thread::sleep(Duration::from_millis(10));
            
            result
        });
        
        handles.push(handle);
    }
    
    // Collect results
    let mut success_count = 0;
    for handle in handles {
        if handle.join().unwrap().is_ok() {
            success_count += 1;
        }
    }
    
    // Exactly 5 threads should have succeeded (one per node)
    assert_eq!(success_count, 5);
    
    // All nodes should now be prepared
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Prepared
    );
    
    // Test concurrent commits and rollbacks
    let coordinator2 = Arc::new(Coordinator::new());
    coordinator2.begin_transaction(1, vec!["node1".to_string()]).unwrap();
    coordinator2.prepare(1, "node1").unwrap();
    
    coordinator2.begin_transaction(2, vec!["node1".to_string()]).unwrap();
    coordinator2.prepare(2, "node1").unwrap();
    
    let c1 = Arc::clone(&coordinator2);
    let c2 = Arc::clone(&coordinator2);
    
    let t1 = thread::spawn(move || {
        c1.commit_transaction(1)
    });
    
    let t2 = thread::spawn(move || {
        c2.rollback_transaction(2)
    });
    
    assert!(t1.join().unwrap().is_ok());
    assert!(t2.join().unwrap().is_ok());
    
    assert_eq!(
        coordinator2.get_transaction_status(1).unwrap(),
        TransactionStatus::Committed
    );
    
    assert_eq!(
        coordinator2.get_transaction_status(2).unwrap(),
        TransactionStatus::RolledBack
    );
}

#[test]
fn test_concurrent_begin_transaction() {
    let coordinator = Arc::new(Coordinator::new());
    let num_threads = 100;
    let barrier = Arc::new(Barrier::new(num_threads));
    
    let mut handles = vec![];
    
    // Create threads that will try to begin transactions with the same ID
    for i in 0..num_threads {
        let coordinator_clone = Arc::clone(&coordinator);
        let barrier_clone = Arc::clone(&barrier);
        
        let handle = thread::spawn(move || {
            barrier_clone.wait(); // Synchronize threads to start at the same time
            
            // All threads try to create the same transaction
            let result = coordinator_clone.begin_transaction(1, vec![format!("node{}", i)]);
            
            result
        });
        
        handles.push(handle);
    }
    
    // Collect results
    let mut success_count = 0;
    for handle in handles {
        if handle.join().unwrap().is_ok() {
            success_count += 1;
        }
    }
    
    // Exactly one thread should have succeeded
    assert_eq!(success_count, 1);
}

#[test]
fn test_large_transaction() {
    let coordinator = Coordinator::new();
    
    // Create a transaction with many nodes
    let nodes: Vec<String> = (0..1000).map(|i| format!("node{}", i)).collect();
    coordinator.begin_transaction(1, nodes.clone()).unwrap();
    
    // Prepare all nodes
    for node in &nodes {
        assert!(coordinator.prepare(1, node).is_ok());
    }
    
    // Verify all nodes are prepared
    assert_eq!(
        coordinator.get_transaction_status(1).unwrap(),
        TransactionStatus::Prepared
    );
    
    // Commit the transaction
    assert!(coordinator.commit_transaction(1).is_ok());
}

#[test]
fn test_multiple_transactions() {
    let coordinator = Coordinator::new();
    
    // Create multiple transactions
    for i in 1..=100 {
        let nodes = vec![format!("node{}", i)];
        coordinator.begin_transaction(i, nodes).unwrap();
        coordinator.prepare(i, &format!("node{}", i)).unwrap();
    }
    
    // Check status of each transaction
    for i in 1..=100 {
        assert_eq!(
            coordinator.get_transaction_status(i).unwrap(),
            TransactionStatus::Prepared
        );
    }
    
    // Commit even transactions, rollback odd transactions
    for i in 1..=100 {
        if i % 2 == 0 {
            coordinator.commit_transaction(i).unwrap();
        } else {
            coordinator.rollback_transaction(i).unwrap();
        }
    }
    
    // Verify statuses
    for i in 1..=100 {
        if i % 2 == 0 {
            assert_eq!(
                coordinator.get_transaction_status(i).unwrap(),
                TransactionStatus::Committed
            );
        } else {
            assert_eq!(
                coordinator.get_transaction_status(i).unwrap(),
                TransactionStatus::RolledBack
            );
        }
    }
}