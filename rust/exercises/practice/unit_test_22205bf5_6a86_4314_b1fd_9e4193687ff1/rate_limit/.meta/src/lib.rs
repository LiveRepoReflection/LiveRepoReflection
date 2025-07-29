use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, Instant};

pub struct RateLimiter {
    rules: Mutex<HashMap<(String, String), RateRule>>,
}

struct RateRule {
    limit: u32,
    window: Duration,
    last_reset: Instant,
    count: u32,
}

impl RateLimiter {
    pub fn new() -> Self {
        RateLimiter {
            rules: Mutex::new(HashMap::new()),
        }
    }

    pub fn update_rate(&mut self, client: &str, endpoint: &str, limit: u32, window_seconds: u64) {
        let mut rules = self.rules.lock().unwrap();
        let key = (client.to_string(), endpoint.to_string());
        rules.insert(
            key,
            RateRule {
                limit,
                window: Duration::from_secs(window_seconds),
                last_reset: Instant::now(),
                count: 0,
            },
        );
    }

    pub fn allow_request(&self, client: &str, endpoint: &str) -> bool {
        let key = (client.to_string(), endpoint.to_string());
        let mut rules = self.rules.lock().unwrap();
        if let Some(rule) = rules.get_mut(&key) {
            let now = Instant::now();
            if now.duration_since(rule.last_reset) >= rule.window {
                rule.last_reset = now;
                rule.count = 0;
            }
            if rule.count < rule.limit {
                rule.count += 1;
                true
            } else {
                false
            }
        } else {
            // Allow by default if no rate limit configuration is present.
            true
        }
    }
}