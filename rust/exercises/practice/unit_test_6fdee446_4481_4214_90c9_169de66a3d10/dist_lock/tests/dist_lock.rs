use std::thread;
use std::time::{Duration, Instant};
use dist_lock::{acquire_lock, release_lock, LockError};

#[test]
fn test_basic_acquire_release() {
    let resource = "res_basic";
    let client = "client1";
    // Client acquires the lock.
    assert!(acquire_lock(resource, client, 100).is_ok());
    // Client releases the lock.
    assert!(release_lock(resource, client).is_ok());
}

#[test]
fn test_double_acquire_same_client_reentrant() {
    let resource = "res_reentrant";
    let client = "client_re";
    // First acquisition should succeed.
    assert!(acquire_lock(resource, client, 100).is_ok());
    // Second acquisition (reentrant) should also succeed.
    assert!(acquire_lock(resource, client, 100).is_ok());
    // First release should not free the lock completely.
    assert!(release_lock(resource, client).is_ok());
    // Second release should free the lock.
    assert!(release_lock(resource, client).is_ok());
}

#[test]
fn test_acquire_conflict() {
    let resource = "res_conflict";
    let client1 = "client1";
    let client2 = "client2";
    // Client1 acquires the lock.
    assert!(acquire_lock(resource, client1, 100).is_ok());
    // Client2 tries to acquire the same lock with a short timeout and should fail.
    match acquire_lock(resource, client2, 50) {
        Err(LockError::LockAcquisitionTimeout) => {},
        _ => panic!("Expected LockAcquisitionTimeout error for conflicting acquisition."),
    }
    // Client1 releases the lock.
    assert!(release_lock(resource, client1).is_ok());
    // Now Client2 should succeed.
    assert!(acquire_lock(resource, client2, 100).is_ok());
    // Clean up.
    assert!(release_lock(resource, client2).is_ok());
}

#[test]
fn test_release_not_owner() {
    let resource = "res_not_owner";
    let client1 = "client1";
    let client2 = "client2";
    // Client1 acquires the lock.
    assert!(acquire_lock(resource, client1, 100).is_ok());
    // Client2 tries to release a lock it does not hold.
    match release_lock(resource, client2) {
        Err(LockError::LockNotHeld) => {},
        _ => panic!("Expected LockNotHeld error when releasing lock not owned."),
    }
    // Clean up by releasing with client1.
    assert!(release_lock(resource, client1).is_ok());
}

#[test]
fn test_lock_expiration() {
    let resource = "res_expire";
    let client = "client_exp";
    // Acquire the lock with an expectation of built-in expiration.
    // (Assume the lock expires if not renewed within a short period.)
    assert!(acquire_lock(resource, client, 100).is_ok());
    // Wait longer than the expected expiration time.
    thread::sleep(Duration::from_millis(150));
    // A new client should now be able to acquire the lock.
    let client2 = "client_new";
    assert!(acquire_lock(resource, client2, 100).is_ok());
    // Clean up.
    assert!(release_lock(resource, client2).is_ok());
}

#[test]
fn test_concurrent_acquisition() {
    let resource = "res_concurrent";
    let client1 = "client_conc1";
    let client2 = "client_conc2";
    
    // Client1 acquires the lock.
    assert!(acquire_lock(resource, client1, 100).is_ok());
    
    let start = Instant::now();
    // Spawn a thread where Client2 will try to acquire the lock.
    let handle = thread::spawn(move || {
        acquire_lock(resource, client2, 300)
    });
    
    // Sleep for a short duration then release the lock.
    thread::sleep(Duration::from_millis(100));
    assert!(release_lock(resource, client1).is_ok());
    
    // Wait for the spawned thread to finish.
    let res = handle.join().expect("Client2 thread panicked");
    let elapsed = start.elapsed();
    // Ensure that Client2 acquired the lock after Client1 released it.
    assert!(elapsed >= Duration::from_millis(100));
    match res {
        Ok(()) => {
            // Clean up by releasing the lock held by Client2.
            assert!(release_lock(resource, client2).is_ok());
        },
        Err(e) => panic!("Client2 failed to acquire lock concurrently: {:?}", e),
    }
}

#[test]
fn test_invalid_timeout() {
    let resource = "res_invalid_timeout";
    let client1 = "client1";
    let client2 = "client2";
    // Client1 acquires the lock.
    assert!(acquire_lock(resource, client1, 100).is_ok());
    // Client2 attempts to acquire the lock with a zero timeout and should fail.
    match acquire_lock(resource, client2, 0) {
        Err(LockError::LockAcquisitionTimeout) => {},
        _ => panic!("Expected LockAcquisitionTimeout error with 0 ms timeout."),
    }
    // Clean up.
    assert!(release_lock(resource, client1).is_ok());
}