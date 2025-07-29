use std::sync::{Arc, Mutex, Barrier};
use std::time::{Duration, Instant};
use std::thread;
use dtc_core::{TransactionCoordinator, Resource};

struct SuccessResource {
    version: Mutex<u64>,
}

impl SuccessResource {
    fn new() -> Self {
        SuccessResource {
            version: Mutex::new(0),
        }
    }
}

impl Resource for SuccessResource {
    fn prepare(&self) -> Result<bool, String> {
        // Check the version number (simulated) and return success.
        let _v = self.version.lock().unwrap();
        Ok(true)
    }
    fn commit(&self) -> Result<(), String> {
        let mut v = self.version.lock().unwrap();
        *v += 1;
        Ok(())
    }
    fn rollback(&self) -> Result<(), String> {
        Ok(())
    }
}

struct FailingPrepareResource;

impl Resource for FailingPrepareResource {
    fn prepare(&self) -> Result<bool, String> {
        // Simulate conflict resulting in failure to prepare.
        Ok(false)
    }
    fn commit(&self) -> Result<(), String> {
        Ok(())
    }
    fn rollback(&self) -> Result<(), String> {
        Ok(())
    }
}

struct FailingCommitResource {
    version: Mutex<u64>,
}

impl FailingCommitResource {
    fn new() -> Self {
        FailingCommitResource {
            version: Mutex::new(0),
        }
    }
}

impl Resource for FailingCommitResource {
    fn prepare(&self) -> Result<bool, String> {
        let _v = self.version.lock().unwrap();
        Ok(true)
    }
    fn commit(&self) -> Result<(), String> {
        Err("commit failed".to_string())
    }
    fn rollback(&self) -> Result<(), String> {
        Ok(())
    }
}

struct DelayResource {
    delay: Duration,
    version: Mutex<u64>,
}

impl DelayResource {
    fn new(delay: Duration) -> Self {
        DelayResource {
            delay,
            version: Mutex::new(0),
        }
    }
}

impl Resource for DelayResource {
    fn prepare(&self) -> Result<bool, String> {
        thread::sleep(self.delay);
        Ok(true)
    }
    fn commit(&self) -> Result<(), String> {
        let mut v = self.version.lock().unwrap();
        *v += 1;
        Ok(())
    }
    fn rollback(&self) -> Result<(), String> {
        Ok(())
    }
}

#[test]
fn test_successful_transaction() {
    let coordinator = TransactionCoordinator::new();
    let tx_id = coordinator.begin_transaction();
    let res1 = Arc::new(SuccessResource::new());
    let res2 = Arc::new(SuccessResource::new());
    coordinator.enlist_resource(tx_id, res1.clone());
    coordinator.enlist_resource(tx_id, res2.clone());
    let prepare_result = coordinator.prepare_transaction(tx_id, Duration::from_secs(5));
    assert!(prepare_result.is_ok(), "Prepare should succeed for all resources");
    let commit_result = coordinator.commit_transaction(tx_id);
    assert!(commit_result.is_ok(), "Commit should succeed when all resources are prepared");
}

#[test]
fn test_failing_prepare_transaction() {
    let coordinator = TransactionCoordinator::new();
    let tx_id = coordinator.begin_transaction();
    let res1 = Arc::new(SuccessResource::new());
    let res2 = Arc::new(FailingPrepareResource);
    coordinator.enlist_resource(tx_id, res1.clone());
    coordinator.enlist_resource(tx_id, res2.clone());
    let prepare_result = coordinator.prepare_transaction(tx_id, Duration::from_secs(5));
    assert!(prepare_result.is_err(), "Prepare should fail when any resource cannot prepare");
    let rollback_result = coordinator.rollback_transaction(tx_id);
    assert!(rollback_result.is_ok(), "Rollback should succeed after a prepare failure");
}

#[test]
fn test_failing_commit_transaction() {
    let coordinator = TransactionCoordinator::new();
    let tx_id = coordinator.begin_transaction();
    let res1 = Arc::new(SuccessResource::new());
    let res2 = Arc::new(FailingCommitResource::new());
    coordinator.enlist_resource(tx_id, res1.clone());
    coordinator.enlist_resource(tx_id, res2.clone());
    let prepare_result = coordinator.prepare_transaction(tx_id, Duration::from_secs(5));
    assert!(prepare_result.is_ok(), "Prepare should succeed if all resources prepare successfully");
    let commit_result = coordinator.commit_transaction(tx_id);
    assert!(commit_result.is_err(), "Commit should fail if any resource fails during commit");
    let rollback_result = coordinator.rollback_transaction(tx_id);
    assert!(rollback_result.is_ok(), "Rollback should succeed after a commit failure");
}

#[test]
fn test_prepare_timeout() {
    let coordinator = TransactionCoordinator::new();
    let tx_id = coordinator.begin_transaction();
    // Create a resource with a delay longer than the timeout specified.
    let delayed_res = Arc::new(DelayResource::new(Duration::from_secs(6)));
    coordinator.enlist_resource(tx_id, delayed_res);
    let prepare_result = coordinator.prepare_transaction(tx_id, Duration::from_secs(5));
    assert!(prepare_result.is_err(), "Prepare should timeout if a resource delay exceeds the timeout duration");
    let rollback_result = coordinator.rollback_transaction(tx_id);
    assert!(rollback_result.is_ok(), "Rollback should succeed after a prepare timeout");
}

#[test]
fn test_concurrent_transactions() {
    let coordinator = Arc::new(TransactionCoordinator::new());
    let barrier = Arc::new(Barrier::new(3));
    let mut handles = vec![];
    for _ in 0..3 {
        let coord_clone = coordinator.clone();
        let barrier_clone = barrier.clone();
        let handle = thread::spawn(move || {
            let tx_id = coord_clone.begin_transaction();
            let res = Arc::new(SuccessResource::new());
            coord_clone.enlist_resource(tx_id, res);
            barrier_clone.wait();
            let prepare_result = coord_clone.prepare_transaction(tx_id, Duration::from_secs(5));
            assert!(prepare_result.is_ok(), "Concurrent prepare should succeed");
            let commit_result = coord_clone.commit_transaction(tx_id);
            assert!(commit_result.is_ok(), "Concurrent commit should succeed");
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
}