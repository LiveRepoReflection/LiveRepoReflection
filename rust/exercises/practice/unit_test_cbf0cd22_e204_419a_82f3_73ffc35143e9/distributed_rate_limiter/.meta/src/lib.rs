use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH, Duration};

pub struct RateLimiter {
    requests_per_window: u64,
    time_window_seconds: u64,
    store: Arc<Mutex<HashMap<String, (u64, SystemTime)>>>,
}

#[derive(Debug)]
pub struct RateLimiterError(String);

impl std::fmt::Display for RateLimiterError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "RateLimiterError: {}", self.0)
    }
}

impl std::error::Error for RateLimiterError {}

impl RateLimiter {
    pub fn new(redis_url: &str, requests_per_window: u64, time_window_seconds: u64)
        -> Result<RateLimiter, RateLimiterError> 
    {
        // In this simulation, the redis_url is not used.
        Ok(RateLimiter {
            requests_per_window,
            time_window_seconds,
            store: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn is_allowed(&self, client_id: &str) -> Result<bool, RateLimiterError> {
        let now = SystemTime::now();
        let now_secs = now.duration_since(UNIX_EPOCH)
            .map_err(|e| RateLimiterError(format!("Time error: {}", e)))?
            .as_secs();
        let window_start = now_secs - (now_secs % self.time_window_seconds);
        let expire_time = UNIX_EPOCH + Duration::from_secs(window_start + self.time_window_seconds);

        let key = format!("{}:{}", client_id, window_start);

        let mut store = self.store.lock().map_err(|_| RateLimiterError("Mutex poisoned".to_string()))?;

        if let Some((count, stored_expire)) = store.get_mut(&key) {
            if now >= *stored_expire {
                // Key expired: reset the count and update the expiry time.
                *count = 1;
                *stored_expire = expire_time;
                Ok(true)
            } else {
                if *count < self.requests_per_window {
                    *count += 1;
                    Ok(true)
                } else {
                    Ok(false)
                }
            }
        } else {
            // Create a new key for this window.
            store.insert(key, (1, expire_time));
            Ok(true)
        }
    }
}