use std::collections::HashMap;
use std::sync::{Mutex, Once};
use std::time::{Duration, Instant};

#[derive(Debug, PartialEq)]
pub enum RateLimitError {
    Exceeded,
}

pub struct DistributedRateLimiter {
    limit: usize,
    window: Duration,
    _conn_str: String,
}

impl DistributedRateLimiter {
    pub fn new(conn_str: &str, limit: usize, window: Duration) -> Self {
        DistributedRateLimiter {
            limit,
            window,
            _conn_str: conn_str.to_string(),
        }
    }

    pub fn allow(&self, client: &str) -> Result<(), RateLimitError> {
        let mut store = get_redis_store().lock().unwrap();
        let now = Instant::now();
        let entry = store.entry(client.to_string()).or_insert((now, 0));
        // If the current window has expired, reset the counter
        if now.duration_since(entry.0) > self.window {
            *entry = (now, 1);
            return Ok(());
        }
        if entry.1 < self.limit {
            entry.1 += 1;
            Ok(())
        } else {
            Err(RateLimitError::Exceeded)
        }
    }
}

fn get_redis_store() -> &'static Mutex<HashMap<String, (Instant, usize)>> {
    static mut STORE: Option<Mutex<HashMap<String, (Instant, usize)>>> = None;
    static INIT: Once = Once::new();
    unsafe {
        INIT.call_once(|| {
            STORE = Some(Mutex::new(HashMap::new()));
        });
        STORE.as_ref().unwrap()
    }
}