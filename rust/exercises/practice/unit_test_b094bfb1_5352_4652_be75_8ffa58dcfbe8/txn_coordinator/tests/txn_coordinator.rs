use std::collections::HashMap;
use std::sync::{Arc, Barrier};
use std::thread;

use txn_coordinator::{
    Coordinator, Operation, Transaction, TransactionResult,
};

#[test]
fn test_single_transaction_commit() {
    // Create a coordinator with 3 worker nodes and no simulated failures.
    let coordinator = Coordinator::new(3);

    // Transaction 1: Write operations on two different worker nodes.
    let tx = Transaction {
        id: 1,
        operations: vec![
            Operation::Write {
                node_id: 0,
                key: "key1".to_string(),
                value: "value1".to_string(),
            },
            Operation::Write {
                node_id: 1,
                key: "key2".to_string(),
                value: "value2".to_string(),
            },
        ],
    };

    let result = coordinator.execute_transaction(tx);
    assert_eq!(result, TransactionResult::Committed);

    // Verify that data in each worker node is updated accordingly.
    let data0 = coordinator.get_worker_data(0).expect("Worker 0 should exist");
    assert_eq!(data0.get("key1"), Some(&"value1".to_string()));

    let data1 = coordinator.get_worker_data(1).expect("Worker 1 should exist");
    assert_eq!(data1.get("key2"), Some(&"value2".to_string()));

    // Check that logs record commit for transaction 1.
    let logs = coordinator.get_logs();
    let commit_found = logs.iter().any(|entry| entry.contains("Transaction 1 committed"));
    assert!(commit_found, "Commit log not found for transaction 1");
}

#[test]
fn test_transaction_abort_on_worker_failure() {
    // Create a coordinator with 3 worker nodes.
    // We plan to simulate a failure on worker node 2.
    let coordinator = Coordinator::new(3);

    // Force worker node 2 into a failure state.
    coordinator.simulate_worker_failure(2);

    // Transaction 2: It involves worker node 2.
    let tx = Transaction {
        id: 2,
        operations: vec![
            Operation::Write {
                node_id: 0,
                key: "keyA".to_string(),
                value: "valueA".to_string(),
            },
            Operation::Write {
                node_id: 2,
                key: "keyB".to_string(),
                value: "valueB".to_string(),
            },
        ],
    };

    let result = coordinator.execute_transaction(tx);
    assert_eq!(result, TransactionResult::Aborted);

    // Verify that the worker nodes' data remains unchanged for worker involved in aborted transaction.
    let data0 = coordinator.get_worker_data(0).expect("Worker 0 should exist");
    assert!(data0.get("keyA").is_none(), "Data should not be committed on worker 0");

    let data2 = coordinator.get_worker_data(2).expect("Worker 2 should exist");
    assert!(data2.get("keyB").is_none(), "Data should not be committed on failed worker 2");

    // Verify logs contain the aborted message.
    let logs = coordinator.get_logs();
    let abort_found = logs.iter().any(|entry| entry.contains("Transaction 2 aborted"));
    assert!(abort_found, "Abort log not found for transaction 2");
}

#[test]
fn test_concurrent_transactions() {
    // Create a coordinator with 5 worker nodes.
    let coordinator = Arc::new(Coordinator::new(5));
    let num_transactions = 10;
    let barrier = Arc::new(Barrier::new(num_transactions));
    let mut handles = Vec::with_capacity(num_transactions);
    let mut results = Vec::new();

    for i in 0..num_transactions {
        let coordinator_clone = Arc::clone(&coordinator);
        let barrier_clone = Arc::clone(&barrier);
        // Each transaction writes to different worker nodes.
        let tx = Transaction {
            id: (100 + i) as u64,
            operations: vec![
                Operation::Write {
                    node_id: i % 5,
                    key: format!("key_{}", i),
                    value: format!("value_{}", i),
                },
                Operation::Write {
                    node_id: (i + 1) % 5,
                    key: format!("key2_{}", i),
                    value: format!("value2_{}", i),
                },
            ],
        };

        let handle = thread::spawn(move || {
            // Ensure all threads start executing at the same time.
            barrier_clone.wait();
            let res = coordinator_clone.execute_transaction(tx);
            res
        });
        handles.push(handle);
    }

    for handle in handles {
        let res = handle.join().expect("Thread panicked");
        results.push(res);
    }

    // All transactions should have committed if there is no simulated failure.
    for res in results {
        assert_eq!(res, TransactionResult::Committed);
    }

    // Check that data is present in the workers.
    // We check for a couple of known keys.
    let data0 = coordinator.get_worker_data(0).expect("Worker 0 should exist");
    // Find if any key starting with "key_" was committed to worker 0.
    let key_found = data0.keys().any(|k| k.starts_with("key_"));
    assert!(key_found, "Worker 0 should contain at least one key from concurrent transactions");

    // Ensure logs length is at least equal to number of transactions committed.
    let logs = coordinator.get_logs();
    let commit_logs: Vec<&String> = logs.iter().filter(|entry| entry.contains("committed")).collect();
    assert!(commit_logs.len() >= num_transactions, "Not all transactions' commits were logged");
}

#[test]
fn test_transaction_with_mixed_operations() {
    // Create a coordinator with 4 worker nodes.
    let coordinator = Coordinator::new(4);

    // Transaction 3: Mix of Write, Read, and Delete operations.
    // For simulation, the Read operation does not affect the data store.
    // Assume that Delete on non-existent key is allowed but should have no effect.
    // This transaction should commit successfully.
    let tx = Transaction {
        id: 3,
        operations: vec![
            Operation::Write {
                node_id: 1,
                key: "alpha".to_string(),
                value: "bravo".to_string(),
            },
            Operation::Read {
                node_id: 1,
                key: "alpha".to_string(),
            },
            Operation::Delete {
                node_id: 1,
                key: "nonexistent".to_string(),
            },
            Operation::Write {
                node_id: 3,
                key: "gamma".to_string(),
                value: "delta".to_string(),
            },
        ],
    };

    let result = coordinator.execute_transaction(tx);
    assert_eq!(result, TransactionResult::Committed);

    // Verify that key "alpha" was written to worker 1.
    let data1 = coordinator.get_worker_data(1).expect("Worker 1 should exist");
    assert_eq!(data1.get("alpha"), Some(&"bravo".to_string()));

    // Verify that key "gamma" was written to worker 3.
    let data3 = coordinator.get_worker_data(3).expect("Worker 3 should exist");
    assert_eq!(data3.get("gamma"), Some(&"delta".to_string()));

    // Verify logs for transaction 3.
    let logs = coordinator.get_logs();
    let tx3_commit = logs.iter().any(|entry| entry.contains("Transaction 3 committed"));
    assert!(tx3_commit, "Transaction 3 commit log not found");
}