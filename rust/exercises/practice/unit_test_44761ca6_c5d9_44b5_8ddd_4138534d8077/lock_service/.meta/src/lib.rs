use std::collections::HashMap;
use std::sync::{Mutex, MutexGuard};
use std::time::{Duration, Instant};

#[derive(Debug)]
pub enum LockError {
    ResourceLocked,
    LockNotHeld,
    InternalError,
}

struct LockInfo {
    client_id: String,
    expiration: Instant,
    timeout: Duration,
}

pub struct DistributedLockManager {
    locks: Mutex<HashMap<String, LockInfo>>,
}

impl DistributedLockManager {
    pub fn new() -> Self {
        DistributedLockManager {
            locks: Mutex::new(HashMap::new()),
        }
    }

    pub fn lock(&self, resource_id: String, client_id: String, timeout: u64) -> Result<bool, LockError> {
        let mut locks = self.locks.lock().map_err(|_| LockError::InternalError)?;
        let now = Instant::now();
        let timeout_duration = Duration::from_millis(timeout);

        // Clean expired locks
        self.cleanup_expired_locks(&mut locks);

        // Check if resource is already locked
        if let Some(lock_info) = locks.get(&resource_id) {
            if lock_info.client_id == client_id {
                // Same client trying to acquire the lock again (no reentrant locks)
                return Ok(false);
            }
            if lock_info.expiration > now {
                return Ok(false);
            }
        }

        // Create new lock
        locks.insert(
            resource_id,
            LockInfo {
                client_id,
                expiration: now + timeout_duration * 2, // Lock expires after 2x timeout
                timeout: timeout_duration,
            },
        );

        Ok(true)
    }

    pub fn unlock(&self, resource_id: String, client_id: String) -> Result<bool, LockError> {
        let mut locks = self.locks.lock().map_err(|_| LockError::InternalError)?;
        
        // Clean expired locks first
        self.cleanup_expired_locks(&mut locks);

        match locks.get(&resource_id) {
            Some(lock_info) => {
                if lock_info.client_id == client_id {
                    locks.remove(&resource_id);
                    Ok(true)
                } else {
                    Ok(false)
                }
            }
            None => Ok(false),
        }
    }

    pub fn heartbeat(&self, resource_id: String, client_id: String) -> Result<bool, LockError> {
        let mut locks = self.locks.lock().map_err(|_| LockError::InternalError)?;
        let now = Instant::now();

        // Clean expired locks first
        self.cleanup_expired_locks(&mut locks);

        match locks.get_mut(&resource_id) {
            Some(lock_info) => {
                if lock_info.client_id == client_id {
                    lock_info.expiration = now + lock_info.timeout * 2;
                    Ok(true)
                } else {
                    Ok(false)
                }
            }
            None => Ok(false),
        }
    }

    fn cleanup_expired_locks(&self, locks: &mut MutexGuard<HashMap<String, LockInfo>>) {
        let now = Instant::now();
        locks.retain(|_, lock_info| lock_info.expiration > now);
    }
}

impl Default for DistributedLockManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_lock_and_unlock() {
        let manager = DistributedLockManager::new();
        assert!(manager.lock("test".to_string(), "client1".to_string(), 1000).unwrap());
        assert!(manager.unlock("test".to_string(), "client1".to_string()).unwrap());
    }

    #[test]
    fn test_lock_expiration() {
        let manager = DistributedLockManager::new();
        assert!(manager.lock("test".to_string(), "client1".to_string(), 100).unwrap());
        thread::sleep(Duration::from_millis(300));
        assert!(manager.lock("test".to_string(), "client2".to_string(), 100).unwrap());
    }

    #[test]
    fn test_heartbeat() {
        let manager = DistributedLockManager::new();
        assert!(manager.lock("test".to_string(), "client1".to_string(), 100).unwrap());
        thread::sleep(Duration::from_millis(50));
        assert!(manager.heartbeat("test".to_string(), "client1".to_string()).unwrap());
        thread::sleep(Duration::from_millis(100));
        // Lock should still be valid due to heartbeat
        assert!(!manager.lock("test".to_string(), "client2".to_string(), 100).unwrap());
    }
}