use std::collections::HashMap;

pub struct RateLimiter {
    default_rate: u32,
    window_secs: u64,
    current_time: u64,
    // Mapping from key to a vector of timestamps (seconds) of when requests were made.
    requests: HashMap<String, Vec<u64>>,
    // Allows per-key dynamic update of rate limits.
    limits: HashMap<String, u32>,
}

impl RateLimiter {
    // Create a new RateLimiter with a default rate limit and a fixed window duration in seconds.
    pub fn new(default_rate: u32, window_secs: u64) -> Self {
        RateLimiter {
            default_rate,
            window_secs,
            current_time: 0,
            requests: HashMap::new(),
            limits: HashMap::new(),
        }
    }

    // Try to acquire permission for a request identified by 'key'.
    // Returns true if the request is allowed (i.e., within the rate limit), false otherwise.
    pub fn try_acquire(&mut self, key: &str) -> bool {
        // Determine the effective rate limit: use per-key limit if exists, otherwise default.
        let limit = *self.limits.get(key).unwrap_or(&self.default_rate);
        // Get or initialize the vector of request timestamps for this key.
        let entry = self.requests.entry(key.to_string()).or_insert_with(Vec::new);
        // Remove requests that fall outside the current sliding window.
        entry.retain(|&timestamp| self.current_time < timestamp + self.window_secs);
        // Allow the request if the current number of recorded requests is below the limit.
        if (entry.len() as u32) < limit {
            entry.push(self.current_time);
            true
        } else {
            false
        }
    }

    // Dynamically update the rate limit for a specific key.
    // If the key does not exist, it begins tracking it using the new limit.
    pub fn update_limit(&mut self, key: &str, new_rate: u32) {
        self.limits.insert(key.to_string(), new_rate);
    }

    // Advances the internal clock by a given number of seconds.
    // This simulates the passage of time for the sliding window mechanism.
    pub fn advance_time(&mut self, secs: u64) {
        self.current_time = self.current_time.saturating_add(secs);
    }
}