use std::thread;
use tx_snapshot::Database;

#[test]
fn test_basic_transaction() {
    let db = Database::new();
    let tx1 = db.begin();
    db.write(tx1, "key1".to_string(), "value1".to_string());
    assert_eq!(db.read(tx1, "key1".to_string()), Some("value1".to_string()));
    assert!(db.commit(tx1).is_ok());
}

#[test]
fn test_snapshot_isolation() {
    let db = Database::new();
    
    // First transaction
    let tx1 = db.begin();
    db.write(tx1, "x".to_string(), "1".to_string());
    
    // Second transaction starts before first commits
    let tx2 = db.begin();
    assert_eq!(db.read(tx2, "x".to_string()), None); // Should not see tx1's uncommitted write
    
    // Commit first transaction
    assert!(db.commit(tx1).is_ok());
    
    // tx2 should still see original state
    assert_eq!(db.read(tx2, "x".to_string()), None);
    
    // New transaction should see committed value
    let tx3 = db.begin();
    assert_eq!(db.read(tx3, "x".to_string()), Some("1".to_string()));
}

#[test]
fn test_write_conflict() {
    let db = Database::new();
    
    let tx1 = db.begin();
    let tx2 = db.begin();
    
    db.write(tx1, "key".to_string(), "value1".to_string());
    db.write(tx2, "key".to_string(), "value2".to_string());
    
    assert!(db.commit(tx1).is_ok());
    assert!(db.commit(tx2).is_err()); // Should fail due to write conflict
}

#[test]
fn test_rollback() {
    let db = Database::new();
    
    let tx1 = db.begin();
    db.write(tx1, "key".to_string(), "value".to_string());
    db.rollback(tx1);
    
    let tx2 = db.begin();
    assert_eq!(db.read(tx2, "key".to_string()), None); // Should not see rolled back value
}

#[test]
fn test_concurrent_transactions() {
    let db = Database::new();
    let db_clone = db.clone();
    
    let handle1 = thread::spawn(move || {
        let tx = db_clone.begin();
        db_clone.write(tx, "key1".to_string(), "thread1".to_string());
        thread::sleep(std::time::Duration::from_millis(100));
        db_clone.commit(tx)
    });
    
    let handle2 = thread::spawn(move || {
        let tx = db.begin();
        db.write(tx, "key2".to_string(), "thread2".to_string());
        thread::sleep(std::time::Duration::from_millis(50));
        db.commit(tx)
    });
    
    assert!(handle1.join().unwrap().is_ok());
    assert!(handle2.join().unwrap().is_ok());
}

#[test]
fn test_invalid_transaction_id() {
    let db = Database::new();
    assert_eq!(db.read(999, "key".to_string()), None);
    assert!(db.commit(999).is_err());
}

#[test]
fn test_multiple_reads_same_transaction() {
    let db = Database::new();
    
    let tx1 = db.begin();
    db.write(tx1, "key".to_string(), "original".to_string());
    assert!(db.commit(tx1).is_ok());
    
    let tx2 = db.begin();
    let tx3 = db.begin();
    
    // Both transactions should see the same value consistently
    assert_eq!(db.read(tx2, "key".to_string()), Some("original".to_string()));
    db.write(tx3, "key".to_string(), "new".to_string());
    assert!(db.commit(tx3).is_ok());
    
    // tx2 should still see the original value
    assert_eq!(db.read(tx2, "key".to_string()), Some("original".to_string()));
}

#[test]
fn test_concurrent_reads() {
    let db = Database::new();
    let tx1 = db.begin();
    db.write(tx1, "shared".to_string(), "initial".to_string());
    assert!(db.commit(tx1).is_ok());
    
    let db_clone1 = db.clone();
    let db_clone2 = db.clone();
    
    let handle1 = thread::spawn(move || {
        let tx = db_clone1.begin();
        for _ in 0..1000 {
            assert_eq!(db_clone1.read(tx, "shared".to_string()), Some("initial".to_string()));
        }
        db_clone1.commit(tx)
    });
    
    let handle2 = thread::spawn(move || {
        let tx = db_clone2.begin();
        for _ in 0..1000 {
            assert_eq!(db_clone2.read(tx, "shared".to_string()), Some("initial".to_string()));
        }
        db_clone2.commit(tx)
    });
    
    assert!(handle1.join().unwrap().is_ok());
    assert!(handle2.join().unwrap().is_ok());
}

#[test]
fn test_transaction_isolation_levels() {
    let db = Database::new();
    
    // Setup initial state
    let tx_init = db.begin();
    db.write(tx_init, "counter".to_string(), "0".to_string());
    assert!(db.commit(tx_init).is_ok());
    
    // Start two concurrent transactions
    let tx1 = db.begin();
    let tx2 = db.begin();
    
    // Both should see initial value
    assert_eq!(db.read(tx1, "counter".to_string()), Some("0".to_string()));
    assert_eq!(db.read(tx2, "counter".to_string()), Some("0".to_string()));
    
    // First transaction updates value
    db.write(tx1, "counter".to_string(), "1".to_string());
    assert!(db.commit(tx1).is_ok());
    
    // Second transaction should still see original value
    assert_eq!(db.read(tx2, "counter".to_string()), Some("0".to_string()));
    
    // New transaction should see updated value
    let tx3 = db.begin();
    assert_eq!(db.read(tx3, "counter".to_string()), Some("1".to_string()));
}