use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

#[derive(Clone)]
pub struct RateLimiter {
    global_limit: u32,
    per_client_limit: u32,
    client_counters: Arc<Mutex<HashMap<String, ClientData>>>,
    global_counter: Arc<Mutex<WindowCounter>>,
    high_load: Arc<AtomicBool>,
    total_requests: Arc<AtomicUsize>,
}

struct ClientData {
    windows: Vec<WindowCounter>,
}

#[derive(Clone)]
struct WindowCounter {
    timestamp: i64,
    count: u32,
}

impl WindowCounter {
    fn new(timestamp: i64) -> Self {
        WindowCounter {
            timestamp,
            count: 0,
        }
    }
}

impl ClientData {
    fn new() -> Self {
        ClientData {
            windows: Vec::new(),
        }
    }

    fn clean_old_windows(&mut self, current_time: i64) {
        self.windows.retain(|w| current_time - w.timestamp < 1000);
    }

    fn get_requests_in_window(&self, current_time: i64) -> u32 {
        self.windows
            .iter()
            .filter(|w| current_time - w.timestamp < 1000)
            .map(|w| w.count)
            .sum()
    }

    fn add_request(&mut self, timestamp: i64) {
        if let Some(window) = self
            .windows
            .iter_mut()
            .find(|w| timestamp - w.timestamp < 100)
        {
            window.count += 1;
        } else {
            let mut new_window = WindowCounter::new(timestamp);
            new_window.count = 1;
            self.windows.push(new_window);
        }
    }
}

impl RateLimiter {
    pub fn new(global_limit: u32, per_client_limit: u32) -> Self {
        RateLimiter {
            global_limit,
            per_client_limit,
            client_counters: Arc::new(Mutex::new(HashMap::new())),
            global_counter: Arc::new(Mutex::new(WindowCounter::new(0))),
            high_load: Arc::new(AtomicBool::new(false)),
            total_requests: Arc::new(AtomicUsize::new(0)),
        }
    }

    pub fn is_allowed(&self, client_id: String, timestamp: i64) -> bool {
        self.total_requests.fetch_add(1, Ordering::SeqCst);

        let effective_global_limit = if self.high_load.load(Ordering::SeqCst) {
            self.global_limit / 2
        } else {
            self.global_limit
        };

        let effective_client_limit = if self.high_load.load(Ordering::SeqCst) {
            self.per_client_limit / 2
        } else {
            self.per_client_limit
        };

        // Check global limit
        let mut global_counter = self.global_counter.lock().unwrap();
        if timestamp - global_counter.timestamp >= 1000 {
            *global_counter = WindowCounter::new(timestamp);
        }
        if global_counter.count >= effective_global_limit {
            return false;
        }

        // Check per-client limit
        let mut client_counters = self.client_counters.lock().unwrap();
        let client_data = client_counters
            .entry(client_id)
            .or_insert_with(ClientData::new);

        client_data.clean_old_windows(timestamp);

        let current_requests = client_data.get_requests_in_window(timestamp);
        if current_requests >= effective_client_limit {
            return false;
        }

        // Allow request
        client_data.add_request(timestamp);
        global_counter.count += 1;
        true
    }

    pub fn simulate_high_load(&self) {
        self.high_load.store(true, Ordering::SeqCst);
    }

    pub fn simulate_normal_load(&self) {
        self.high_load.store(false, Ordering::SeqCst);
    }

    pub fn get_total_requests(&self) -> usize {
        self.total_requests.load(Ordering::SeqCst)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn test_basic_rate_limiting() {
        let limiter = RateLimiter::new(100, 10);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64;

        for _ in 0..10 {
            assert!(limiter.is_allowed("client1".to_string(), now));
        }
        assert!(!limiter.is_allowed("client1".to_string(), now));
    }

    #[test]
    fn test_window_reset() {
        let limiter = RateLimiter::new(100, 10);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64;

        // Use up the quota
        for _ in 0..10 {
            assert!(limiter.is_allowed("client1".to_string(), now));
        }
        assert!(!limiter.is_allowed("client1".to_string(), now));

        // Test after window reset
        let new_timestamp = now + 1001;
        assert!(limiter.is_allowed("client1".to_string(), new_timestamp));
    }

    #[test]
    fn test_adaptive_throttling() {
        let limiter = RateLimiter::new(100, 10);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64;

        // Normal load
        let mut allowed_normal = 0;
        for _ in 0..15 {
            if limiter.is_allowed("client1".to_string(), now) {
                allowed_normal += 1;
            }
        }

        // High load
        limiter.simulate_high_load();
        let mut allowed_high_load = 0;
        for _ in 0..15 {
            if limiter.is_allowed("client1".to_string(), now) {
                allowed_high_load += 1;
            }
        }

        assert!(allowed_high_load < allowed_normal);
    }
}