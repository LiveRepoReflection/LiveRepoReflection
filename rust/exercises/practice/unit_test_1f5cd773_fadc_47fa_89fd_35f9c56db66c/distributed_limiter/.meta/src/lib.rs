use std::collections::{HashMap, VecDeque};
use std::sync::Mutex;
use std::time::{Duration, Instant};

pub struct RateLimiter {
    rate_limit: u32,
    time_window: Duration,
    state: Mutex<HashMap<String, VecDeque<Instant>>>,
}

impl RateLimiter {
    pub fn new(rate_limit: u32, time_window: Duration) -> Self {
        RateLimiter {
            rate_limit,
            time_window,
            state: Mutex::new(HashMap::new()),
        }
    }

    pub fn is_allowed(&self, client_id: &str) -> bool {
        let now = Instant::now();
        let mut state_map = self.state.lock().unwrap();
        let entry = state_map.entry(client_id.to_string()).or_insert_with(VecDeque::new);

        // Purge timestamps that are outside the current time window.
        while let Some(&oldest) = entry.front() {
            if now.duration_since(oldest) > self.time_window {
                entry.pop_front();
            } else {
                break;
            }
        }

        // Check if the client has remaining quota.
        if entry.len() < self.rate_limit as usize {
            entry.push_back(now);
            true
        } else {
            false
        }
    }
}