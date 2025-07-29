use std::sync::Arc;
use std::thread;
use std::time::Duration;

// Mock Resource Manager implementation for testing
struct MockResourceManager {
    id: u64,
    should_prepare_fail: bool,
    should_commit_fail: bool,
    should_rollback_fail: bool,
}

impl MockResourceManager {
    fn new(id: u64) -> Self {
        Self {
            id,
            should_prepare_fail: false,
            should_commit_fail: false,
            should_rollback_fail: false,
        }
    }

    fn with_prepare_failure(id: u64) -> Self {
        Self {
            id,
            should_prepare_fail: true,
            should_commit_fail: false,
            should_rollback_fail: false,
        }
    }

    fn with_commit_failure(id: u64) -> Self {
        Self {
            id,
            should_prepare_fail: false,
            should_commit_fail: true,
            should_rollback_fail: false,
        }
    }

    fn with_rollback_failure(id: u64) -> Self {
        Self {
            id,
            should_prepare_fail: false,
            should_commit_fail: false,
            should_rollback_fail: true,
        }
    }
}

impl tx_manager::ResourceManager for MockResourceManager {
    fn prepare(&self) -> bool {
        thread::sleep(Duration::from_millis(10)); // Simulate work
        !self.should_prepare_fail
    }

    fn commit(&self) -> Result<(), String> {
        thread::sleep(Duration::from_millis(10)); // Simulate work
        if self.should_commit_fail {
            Err("Commit failed".to_string())
        } else {
            Ok(())
        }
    }

    fn rollback(&self) -> Result<(), String> {
        thread::sleep(Duration::from_millis(10)); // Simulate work
        if self.should_rollback_fail {
            Err("Rollback failed".to_string())
        } else {
            Ok(())
        }
    }

    fn get_resource_id(&self) -> u64 {
        self.id
    }
}

#[test]
fn test_basic_successful_transaction() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction();
    assert!(tid.is_ok());
    let tid = tid.unwrap();

    let rm1 = Arc::new(MockResourceManager::new(1));
    let rm2 = Arc::new(MockResourceManager::new(2));

    assert!(tm.enlist_resource(tid, rm1).is_ok());
    assert!(tm.enlist_resource(tid, rm2).is_ok());

    assert!(tm.prepare_transaction(tid).unwrap());
    assert!(tm.commit_transaction(tid).unwrap());

    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Committed
    );
}

#[test]
fn test_prepare_phase_failure() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction().unwrap();

    let rm1 = Arc::new(MockResourceManager::new(1));
    let rm2 = Arc::new(MockResourceManager::with_prepare_failure(2));

    assert!(tm.enlist_resource(tid, rm1).is_ok());
    assert!(tm.enlist_resource(tid, rm2).is_ok());

    assert!(!tm.prepare_transaction(tid).unwrap());
    assert!(tm.abort_transaction(tid).unwrap());

    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Aborted
    );
}

#[test]
fn test_commit_phase_failure() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction().unwrap();

    let rm1 = Arc::new(MockResourceManager::new(1));
    let rm2 = Arc::new(MockResourceManager::with_commit_failure(2));

    assert!(tm.enlist_resource(tid, rm1).is_ok());
    assert!(tm.enlist_resource(tid, rm2).is_ok());

    assert!(tm.prepare_transaction(tid).unwrap());
    assert!(!tm.commit_transaction(tid).unwrap());
}

#[test]
fn test_duplicate_resource_enlistment() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction().unwrap();

    let rm1 = Arc::new(MockResourceManager::new(1));
    
    assert!(tm.enlist_resource(tid, rm1.clone()).is_ok());
    assert!(tm.enlist_resource(tid, rm1.clone()).is_err());
}

#[test]
fn test_invalid_transaction_id() {
    let tm = tx_manager::TransactionManager::new();
    let rm1 = Arc::new(MockResourceManager::new(1));

    assert!(tm.enlist_resource(999, rm1).is_err());
    assert!(tm.prepare_transaction(999).is_err());
    assert!(tm.commit_transaction(999).is_err());
    assert!(tm.abort_transaction(999).is_err());
    
    assert_eq!(
        tm.get_transaction_status(999),
        tx_manager::TransactionStatus::NotFound
    );
}

#[test]
fn test_concurrent_transactions() {
    let tm = Arc::new(tx_manager::TransactionManager::new());
    let mut handles = vec![];

    for i in 0..5 {
        let tm_clone = tm.clone();
        handles.push(thread::spawn(move || {
            let tid = tm_clone.begin_transaction().unwrap();
            let rm = Arc::new(MockResourceManager::new(i));
            
            assert!(tm_clone.enlist_resource(tid, rm).is_ok());
            assert!(tm_clone.prepare_transaction(tid).unwrap());
            assert!(tm_clone.commit_transaction(tid).unwrap());
            
            assert_eq!(
                tm_clone.get_transaction_status(tid),
                tx_manager::TransactionStatus::Committed
            );
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_rollback_with_failures() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction().unwrap();

    let rm1 = Arc::new(MockResourceManager::new(1));
    let rm2 = Arc::new(MockResourceManager::with_rollback_failure(2));

    assert!(tm.enlist_resource(tid, rm1).is_ok());
    assert!(tm.enlist_resource(tid, rm2).is_ok());

    assert!(!tm.abort_transaction(tid).unwrap());
    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Aborted
    );
}

#[test]
fn test_transaction_state_transitions() {
    let tm = tx_manager::TransactionManager::new();
    let tid = tm.begin_transaction().unwrap();

    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Active
    );

    let rm = Arc::new(MockResourceManager::new(1));
    assert!(tm.enlist_resource(tid, rm).is_ok());

    assert!(tm.prepare_transaction(tid).unwrap());
    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Prepared
    );

    assert!(tm.commit_transaction(tid).unwrap());
    assert_eq!(
        tm.get_transaction_status(tid),
        tx_manager::TransactionStatus::Committed
    );
}