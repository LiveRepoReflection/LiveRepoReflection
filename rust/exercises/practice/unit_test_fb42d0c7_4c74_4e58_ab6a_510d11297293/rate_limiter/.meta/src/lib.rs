use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct RateLimitConfig {
    pub user_id: String,
    pub endpoint: String,
    pub max_requests: u32,
    pub time_window: Duration,
}

#[derive(Debug)]
struct RequestCounter {
    count: u32,
    window_start: Instant,
}

#[derive(Debug)]
pub struct RateLimiter {
    counters: HashMap<String, RequestCounter>,
    configs: HashMap<String, RateLimitConfig>,
}

impl RateLimiter {
    pub fn new() -> Self {
        RateLimiter {
            counters: HashMap::new(),
            configs: HashMap::new(),
        }
    }

    pub fn add_config(&mut self, config: RateLimitConfig) {
        let key = Self::generate_key(&config.user_id, &config.endpoint);
        self.configs.insert(key, config);
    }

    pub fn update_config(&mut self, config: RateLimitConfig) {
        let key = Self::generate_key(&config.user_id, &config.endpoint);
        self.configs.insert(key, config);
    }

    pub async fn check_limit(&mut self, user_id: &str, endpoint: &str) -> bool {
        let key = Self::generate_key(user_id, endpoint);
        
        if let Some(config) = self.configs.get(&key) {
            let counter_key = format!("{}-{}", user_id, endpoint);
            
            let now = Instant::now();
            let mut should_reset = false;

            if let Some(counter) = self.counters.get_mut(&counter_key) {
                if now.duration_since(counter.window_start) > config.time_window {
                    should_reset = true;
                }
            } else {
                should_reset = true;
            }

            if should_reset {
                self.counters.insert(
                    counter_key.clone(),
                    RequestCounter {
                        count: 1,
                        window_start: now,
                    },
                );
                return true;
            }

            if let Some(counter) = self.counters.get_mut(&counter_key) {
                if counter.count < config.max_requests {
                    counter.count += 1;
                    true
                } else {
                    false
                }
            } else {
                false
            }
        } else {
            true
        }
    }

    fn generate_key(user_id: &str, endpoint: &str) -> String {
        format!("{}-{}", user_id, endpoint)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time;

    #[tokio::test]
    async fn test_basic_rate_limiting() {
        let mut limiter = RateLimiter::new();
        let config = RateLimitConfig {
            user_id: "user1".to_string(),
            endpoint: "/api".to_string(),
            max_requests: 2,
            time_window: Duration::from_secs(1),
        };
        limiter.add_config(config);

        assert!(limiter.check_limit("user1", "/api").await);
        assert!(limiter.check_limit("user1", "/api").await);
        assert!(!limiter.check_limit("user1", "/api").await);

        time::sleep(Duration::from_secs(1)).await;
        assert!(limiter.check_limit("user1", "/api").await);
    }
}