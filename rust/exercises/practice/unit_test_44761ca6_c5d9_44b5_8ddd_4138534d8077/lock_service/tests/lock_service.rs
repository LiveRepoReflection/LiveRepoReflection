use std::sync::Arc;
use std::thread;
use std::time::Duration;

#[test]
fn test_basic_lock_unlock() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    let result = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result.is_ok());
    assert!(result.unwrap());
    
    let unlock_result = lock_manager.unlock("resource1".to_string(), "client1".to_string());
    assert!(unlock_result.is_ok());
    assert!(unlock_result.unwrap());
}

#[test]
fn test_concurrent_lock_attempts() {
    let lock_manager = Arc::new(lock_service::DistributedLockManager::new());
    let lock_manager_clone = Arc::clone(&lock_manager);
    
    // First client acquires the lock
    let result1 = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result1.is_ok());
    assert!(result1.unwrap());
    
    // Second client attempts to acquire the same lock
    let handle = thread::spawn(move || {
        let result = lock_manager_clone.lock("resource1".to_string(), "client2".to_string(), 500);
        assert!(result.is_ok());
        assert!(!result.unwrap()); // Should fail to acquire lock
    });
    
    handle.join().unwrap();
}

#[test]
fn test_lock_timeout() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // First client acquires the lock
    let result1 = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result1.is_ok());
    assert!(result1.unwrap());
    
    // Second client attempts with very short timeout
    let result2 = lock_manager.lock("resource1".to_string(), "client2".to_string(), 100);
    assert!(result2.is_ok());
    assert!(!result2.unwrap()); // Should timeout
}

#[test]
fn test_lock_expiration() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // Acquire lock with 500ms timeout
    let result = lock_manager.lock("resource1".to_string(), "client1".to_string(), 500);
    assert!(result.is_ok());
    assert!(result.unwrap());
    
    // Wait for lock to expire (2 * timeout = 1000ms)
    thread::sleep(Duration::from_millis(1100));
    
    // Another client should now be able to acquire the lock
    let result2 = lock_manager.lock("resource1".to_string(), "client2".to_string(), 500);
    assert!(result2.is_ok());
    assert!(result2.unwrap());
}

#[test]
fn test_heartbeat() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // Acquire lock
    let result = lock_manager.lock("resource1".to_string(), "client1".to_string(), 500);
    assert!(result.is_ok());
    assert!(result.unwrap());
    
    // Send heartbeat
    thread::sleep(Duration::from_millis(300));
    let heartbeat_result = lock_manager.heartbeat("resource1".to_string(), "client1".to_string());
    assert!(heartbeat_result.is_ok());
    assert!(heartbeat_result.unwrap());
    
    // Lock should still be valid after original timeout
    thread::sleep(Duration::from_millis(300));
    let invalid_lock_attempt = lock_manager.lock("resource1".to_string(), "client2".to_string(), 100);
    assert!(invalid_lock_attempt.is_ok());
    assert!(!invalid_lock_attempt.unwrap());
}

#[test]
fn test_invalid_unlock() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // Try to unlock a non-existent lock
    let result = lock_manager.unlock("resource1".to_string(), "client1".to_string());
    assert!(result.is_ok());
    assert!(!result.unwrap());
}

#[test]
fn test_invalid_heartbeat() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // Try to send heartbeat for non-existent lock
    let result = lock_manager.heartbeat("resource1".to_string(), "client1".to_string());
    assert!(result.is_ok());
    assert!(!result.unwrap());
}

#[test]
fn test_multiple_resources() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // Lock first resource
    let result1 = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result1.is_ok());
    assert!(result1.unwrap());
    
    // Lock second resource
    let result2 = lock_manager.lock("resource2".to_string(), "client2".to_string(), 1000);
    assert!(result2.is_ok());
    assert!(result2.unwrap());
    
    // Verify both locks are held
    let attempt1 = lock_manager.lock("resource1".to_string(), "client3".to_string(), 100);
    let attempt2 = lock_manager.lock("resource2".to_string(), "client3".to_string(), 100);
    assert!(!attempt1.unwrap());
    assert!(!attempt2.unwrap());
}

#[test]
fn test_reentrant_lock_attempt() {
    let lock_manager = lock_service::DistributedLockManager::new();
    
    // First lock attempt
    let result1 = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result1.is_ok());
    assert!(result1.unwrap());
    
    // Attempt to acquire same lock again
    let result2 = lock_manager.lock("resource1".to_string(), "client1".to_string(), 1000);
    assert!(result2.is_ok());
    assert!(!result2.unwrap()); // Should fail as reentrant locks are not supported
}