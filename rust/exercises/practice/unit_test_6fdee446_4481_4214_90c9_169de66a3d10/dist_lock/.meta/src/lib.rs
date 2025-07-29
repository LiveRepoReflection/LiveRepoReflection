use std::collections::HashMap;
use std::sync::{Mutex, MutexGuard, OnceLock};
use std::time::{Duration, Instant};
use std::thread;

#[derive(Debug, PartialEq, Eq)]
pub enum LockError {
    LockAcquisitionTimeout,
    LockNotHeld,
    InternalError,
}

struct LockEntry {
    owner: String,
    count: u32,
    expiration: Instant,
}

impl LockEntry {
    fn new(owner: &str, expiration: Instant) -> Self {
        LockEntry {
            owner: owner.to_string(),
            count: 1,
            expiration,
        }
    }
}

static DEFAULT_LOCK_DURATION: Duration = Duration::from_millis(100);
static LOCKS: OnceLock<Mutex<HashMap<String, LockEntry>>> = OnceLock::new();

fn get_current_locks<'a>() -> Result<MutexGuard<'a, HashMap<String, LockEntry>>, LockError> {
    let mutex = LOCKS.get_or_init(|| Mutex::new(HashMap::new()));
    mutex.lock().map_err(|_| LockError::InternalError)
}

/// Attempts to acquire a lock on the given resource for the provided client.
/// 
/// If the lock is already held by another client and has not expired, this function will wait
/// until either the lock becomes available or the specified timeout (in milliseconds) elapses.
/// A client can re-enter a lock it already holds; this increases a re-entrancy counter. 
pub fn acquire_lock(resource_id: &str, client_id: &str, timeout_ms: u64) -> Result<(), LockError> {
    let timeout = Duration::from_millis(timeout_ms);
    let start = Instant::now();

    loop {
        {
            let mut locks = get_current_locks()?;
            // Check if a lock already exists for the resource.
            if let Some(entry) = locks.get_mut(resource_id) {
                // If the lock has expired, remove it.
                if Instant::now() >= entry.expiration {
                    locks.remove(resource_id);
                } else if entry.owner == client_id {
                    // Re-entrant acquisition: increment counter and refresh expiration.
                    entry.count += 1;
                    entry.expiration = Instant::now() + DEFAULT_LOCK_DURATION;
                    return Ok(());
                }
            }
            // If the resource is not locked, acquire it.
            if !locks.contains_key(resource_id) {
                let expiration = Instant::now() + DEFAULT_LOCK_DURATION;
                locks.insert(resource_id.to_string(), LockEntry::new(client_id, expiration));
                return Ok(());
            }
        }
        // Check if timeout has been reached.
        if Instant::now().duration_since(start) >= timeout {
            return Err(LockError::LockAcquisitionTimeout);
        }
        thread::sleep(Duration::from_millis(10));
    }
}

/// Releases the lock on the given resource for the provided client.
/// 
/// If the client has acquired the lock multiple times (re-entrant locking), this function will
/// decrement the re-entrancy count, and only fully release the lock when the count reaches zero.
pub fn release_lock(resource_id: &str, client_id: &str) -> Result<(), LockError> {
    let mut locks = get_current_locks()?;
    if let Some(entry) = locks.get_mut(resource_id) {
        if entry.owner != client_id {
            return Err(LockError::LockNotHeld);
        }
        if entry.count > 1 {
            entry.count -= 1;
            entry.expiration = Instant::now() + DEFAULT_LOCK_DURATION;
        } else {
            locks.remove(resource_id);
        }
        Ok(())
    } else {
        Err(LockError::LockNotHeld)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Instant;

    #[test]
    fn test_basic_acquire_release() {
        let resource = "res_basic";
        let client = "client1";
        assert!(acquire_lock(resource, client, 100).is_ok());
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
        // Acquire the lock.
        assert!(acquire_lock(resource, client, 100).is_ok());
        // Wait longer than the lock expiration duration.
        thread::sleep(Duration::from_millis(150));
        // A new client should now be able to acquire the expired lock.
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
        let elapsed = Instant::now().duration_since(start);
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
        // Client2 attempts to acquire the lock with a 0 ms timeout and should fail.
        match acquire_lock(resource, client2, 0) {
            Err(LockError::LockAcquisitionTimeout) => {},
            _ => panic!("Expected LockAcquisitionTimeout error with 0 ms timeout."),
        }
        // Clean up.
        assert!(release_lock(resource, client1).is_ok());
    }
}