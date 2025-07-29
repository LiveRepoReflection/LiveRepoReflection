#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use std::sync::{Arc, Mutex};

    // Assume the RateLimiter structure is defined in lib.rs with the following API:
    //
    // pub struct RateLimiter { ... }
    //
    // impl RateLimiter {
    //     // Creates a new rate limiter instance with a default rate limit for all keys.
    //     // rate: maximum number of allowed requests per window_secs interval.
    //     pub fn new(default_rate: u32, window_secs: u64) -> Self;
    //
    //     // Attempts to acquire a token for the given key.
    //     // Returns true if the request is allowed; false otherwise.
    //     pub fn try_acquire(&mut self, key: &str) -> bool;
    //
    //     // Dynamically updates the limit for a specific key.
    //     // If key did not previously exist, it creates a new entry with the given rate.
    //     pub fn update_limit(&mut self, key: &str, new_rate: u32);
    //
    //     // Advances the internal clock for testing purposes.
    //     // This simulates the passage of time in seconds.
    //     pub fn advance_time(&mut self, secs: u64);
    // }
    //
    // For testing concurrent access, we wrap the RateLimiter in an Arc<Mutex<>>.

    // A stub of the RateLimiter struct to allow compilation of tests.
    // In an actual implementation, this would be replaced by the real implementation.
    pub struct RateLimiter {
        default_rate: u32,
        window_secs: u64,
        // For simplicity, we simulate time in seconds.
        current_time: u64,
        // Stores for each key, a vector of request timestamps.
        requests: HashMap<String, Vec<u64>>,
        // Stores dynamic limits per key.
        limits: HashMap<String, u32>,
    }

    impl RateLimiter {
        pub fn new(default_rate: u32, window_secs: u64) -> Self {
            RateLimiter {
                default_rate,
                window_secs,
                current_time: 0,
                requests: HashMap::new(),
                limits: HashMap::new(),
            }
        }

        pub fn try_acquire(&mut self, key: &str) -> bool {
            // Determine the rate limit for the key.
            let limit = *self.limits.get(key).unwrap_or(&self.default_rate);
            let entry = self.requests.entry(key.to_string()).or_insert_with(Vec::new);

            // Remove outdated requests that are outside of the current sliding window.
            entry.retain(|&timestamp| self.current_time < timestamp + self.window_secs);

            // If number of requests in the current window is below limit, accept.
            if (entry.len() as u32) < limit {
                entry.push(self.current_time);
                true
            } else {
                false
            }
        }

        pub fn update_limit(&mut self, key: &str, new_rate: u32) {
            self.limits.insert(key.to_string(), new_rate);
        }

        // Advance the internal simulated clock by secs.
        pub fn advance_time(&mut self, secs: u64) {
            self.current_time = self.current_time.saturating_add(secs);
        }
    }

    #[test]
    fn test_basic_allowance() {
        let mut limiter = RateLimiter::new(5, 60);
        // Allow exactly 5 requests.
        for _ in 0..5 {
            assert!(limiter.try_acquire("user1"), "Request should be allowed");
        }
        // 6th request should be rejected.
        assert!(!limiter.try_acquire("user1"), "6th request should be blocked");
    }

    #[test]
    fn test_time_reset() {
        let mut limiter = RateLimiter::new(3, 10);
        // Use up the quota.
        for _ in 0..3 {
            assert!(limiter.try_acquire("user2"), "Request should be allowed");
        }
        assert!(!limiter.try_acquire("user2"), "Quota exceeded, should be blocked");

        // Advance time to reset the window.
        limiter.advance_time(10);
        for _ in 0..3 {
            assert!(limiter.try_acquire("user2"), "After time reset, request should be allowed");
        }
        assert!(!limiter.try_acquire("user2"), "Quota exceeded again, should be blocked");
    }

    #[test]
    fn test_multiple_keys_independent_limits() {
        let mut limiter = RateLimiter::new(2, 30);
        // Test for key "userA".
        assert!(limiter.try_acquire("userA"));
        assert!(limiter.try_acquire("userA"));
        assert!(!limiter.try_acquire("userA"));

        // Test for key "userB" should be independent.
        assert!(limiter.try_acquire("userB"));
        assert!(limiter.try_acquire("userB"));
        assert!(!limiter.try_acquire("userB"));
    }

    #[test]
    fn test_dynamic_update() {
        let mut limiter = RateLimiter::new(1, 20);
        // Initially, only one request is allowed.
        assert!(limiter.try_acquire("user3"));
        assert!(!limiter.try_acquire("user3"));

        // Update limit dynamically for "user3" to allow 3 requests.
        limiter.update_limit("user3", 3);
        // Advance time to reset the window.
        limiter.advance_time(20);
        for _ in 0..3 {
            assert!(limiter.try_acquire("user3"), "After dynamic update, request should be allowed");
        }
        assert!(!limiter.try_acquire("user3"), "Quota exceeded after dynamic update");
    }

    #[test]
    fn test_sliding_window_behavior() {
        let mut limiter = RateLimiter::new(4, 20);
        // At time 0, allow the first request.
        assert!(limiter.try_acquire("user4"), "Request at t=0 allowed");

        // Advance time by 5 seconds; still in same window.
        limiter.advance_time(5);
        assert!(limiter.try_acquire("user4"), "Request at t=5 allowed");

        // Advance time by another 5 seconds (t=10).
        limiter.advance_time(5);
        assert!(limiter.try_acquire("user4"), "Request at t=10 allowed");

        // Advance time by another 5 seconds (t=15).
        limiter.advance_time(5);
        assert!(limiter.try_acquire("user4"), "Request at t=15 allowed");
        // At this point, 4 requests have been made in the window [t=0, t=15].
        assert!(!limiter.try_acquire("user4"), "Additional request should be blocked");

        // Advance time so that the request at t=0 falls outside the sliding window (t becomes 20).
        limiter.advance_time(5);
        // Now one request (at t=0) is out of the window; hence, one slot is available.
        assert!(limiter.try_acquire("user4"), "After sliding window shifts, a new request should be allowed");
    }

    #[test]
    fn test_concurrent_access_simulation() {
        let limiter = Arc::new(Mutex::new(RateLimiter::new(10, 10)));
        let key = "concurrent_user";

        let handles: Vec<_> = (0..20)
            .map(|_| {
                let limiter_clone = Arc::clone(&limiter);
                let key_str = key.to_string();
                std::thread::spawn(move || {
                    let mut lock = limiter_clone.lock().unwrap();
                    lock.try_acquire(&key_str)
                })
            })
            .collect();

        let results: Vec<bool> = handles.into_iter().map(|h| h.join().unwrap()).collect();

        // There should be exactly 10 successful acquisitions.
        let success_count = results.into_iter().filter(|&allowed| allowed).count();
        assert_eq!(success_count, 10, "Only 10 requests should be allowed concurrently");
    }
}