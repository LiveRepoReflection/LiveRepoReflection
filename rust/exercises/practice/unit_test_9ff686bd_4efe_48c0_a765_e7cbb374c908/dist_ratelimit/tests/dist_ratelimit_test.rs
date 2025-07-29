use dist_ratelimit::*;
use std::thread;
use std::time::Duration;

#[test]
fn test_basic_rate_limiting() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    // Configure rate limit: 3 requests per second
    limiter.configure(client_id, resource_id, 3, Duration::from_secs(1));
    
    // First 3 requests should succeed
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(limiter.is_allowed(client_id, resource_id));
    
    // Fourth request should fail
    assert!(!limiter.is_allowed(client_id, resource_id));
}

#[test]
fn test_multiple_clients() {
    let limiter = RateLimiter::new();
    
    // Configure different limits for different clients
    limiter.configure("client1", "resource1", 2, Duration::from_secs(1));
    limiter.configure("client2", "resource1", 3, Duration::from_secs(1));
    
    // Test client1's limit
    assert!(limiter.is_allowed("client1", "resource1"));
    assert!(limiter.is_allowed("client1", "resource1"));
    assert!(!limiter.is_allowed("client1", "resource1"));
    
    // Test client2's limit (should be independent)
    assert!(limiter.is_allowed("client2", "resource1"));
    assert!(limiter.is_allowed("client2", "resource1"));
    assert!(limiter.is_allowed("client2", "resource1"));
    assert!(!limiter.is_allowed("client2", "resource1"));
}

#[test]
fn test_window_reset() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    limiter.configure(client_id, resource_id, 1, Duration::from_millis(100));
    
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(!limiter.is_allowed(client_id, resource_id));
    
    // Wait for window to reset
    thread::sleep(Duration::from_millis(100));
    
    // Should be allowed again
    assert!(limiter.is_allowed(client_id, resource_id));
}

#[test]
fn test_concurrent_access() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    limiter.configure(client_id, resource_id, 5, Duration::from_secs(1));
    
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let limiter = limiter.clone();
            let c_id = client_id.to_string();
            let r_id = resource_id.to_string();
            
            thread::spawn(move || {
                limiter.is_allowed(&c_id, &r_id)
            })
        })
        .collect();
    
    let results: Vec<bool> = handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect();
    
    // Exactly 5 requests should have been allowed
    assert_eq!(results.iter().filter(|&&r| r).count(), 5);
}

#[test]
fn test_dynamic_rule_update() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    // Initial configuration
    limiter.configure(client_id, resource_id, 1, Duration::from_secs(1));
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(!limiter.is_allowed(client_id, resource_id));
    
    // Update configuration
    limiter.configure(client_id, resource_id, 2, Duration::from_secs(1));
    
    // Should get new requests according to new limit
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(!limiter.is_allowed(client_id, resource_id));
}

#[test]
fn test_metrics() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    limiter.configure(client_id, resource_id, 2, Duration::from_secs(1));
    
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(limiter.is_allowed(client_id, resource_id));
    assert!(!limiter.is_allowed(client_id, resource_id));
    
    let metrics = limiter.get_metrics(client_id, resource_id);
    assert_eq!(metrics.allowed_requests, 2);
    assert_eq!(metrics.rejected_requests, 1);
}

#[test]
#[should_panic]
fn test_invalid_configuration() {
    let limiter = RateLimiter::new();
    limiter.configure("client1", "resource1", 0, Duration::from_secs(1));
}

#[test]
fn test_rule_expiration() {
    let limiter = RateLimiter::new();
    let client_id = "client1";
    let resource_id = "resource1";
    
    limiter.configure(client_id, resource_id, 1, Duration::from_millis(50));
    assert!(limiter.is_allowed(client_id, resource_id));
    
    // Wait for rule to expire
    thread::sleep(Duration::from_millis(200));
    
    // Should return true as rule has expired
    assert!(limiter.is_allowed(client_id, resource_id));
}