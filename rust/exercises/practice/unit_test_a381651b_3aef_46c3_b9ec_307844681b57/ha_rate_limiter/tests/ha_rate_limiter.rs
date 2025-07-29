use std::collections::HashMap;
use std::thread;
use std::time::{Duration};

use ha_rate_limiter::{RateLimiter, RateLimitCfg};

#[test]
fn test_single_rate_limit_enforcement() {
    let mut rl = RateLimiter::new();
    let cfg = RateLimitCfg {
        key: "user_1".to_string(),
        limit: 5,
        window: Duration::from_secs(2),
        priority: 1,
        metadata: HashMap::new(),
    };
    rl.add_rule(cfg);

    // Send 5 requests within the window; they should be allowed.
    for _ in 0..5 {
        let req_metadata = HashMap::new();
        assert!(rl.handle_request("user_1", &req_metadata));
    }
    // A 6th request within the window should be rejected.
    let req_metadata = HashMap::new();
    assert!(!rl.handle_request("user_1", &req_metadata));

    // Sleep until the window expires.
    thread::sleep(Duration::from_secs(2));
    // New request after the window should be allowed.
    assert!(rl.handle_request("user_1", &HashMap::new()));
}

#[test]
fn test_multiple_rate_limits_priority() {
    let mut rl = RateLimiter::new();

    // Lower priority rule with higher limit.
    let mut metadata_low = HashMap::new();
    metadata_low.insert("role".to_string(), "guest".to_string());
    let cfg_low = RateLimitCfg {
        key: "user_2".to_string(),
        limit: 10,
        window: Duration::from_secs(10),
        priority: 1,
        metadata: metadata_low,
    };
    rl.add_rule(cfg_low);

    // Higher priority rule with lower limit.
    let mut metadata_high = HashMap::new();
    metadata_high.insert("role".to_string(), "admin".to_string());
    let cfg_high = RateLimitCfg {
        key: "user_2".to_string(),
        limit: 3,
        window: Duration::from_secs(10),
        priority: 2,
        metadata: metadata_high,
    };
    rl.add_rule(cfg_high);

    // For requests matching the "admin" metadata, the limit should be 3.
    let mut admin_metadata = HashMap::new();
    admin_metadata.insert("role".to_string(), "admin".to_string());
    for _ in 0..3 {
        assert!(rl.handle_request("user_2", &admin_metadata));
    }
    assert!(!rl.handle_request("user_2", &admin_metadata));

    // Requests matching "guest" metadata should follow the guest rule.
    let mut guest_metadata = HashMap::new();
    guest_metadata.insert("role".to_string(), "guest".to_string());
    for _ in 0..10 {
        assert!(rl.handle_request("user_2", &guest_metadata));
    }
    assert!(!rl.handle_request("user_2", &guest_metadata));
}

#[test]
fn test_rate_limit_reset_after_window() {
    let mut rl = RateLimiter::new();
    let cfg = RateLimitCfg {
        key: "ip_192.168.1.1".to_string(),
        limit: 2,
        window: Duration::from_secs(1),
        priority: 1,
        metadata: HashMap::new(),
    };
    rl.add_rule(cfg);

    // Two requests should be allowed.
    assert!(rl.handle_request("ip_192.168.1.1", &HashMap::new()));
    assert!(rl.handle_request("ip_192.168.1.1", &HashMap::new()));
    // Third request should be rejected.
    assert!(!rl.handle_request("ip_192.168.1.1", &HashMap::new()));

    // Sleep long enough for the window to reset.
    thread::sleep(Duration::from_secs(1));
    assert!(rl.handle_request("ip_192.168.1.1", &HashMap::new()));
}

#[test]
fn test_dynamic_configuration_update() {
    let mut rl = RateLimiter::new();
    // Initially set a rule with a limit of 3 requests.
    let cfg_initial = RateLimitCfg {
        key: "user_update".to_string(),
        limit: 3,
        window: Duration::from_secs(5),
        priority: 1,
        metadata: HashMap::new(),
    };
    rl.add_rule(cfg_initial);

    for _ in 0..3 {
        assert!(rl.handle_request("user_update", &HashMap::new()));
    }
    // Fourth request should be rejected.
    assert!(!rl.handle_request("user_update", &HashMap::new()));

    // Update the rule to a higher limit.
    let cfg_updated = RateLimitCfg {
        key: "user_update".to_string(),
        limit: 6,
        window: Duration::from_secs(5),
        priority: 1,
        metadata: HashMap::new(),
    };
    rl.update_rule(cfg_updated);

    // Now 6 requests should be allowed.
    for _ in 0..6 {
        assert!(rl.handle_request("user_update", &HashMap::new()));
    }
    // Seventh request should be rejected.
    assert!(!rl.handle_request("user_update", &HashMap::new()));
}

#[test]
fn test_concurrent_requests() {
    use std::sync::{Arc, Mutex};

    let mut rl = RateLimiter::new();
    let cfg = RateLimitCfg {
        key: "concurrent".to_string(),
        limit: 100,
        window: Duration::from_secs(3),
        priority: 1,
        metadata: HashMap::new(),
    };
    rl.add_rule(cfg);
    let rl = Arc::new(Mutex::new(rl));

    let mut handles = vec![];
    let total_requests = 150;

    for _ in 0..total_requests {
        let rl_clone = Arc::clone(&rl);
        let handle = thread::spawn(move || {
            let req_metadata = HashMap::new();
            let mut allowed = false;
            {
                let mut limiter = rl_clone.lock().unwrap();
                allowed = limiter.handle_request("concurrent", &req_metadata);
            }
            allowed
        });
        handles.push(handle);
    }

    let results: Vec<bool> = handles.into_iter().map(|h| h.join().unwrap()).collect();
    let allowed_count = results.iter().filter(|&&b| b).count();
    // Only up to 100 requests should be allowed.
    assert_eq!(allowed_count, 100);
}