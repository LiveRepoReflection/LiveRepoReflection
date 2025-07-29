use std::collections::HashMap;
use std::sync::{Mutex};
use std::time::{Duration, Instant};
use std::thread;

pub struct LockManager {
    inner: Mutex<HashMap<String, LockEntry>>,
}

struct LockEntry {
    owner: String,
    count: u32,
    expiration: Option<Instant>,
}

impl LockManager {
    pub fn new() -> Self {
        LockManager {
            inner: Mutex::new(HashMap::new()),
        }
    }

    pub fn acquire(&self, client: &str, resource: &str, wait_timeout: Option<Duration>) -> Result<(), ()> {
        let deadline = wait_timeout.map(|timeout| Instant::now() + timeout);
        loop {
            {
                let mut locks = self.inner.lock().unwrap();
                // Check if the resource is not locked or the lock has expired.
                if let Some(entry) = locks.get_mut(resource) {
                    if let Some(exp) = entry.expiration {
                        if Instant::now() >= exp {
                            // The lock has expired. Remove it.
                            locks.remove(resource);
                        }
                    }
                }
                // Now, if resource is free or expired.
                if let Some(entry) = locks.get_mut(resource) {
                    // Resource is locked.
                    if entry.owner == client {
                        // Reentrant locking: update expiration if provided.
                        entry.count += 1;
                        if let Some(timeout) = wait_timeout {
                            entry.expiration = Some(Instant::now() + timeout);
                        }
                        return Ok(());
                    }
                } else {
                    // Resource is free.
                    let expiration = wait_timeout.map(|timeout| Instant::now() + timeout);
                    locks.insert(resource.to_string(), LockEntry {
                        owner: client.to_string(),
                        count: 1,
                        expiration,
                    });
                    return Ok(());
                }
            }
            // If here, resource is locked by another client.
            // Check if the waiting client has a deadline.
            if let Some(d) = deadline {
                if Instant::now() >= d {
                    return Err(());
                }
            }
            // Sleep a short duration before retrying.
            thread::sleep(Duration::from_millis(10));
        }
    }

    pub fn release(&self, client: &str, resource: &str) -> Result<(), ()> {
        let mut locks = self.inner.lock().unwrap();
        if let Some(entry) = locks.get_mut(resource) {
            if entry.owner != client {
                return Err(());
            }
            // Decrement the reentrancy count.
            entry.count -= 1;
            if entry.count == 0 {
                locks.remove(resource);
            }
            return Ok(());
        }
        Err(())
    }
}