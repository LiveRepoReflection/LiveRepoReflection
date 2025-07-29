use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use transaction_orchestrator::{
    CoordinatorConfig, Operation, OperationType, Outcome, Transaction, TransactionCoordinator,
};

fn sample_transaction(transaction_id: &str, success: bool, simulate_timeout: bool) -> Transaction {
    // Prepare two operations for the transaction.
    // For service_b, we simulate an abort or a timeout if required.
    let op1 = Operation {
        service_id: "service_a".to_string(),
        operation_id: "op1".to_string(),
        operation_type: OperationType::Commit,
    };
    let op2 = Operation {
        service_id: "service_b".to_string(),
        operation_id: "op2".to_string(),
        operation_type: if success {
            OperationType::Commit
        } else {
            // Simulate a service that intends to abort.
            OperationType::Abort
        },
    };
    // If simulate_timeout is true, the coordinator's config should have a low timeout
    // causing the slow response to trigger a timeout.
    Transaction {
        transaction_id: transaction_id.to_string(),
        operations: vec![op1, op2],
    }
}

#[test]
fn test_successful_transaction() {
    let config = CoordinatorConfig {
        prepare_timeout_ms: 200,
        commit_timeout_ms: 200,
        log_file_path: None,
    };
    let mut coordinator = TransactionCoordinator::new(config);
    let transaction = sample_transaction("tx_success", true, false);
    let outcome = coordinator.execute_transaction(transaction);
    assert!(matches!(outcome, Outcome::Committed));
}

#[test]
fn test_failed_transaction_due_to_abort() {
    let config = CoordinatorConfig {
        prepare_timeout_ms: 200,
        commit_timeout_ms: 200,
        log_file_path: None,
    };
    let mut coordinator = TransactionCoordinator::new(config);
    let transaction = sample_transaction("tx_abort", false, false);
    let outcome = coordinator.execute_transaction(transaction);
    match outcome {
        Outcome::RolledBack(reason) => {
            assert!(reason.contains("abort"), "Expected rollback due to abort, got: {}", reason);
        }
        _ => panic!("Transaction should have been rolled back due to an abort signal"),
    }
}

#[test]
fn test_transaction_timeout() {
    // Set a very short timeout to force a timeout scenario.
    let config = CoordinatorConfig {
        prepare_timeout_ms: 1,
        commit_timeout_ms: 1,
        log_file_path: None,
    };
    let mut coordinator = TransactionCoordinator::new(config);
    let transaction = sample_transaction("tx_timeout", true, true);
    let outcome = coordinator.execute_transaction(transaction);
    match outcome {
        Outcome::RolledBack(reason) => {
            assert!(reason.contains("timeout"), "Expected rollback due to timeout, got: {}", reason);
        }
        _ => panic!("Transaction should have been rolled back due to timeout"),
    }
}

#[test]
fn test_concurrent_transactions() {
    let config = CoordinatorConfig {
        prepare_timeout_ms: 200,
        commit_timeout_ms: 200,
        log_file_path: None,
    };
    let coordinator = Arc::new(Mutex::new(TransactionCoordinator::new(config)));
    let mut handles = Vec::new();

    for i in 0..10 {
        let coordinator_clone = Arc::clone(&coordinator);
        let tx_id = format!("tx_concurrent_{}", i);
        handles.push(thread::spawn(move || {
            let transaction = Transaction {
                transaction_id: tx_id,
                operations: vec![
                    Operation {
                        service_id: "service_a".to_string(),
                        operation_id: "op_a".to_string(),
                        operation_type: OperationType::Commit,
                    },
                    Operation {
                        service_id: "service_b".to_string(),
                        operation_id: "op_b".to_string(),
                        operation_type: OperationType::Commit,
                    },
                ],
            };
            let outcome = coordinator_clone.lock().unwrap().execute_transaction(transaction);
            outcome
        }));
    }

    for handle in handles {
        let outcome = handle.join().unwrap();
        assert!(matches!(outcome, Outcome::Committed));
    }
}

#[test]
fn test_deadlock_detection() {
    // Simulate a deadlock scenario by creating two transactions that may contend for the same resource.
    // The coordinator is expected to detect the deadlock and abort one of the transactions.
    let config = CoordinatorConfig {
        prepare_timeout_ms: 200,
        commit_timeout_ms: 200,
        log_file_path: None,
    };
    let mut coordinator = TransactionCoordinator::new(config);

    let tx1 = Transaction {
        transaction_id: "tx_deadlock_1".to_string(),
        operations: vec![Operation {
            service_id: "service_deadlock".to_string(),
            operation_id: "op1".to_string(),
            operation_type: OperationType::Commit,
        }],
    };

    let tx2 = Transaction {
        transaction_id: "tx_deadlock_2".to_string(),
        operations: vec![Operation {
            service_id: "service_deadlock".to_string(),
            operation_id: "op2".to_string(),
            operation_type: OperationType::Commit,
        }],
    };

    let outcome1 = coordinator.execute_transaction(tx1);
    let outcome2 = coordinator.execute_transaction(tx2);

    let deadlock_detected = matches!(outcome1, Outcome::RolledBack(_)) || matches!(outcome2, Outcome::RolledBack(_));
    assert!(deadlock_detected, "At least one transaction should have been rolled back due to deadlock detection");
}

#[test]
fn test_durability_and_recovery() {
    // Simulate durability by writing to a temporary log file, executing a transaction, then recovering state.
    let temp_log_path = "transaction_orchestrator_test.log";
    {
        let config = CoordinatorConfig {
            prepare_timeout_ms: 200,
            commit_timeout_ms: 200,
            log_file_path: Some(temp_log_path.to_string()),
        };
        let mut coordinator = TransactionCoordinator::new(config);
        let transaction = Transaction {
            transaction_id: "tx_durable".to_string(),
            operations: vec![
                Operation {
                    service_id: "service_a".to_string(),
                    operation_id: "op1".to_string(),
                    operation_type: OperationType::Commit,
                },
                Operation {
                    service_id: "service_b".to_string(),
                    operation_id: "op2".to_string(),
                    operation_type: OperationType::Commit,
                },
            ],
        };
        let outcome = coordinator.execute_transaction(transaction);
        assert!(matches!(outcome, Outcome::Committed));
    }
    // Recover the coordinator state using the same log file.
    let recovered_coordinator = TransactionCoordinator::recover_from_log(temp_log_path);
    // Verify that there are no pending transactions after recovery.
    assert!(recovered_coordinator.pending_transactions().is_empty(), "Recovered coordinator should have no pending transactions");
    // Clean up the temporary log file.
    std::fs::remove_file(temp_log_path).expect("Failed to remove temporary log file");
}