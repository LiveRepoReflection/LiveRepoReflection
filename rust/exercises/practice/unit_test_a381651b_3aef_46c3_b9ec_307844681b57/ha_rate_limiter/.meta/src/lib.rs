use std::collections::HashMap;
use std::time::{Duration, Instant};

#[derive(Clone, Debug)]
pub struct RateLimitCfg {
    pub key: String,
    pub limit: u32,
    pub window: Duration,
    pub priority: u32,
    pub metadata: HashMap<String, String>,
}

struct RateLimitRule {
    config: RateLimitCfg,
    count: u32,
    window_start: Instant,
}

impl RateLimitRule {
    fn new(cfg: RateLimitCfg) -> Self {
        Self {
            config: cfg,
            count: 0,
            window_start: Instant::now(),
        }
    }

    fn reset(&mut self) {
        self.count = 0;
        self.window_start = Instant::now();
    }

    fn check_and_increment(&mut self) -> bool {
        let now = Instant::now();
        if now.duration_since(self.window_start) >= self.config.window {
            self.reset();
        }
        if self.count < self.config.limit {
            self.count += 1;
            true
        } else {
            false
        }
    }

    fn matches(&self, req_metadata: &HashMap<String, String>) -> bool {
        // A rule applies if all key/value pairs in the rule's metadata exist and match in the request's metadata.
        for (key, value) in &self.config.metadata {
            if req_metadata.get(key) != Some(value) {
                return false;
            }
        }
        true
    }
}

pub struct RateLimiter {
    rules: Vec<RateLimitRule>,
}

impl RateLimiter {
    pub fn new() -> Self {
        Self { rules: Vec::new() }
    }

    pub fn add_rule(&mut self, cfg: RateLimitCfg) {
        let rule = RateLimitRule::new(cfg);
        self.rules.push(rule);
    }

    pub fn update_rule(&mut self, cfg: RateLimitCfg) {
        // Update the rule if it exists (matching key and metadata), otherwise add as new.
        for rule in self.rules.iter_mut() {
            if rule.config.key == cfg.key && rule.config.metadata == cfg.metadata {
                rule.config = cfg;
                rule.reset();
                return;
            }
        }
        self.add_rule(cfg);
    }

    pub fn handle_request(&mut self, key: &str, req_metadata: &HashMap<String, String>) -> bool {
        // Find rules matching the provided key and request metadata.
        let mut applicable: Vec<&mut RateLimitRule> = self
            .rules
            .iter_mut()
            .filter(|rule| rule.config.key == key && rule.matches(req_metadata))
            .collect();

        // If no rule applies, allow the request.
        if applicable.is_empty() {
            return true;
        }

        // Choose the rule with the highest priority.
        applicable.sort_by(|a, b| b.config.priority.cmp(&a.config.priority));
        let selected_rule = applicable.first_mut().unwrap();
        selected_rule.check_and_increment()
    }
}