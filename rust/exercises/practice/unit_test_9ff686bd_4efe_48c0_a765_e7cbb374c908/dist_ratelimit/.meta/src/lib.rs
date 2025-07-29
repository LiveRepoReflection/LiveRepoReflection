use parking_lot::RwLock;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};

#[derive(Clone)]
pub struct RateLimiter {
    rules: Arc<RwLock<HashMap<(String, String), RuleState>>>,
}

#[derive(Clone)]
struct RuleState {
    limit: u32,
    window: Duration,
    requests: Vec<Instant>,
    allowed_count: u32,
    rejected_count: u32,
    last_accessed: Instant,
}

#[derive(Debug)]
pub struct Metrics {
    pub allowed_requests: u32,
    pub rejected_requests: u32,
}

impl RateLimiter {
    pub fn new() -> Self {
        RateLimiter {
            rules: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn configure(&self, client_id: &str, resource_id: &str, limit: u32, window: Duration) {
        if limit == 0 {
            panic!("Rate limit must be greater than 0");
        }

        let mut rules = self.rules.write();
        rules.insert(
            (client_id.to_string(), resource_id.to_string()),
            RuleState {
                limit,
                window,
                requests: Vec::with_capacity(limit as usize),
                allowed_count: 0,
                rejected_count: 0,
                last_accessed: Instant::now(),
            },
        );
    }

    pub fn is_allowed(&self, client_id: &str, resource_id: &str) -> bool {
        let mut rules = self.rules.write();
        let key = (client_id.to_string(), resource_id.to_string());

        if let Some(rule) = rules.get_mut(&key) {
            rule.last_accessed = Instant::now();

            // Remove expired timestamps
            let now = Instant::now();
            rule.requests.retain(|&timestamp| {
                now.duration_since(timestamp) <= rule.window
            });

            if rule.requests.len() < rule.limit as usize {
                rule.requests.push(now);
                rule.allowed_count += 1;
                true
            } else {
                rule.rejected_count += 1;
                false
            }
        } else {
            // If no rule exists, allow the request
            true
        }
    }

    pub fn get_metrics(&self, client_id: &str, resource_id: &str) -> Metrics {
        let rules = self.rules.read();
        let key = (client_id.to_string(), resource_id.to_string());

        if let Some(rule) = rules.get(&key) {
            Metrics {
                allowed_requests: rule.allowed_count,
                rejected_requests: rule.rejected_count,
            }
        } else {
            Metrics {
                allowed_requests: 0,
                rejected_requests: 0,
            }
        }
    }

    // Clean up expired rules
    fn cleanup_expired_rules(&self, expiry_duration: Duration) {
        let mut rules = self.rules.write();
        let now = Instant::now();
        rules.retain(|_, rule| {
            now.duration_since(rule.last_accessed) < expiry_duration
        });
    }
}

impl Default for RateLimiter {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_cleanup_expired_rules() {
        let limiter = RateLimiter::new();
        limiter.configure("client1", "resource1", 1, Duration::from_secs(1));
        
        // Wait for a short time
        thread::sleep(Duration::from_millis(50));
        
        // Clean up rules older than 25ms
        limiter.cleanup_expired_rules(Duration::from_millis(25));
        
        // Rule should be removed
        assert!(limiter.rules.read().is_empty());
    }

    #[test]
    fn test_rule_isolation() {
        let limiter = RateLimiter::new();
        
        limiter.configure("client1", "resource1", 1, Duration::from_secs(1));
        limiter.configure("client1", "resource2", 2, Duration::from_secs(1));
        
        assert!(limiter.is_allowed("client1", "resource1"));
        assert!(!limiter.is_allowed("client1", "resource1"));
        
        assert!(limiter.is_allowed("client1", "resource2"));
        assert!(limiter.is_allowed("client1", "resource2"));
        assert!(!limiter.is_allowed("client1", "resource2"));
    }
}