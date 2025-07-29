use std::sync::{Arc, mpsc::channel};
use std::thread;
use std::time::Duration;
use txn_coord::{TransactionManager, Operation, TransactionOutcome, ResourceManager, Vote};

struct DummyResourceManager {
    vote: Vote,
    response_delay: Duration,
}

impl ResourceManager for DummyResourceManager {
    fn prepare(&self, _txn_id: u64, _op_id: u64) -> Vote {
        if self.response_delay > Duration::from_millis(0) {
            thread::sleep(self.response_delay);
        }
        self.vote.clone()
    }

    fn commit(&self, _txn_id: u64) {
        // Simulate commit operation.
    }

    fn abort(&self, _txn_id: u64) {
        // Simulate abort operation.
    }
}

#[test]
fn test_commit_transaction() {
    // Create a new TransactionManager with an appropriate timeout and log file.
    let log_file = "txn_coord/tests/test_log_commit.txt";
    let tm = TransactionManager::new(Duration::from_millis(100), log_file);

    // Register two resource managers that will vote to commit promptly.
    tm.register_resource_manager(1, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(10),
    }));
    tm.register_resource_manager(2, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(20),
    }));

    // Create operations corresponding to resource managers.
    let ops = vec![
        Operation { resource_id: 1, op_id: 101 },
        Operation { resource_id: 2, op_id: 201 },
    ];

    let outcome = tm.submit_transaction(1, ops);
    assert_eq!(outcome, TransactionOutcome::Commit);
}

#[test]
fn test_abort_transaction_due_to_vote() {
    // Create a TransactionManager with an appropriate timeout and log file.
    let log_file = "txn_coord/tests/test_log_abort_vote.txt";
    let tm = TransactionManager::new(Duration::from_millis(100), log_file);

    // Register two resource managers; one will vote commit and the other vote abort.
    tm.register_resource_manager(1, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(10),
    }));
    tm.register_resource_manager(2, Arc::new(DummyResourceManager {
        vote: Vote::Abort,
        response_delay: Duration::from_millis(10),
    }));

    let ops = vec![
        Operation { resource_id: 1, op_id: 102 },
        Operation { resource_id: 2, op_id: 202 },
    ];

    let outcome = tm.submit_transaction(2, ops);
    assert_eq!(outcome, TransactionOutcome::Abort);
}

#[test]
fn test_abort_transaction_due_to_timeout() {
    // Set a very short timeout so that a delayed response triggers a timeout.
    let log_file = "txn_coord/tests/test_log_abort_timeout.txt";
    let tm = TransactionManager::new(Duration::from_millis(50), log_file);

    // Register resource managers; one of them delays long enough to trigger a timeout.
    tm.register_resource_manager(1, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(10),
    }));
    tm.register_resource_manager(2, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(100),
    }));

    let ops = vec![
        Operation { resource_id: 1, op_id: 103 },
        Operation { resource_id: 2, op_id: 203 },
    ];

    let outcome = tm.submit_transaction(3, ops);
    assert_eq!(outcome, TransactionOutcome::Abort);
}

#[test]
fn test_concurrent_transactions() {
    let log_file = "txn_coord/tests/test_log_concurrent.txt";
    let tm = Arc::new(TransactionManager::new(Duration::from_millis(100), log_file));

    // Register resource managers.
    tm.register_resource_manager(1, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(10),
    }));
    tm.register_resource_manager(2, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(15),
    }));

    let (tx, rx) = channel();
    let mut handles = Vec::new();

    // Launch 10 concurrent transactions.
    for txn_id in 100..110 {
        let tm_clone = Arc::clone(&tm);
        let tx_clone = tx.clone();
        let handle = thread::spawn(move || {
            let ops = vec![
                Operation { resource_id: 1, op_id: txn_id * 10 + 1 },
                Operation { resource_id: 2, op_id: txn_id * 10 + 2 },
            ];
            let outcome = tm_clone.submit_transaction(txn_id, ops);
            tx_clone.send(outcome).unwrap();
        });
        handles.push(handle);
    }

    drop(tx);

    // Collect outcomes; all should be commit.
    for received in rx {
        assert_eq!(received, TransactionOutcome::Commit);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_recovery_after_crash() {
    // Simulate a recovery after a crash by first creating a transaction that remains
    // in a pending state and then re-instantiating the TransactionManager.
    let log_file = "txn_coord/tests/test_log_recovery.txt";

    {
        // Create a TransactionManager and submit a transaction that simulates a delayed response.
        let tm = TransactionManager::new(Duration::from_millis(100), log_file);
        tm.register_resource_manager(1, Arc::new(DummyResourceManager {
            vote: Vote::Commit,
            response_delay: Duration::from_millis(200),
        }));
        let ops = vec![
            Operation { resource_id: 1, op_id: 501 },
        ];
        let outcome = tm.submit_transaction(50, ops);
        // Given the delay, the transaction should be aborted due to timeout.
        assert_eq!(outcome, TransactionOutcome::Abort);
    }

    // Simulate recovery by reloading the TransactionManager from log.
    let recovered_tm = TransactionManager::recover(log_file);
    // After recovery, the system should be able to process new transactions correctly.
    recovered_tm.register_resource_manager(1, Arc::new(DummyResourceManager {
        vote: Vote::Commit,
        response_delay: Duration::from_millis(10),
    }));
    let ops_new = vec![
        Operation { resource_id: 1, op_id: 502 },
    ];
    let outcome_new = recovered_tm.submit_transaction(51, ops_new);
    assert_eq!(outcome_new, TransactionOutcome::Commit);
}