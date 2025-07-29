use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::{fs, thread};

use distro_tx::{Resource, TransactionManager, TransactionStatus};

struct SuccessResource {
    name: String,
    state: Arc<Mutex<bool>>,
}

impl SuccessResource {
    fn new(name: &str) -> Self {
        SuccessResource {
            name: name.to_string(),
            state: Arc::new(Mutex::new(false)),
        }
    }
}

impl Resource for SuccessResource {
    fn prepare(&self) -> Result<(), String> {
        let mut state = self.state.lock().unwrap();
        *state = true;
        Ok(())
    }

    fn commit(&self) -> Result<(), String> {
        let state = self.state.lock().unwrap();
        if *state {
            Ok(())
        } else {
            Err(format!("Resource {} was not prepared", self.name))
        }
    }

    fn rollback(&self) -> Result<(), String> {
        let mut state = self.state.lock().unwrap();
        *state = false;
        Ok(())
    }
}

struct FailingResource {
    name: String,
}

impl FailingResource {
    fn new(name: &str) -> Self {
        FailingResource {
            name: name.to_string(),
        }
    }
}

impl Resource for FailingResource {
    fn prepare(&self) -> Result<(), String> {
        Err(format!("Resource {} failed during prepare", self.name))
    }

    fn commit(&self) -> Result<(), String> {
        Err(format!("Resource {} cannot commit", self.name))
    }

    fn rollback(&self) -> Result<(), String> {
        Ok(())
    }
}

struct SlowResource {
    name: String,
    delay: Duration,
    state: Arc<Mutex<bool>>,
}

impl SlowResource {
    fn new(name: &str, delay: Duration) -> Self {
        SlowResource {
            name: name.to_string(),
            delay,
            state: Arc::new(Mutex::new(false)),
        }
    }
}

impl Resource for SlowResource {
    fn prepare(&self) -> Result<(), String> {
        thread::sleep(self.delay);
        let mut state = self.state.lock().unwrap();
        *state = true;
        Ok(())
    }

    fn commit(&self) -> Result<(), String> {
        let state = self.state.lock().unwrap();
        if *state {
            Ok(())
        } else {
            Err(format!("Resource {} was not prepared", self.name))
        }
    }

    fn rollback(&self) -> Result<(), String> {
        let mut state = self.state.lock().unwrap();
        *state = false;
        Ok(())
    }
}

#[test]
fn test_successful_transaction_commit() {
    let mut tm = TransactionManager::new();
    let txid = tm.initiate_transaction();

    tm.register_resource(txid, Box::new(SuccessResource::new("Res1")));
    tm.register_resource(txid, Box::new(SuccessResource::new("Res2")));

    // Prepare phase must succeed for all resources.
    assert!(tm.prepare(txid).is_ok());
    // Commit phase must succeed.
    assert!(tm.commit(txid).is_ok());
    // Ensure that final transaction status is "Committed".
    assert_eq!(tm.get_status(txid), TransactionStatus::Committed);
}

#[test]
fn test_failed_transaction_rolls_back() {
    let mut tm = TransactionManager::new();
    let txid = tm.initiate_transaction();

    tm.register_resource(txid, Box::new(SuccessResource::new("Res1")));
    tm.register_resource(txid, Box::new(FailingResource::new("FailRes")));

    // Prepare phase should fail due to one failing resource.
    assert!(tm.prepare(txid).is_err());
    // Rollback phase should succeed.
    assert!(tm.rollback(txid).is_ok());
    // Final status should reflect aborted transaction.
    assert_eq!(tm.get_status(txid), TransactionStatus::Aborted);
}

#[test]
fn test_idempotent_operations() {
    let mut tm = TransactionManager::new();
    let txid = tm.initiate_transaction();

    tm.register_resource(txid, Box::new(SuccessResource::new("Res1")));
    tm.register_resource(txid, Box::new(SuccessResource::new("Res2")));

    // First prepare.
    assert!(tm.prepare(txid).is_ok());
    // Second prepare: should be idempotent and return success.
    assert!(tm.prepare(txid).is_ok());

    // First commit.
    assert!(tm.commit(txid).is_ok());
    // Second commit: should also be idempotent.
    assert!(tm.commit(txid).is_ok());
    // Final status should remain "Committed".
    assert_eq!(tm.get_status(txid), TransactionStatus::Committed);
}

#[test]
fn test_timeout_handling() {
    let mut tm = TransactionManager::new();
    // Configure a short timeout for this transaction manager.
    tm.set_timeout(Duration::from_millis(100));
    let txid = tm.initiate_transaction();

    // Register a resource that will delay longer than the timeout.
    tm.register_resource(txid, Box::new(SlowResource::new("SlowRes", Duration::from_millis(200))));

    let start = Instant::now();
    let result = tm.prepare(txid);
    let elapsed = start.elapsed();

    // Expect a timeout error from prepare phase.
    assert!(result.is_err());
    // Confirm that the elapsed time meets the minimum expected timeout.
    assert!(elapsed >= Duration::from_millis(100));
    // Rollback after timeout.
    assert!(tm.rollback(txid).is_ok());
    assert_eq!(tm.get_status(txid), TransactionStatus::Aborted);
}

#[test]
fn test_persistence_and_recovery() {
    // Create a transaction manager and initiate a transaction.
    let mut tm = TransactionManager::new();
    let txid = tm.initiate_transaction();

    tm.register_resource(txid, Box::new(SuccessResource::new("ResPersist")));
    // Execute prepare phase.
    assert!(tm.prepare(txid).is_ok());
    // Persist current state to disk.
    assert!(tm.persist().is_ok());

    // Simulate a restart by creating a new instance of the transaction manager.
    let mut recovered_tm = TransactionManager::new();
    // Recover persisted state.
    assert!(recovered_tm.recover().is_ok());
    // The previously in-flight transaction should be recoverable. Commit it.
    assert!(recovered_tm.commit(txid).is_ok());
    // Final status must be "Committed".
    assert_eq!(recovered_tm.get_status(txid), TransactionStatus::Committed);

    // Clean up persisted state file.
    let _ = fs::remove_file("transaction_manager_state.dat");
}