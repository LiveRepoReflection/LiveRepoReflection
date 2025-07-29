use std::sync::{Arc, atomic::{AtomicU32, Ordering}};
use std::thread;
use std::time::{Duration, Instant};

use lock_manager::LockManager; // Assuming the LockManager struct is defined in src/lib.rs with appropriate methods.

#[test]
fn test_basic_lock_acquire_release() {
    let lm = LockManager::new();
    // Client "client1" acquires a lock on "resource1" without timeout.
    assert!(lm.acquire("client1", "resource1", None).is_ok());
    // Release should succeed.
    assert!(lm.release("client1", "resource1").is_ok());
}

#[test]
fn test_lock_timeout() {
    let lm = LockManager::new();
    // Client "client1" acquires the lock on "resource2".
    assert!(lm.acquire("client1", "resource2", Some(Duration::from_millis(300))).is_ok());
    // Client "client2" attempts to acquire the same lock with a shorter timeout.
    let start = Instant::now();
    let result = lm.acquire("client2", "resource2", Some(Duration::from_millis(150)));
    let elapsed = start.elapsed();
    // Should return an error due to timeout.
    assert!(result.is_err());
    // Ensure that enough time has passed (at least 150ms).
    assert!(elapsed >= Duration::from_millis(150));
    
    // Release the lock with client1 and then allow client2 to successfully acquire it.
    assert!(lm.release("client1", "resource2").is_ok());
    assert!(lm.acquire("client2", "resource2", None).is_ok());
    assert!(lm.release("client2", "resource2").is_ok());
}

#[test]
fn test_reentrant_locking() {
    let lm = LockManager::new();
    // Client "client3" acquires "resource3" twice (reentrant locking).
    assert!(lm.acquire("client3", "resource3", None).is_ok());
    assert!(lm.acquire("client3", "resource3", None).is_ok());
    // Releasing once should not free the lock for others.
    assert!(lm.release("client3", "resource3").is_ok());
    // Another client should still not be able to acquire the lock.
    assert!(lm.acquire("client4", "resource3", Some(Duration::from_millis(100))).is_err());
    // Final release frees the resource.
    assert!(lm.release("client3", "resource3").is_ok());
    // Now client4 can acquire the lock.
    assert!(lm.acquire("client4", "resource3", None).is_ok());
    assert!(lm.release("client4", "resource3").is_ok());
}

#[test]
fn test_release_nonexistent_lock() {
    let lm = LockManager::new();
    // Attempting to release a lock that was never acquired should result in an error.
    let result = lm.release("client1", "nonexistent_resource");
    assert!(result.is_err());
}

#[test]
fn test_concurrent_locking() {
    let lm = Arc::new(LockManager::new());
    let resource = "concurrent_resource";
    let counter = Arc::new(AtomicU32::new(0));
    let mut handles = Vec::new();

    // Spawn 10 threads; each thread will acquire the same resource, increment a counter, then release the lock.
    for i in 0..10 {
        let lm_clone = Arc::clone(&lm);
        let counter_clone = Arc::clone(&counter);
        let client_id = format!("client_{}", i);
        let res = resource.to_string();
        let handle = thread::spawn(move || {
            // Acquire lock without timeout.
            lm_clone.acquire(&client_id, &res, None).expect("Failed to acquire lock");
            // Critical section: read and increment safely.
            let prev = counter_clone.fetch_add(1, Ordering::SeqCst);
            // Simulate work.
            thread::sleep(Duration::from_millis(10));
            // Check that the order is maintained (each thread sees incremental updates).
            assert_eq!(prev, counter_clone.load(Ordering::SeqCst) - 1);
            // Release the lock.
            lm_clone.release(&client_id, &res).expect("Failed to release lock");
        });
        handles.push(handle);
    }

    // Wait for all threads to complete.
    for handle in handles {
        handle.join().expect("Thread panicked");
    }
    // Expect that the counter has been incremented exactly 10 times.
    assert_eq!(counter.load(Ordering::SeqCst), 10);
}

#[test]
fn test_automatic_timeout_release() {
    let lm = LockManager::new();
    // Client "client5" acquires the lock on "resource5" with a short timeout.
    assert!(lm.acquire("client5", "resource5", Some(Duration::from_millis(50))).is_ok());
    // Sleep long enough for the lock to expire automatically.
    thread::sleep(Duration::from_millis(100));
    // Now, client "client6" should be able to acquire the same resource.
    assert!(lm.acquire("client6", "resource5", None).is_ok());
    assert!(lm.release("client6", "resource5").is_ok());
}

#[test]
fn test_multiple_resources() {
    let lm = LockManager::new();
    // Acquiring locks on different resources concurrently.
    let resources = vec!["res1", "res2", "res3", "res4"];
    for res in &resources {
        assert!(lm.acquire("client_multi", res, None).is_ok());
    }
    // Release all locks.
    for res in &resources {
        assert!(lm.release("client_multi", res).is_ok());
    }
}