use adaptive_limiter::RateLimiter;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[test]
fn test_single_client_basic_rate_limiting() {
    let limiter = RateLimiter::new(100, 10); // 100 global rps, 10 per client
    let client_id = "client1".to_string();
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Should allow first 10 requests
    for _ in 0..10 {
        assert!(limiter.is_allowed(client_id.clone(), now));
    }

    // Should deny 11th request
    assert!(!limiter.is_allowed(client_id.clone(), now));
}

#[test]
fn test_multiple_clients() {
    let limiter = RateLimiter::new(20, 10);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Two clients should be able to make their quota of requests
    for _ in 0..10 {
        assert!(limiter.is_allowed("client1".to_string(), now));
        assert!(limiter.is_allowed("client2".to_string(), now));
    }

    // Both should be denied after exceeding their quota
    assert!(!limiter.is_allowed("client1".to_string(), now));
    assert!(!limiter.is_allowed("client2".to_string(), now));
}

#[test]
fn test_global_rate_limit() {
    let limiter = RateLimiter::new(15, 10); // Global limit less than sum of individual limits
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // First client uses their quota
    for _ in 0..10 {
        assert!(limiter.is_allowed("client1".to_string(), now));
    }

    // Second client should be limited by global limit
    for _ in 0..5 {
        assert!(limiter.is_allowed("client2".to_string(), now));
    }

    // Should be denied due to global limit
    assert!(!limiter.is_allowed("client2".to_string(), now));
}

#[test]
fn test_concurrent_access() {
    let limiter = RateLimiter::new(1000, 100);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    let mut handles = vec![];

    // Spawn 10 threads making concurrent requests
    for i in 0..10 {
        let client_id = format!("client{}", i);
        let limiter = limiter.clone();
        
        handles.push(thread::spawn(move || {
            let mut allowed = 0;
            for _ in 0..150 {
                if limiter.is_allowed(client_id.clone(), now) {
                    allowed += 1;
                }
            }
            allowed
        }));
    }

    // Verify that each thread was rate limited appropriately
    for handle in handles {
        let allowed = handle.join().unwrap();
        assert!(allowed <= 100); // Should not exceed per-client limit
    }
}

#[test]
fn test_adaptive_throttling() {
    let limiter = RateLimiter::new(1000, 100);
    let base_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Simulate normal load
    for i in 0..50 {
        assert!(limiter.is_allowed("client1".to_string(), base_time + i));
    }

    // Simulate high load
    limiter.simulate_high_load();
    
    let mut allowed = 0;
    for i in 50..100 {
        if limiter.is_allowed("client1".to_string(), base_time + i) {
            allowed += 1;
        }
    }
    
    // Under high load, should allow fewer requests
    assert!(allowed < 50);

    // Simulate normal load again
    limiter.simulate_normal_load();
    
    allowed = 0;
    for i in 100..150 {
        if limiter.is_allowed("client1".to_string(), base_time + i) {
            allowed += 1;
        }
    }
    
    // Under normal load, should allow more requests
    assert!(allowed > 40);
}

#[test]
fn test_time_window_reset() {
    let limiter = RateLimiter::new(100, 10);
    let base_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Use up the quota
    for _ in 0..10 {
        assert!(limiter.is_allowed("client1".to_string(), base_time));
    }
    
    // Should be denied
    assert!(!limiter.is_allowed("client1".to_string(), base_time));

    // Move to next time window (1 second later)
    let next_window = base_time + 1000;
    
    // Should be allowed again
    for _ in 0..10 {
        assert!(limiter.is_allowed("client1".to_string(), next_window));
    }
}

#[test]
fn test_burst_handling() {
    let limiter = RateLimiter::new(100, 20);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Simulate burst of requests
    let mut allowed = 0;
    for _ in 0..100 {
        if limiter.is_allowed("client1".to_string(), now) {
            allowed += 1;
        }
    }

    // Should not exceed per-client limit
    assert!(allowed <= 20);

    // Wait a short time
    thread::sleep(Duration::from_millis(100));

    // Should still be limited
    assert!(!limiter.is_allowed("client1".to_string(), now + 100));
}

#[test]
fn test_different_time_windows() {
    let limiter = RateLimiter::new(100, 10);
    let base_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Test requests across different time windows
    for window in 0..3 {
        let window_time = base_time + (window * 1000) as i64;
        
        // Each window should allow up to 10 requests
        for _ in 0..10 {
            assert!(limiter.is_allowed("client1".to_string(), window_time));
        }
        
        // 11th request in window should be denied
        assert!(!limiter.is_allowed("client1".to_string(), window_time));
    }
}

#[test]
fn test_system_overload_recovery() {
    let limiter = RateLimiter::new(1000, 100);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;

    // Normal operation
    let mut normal_allowed = 0;
    for _ in 0..50 {
        if limiter.is_allowed("client1".to_string(), now) {
            normal_allowed += 1;
        }
    }

    // Simulate system overload
    limiter.simulate_high_load();
    
    let mut overload_allowed = 0;
    for _ in 0..50 {
        if limiter.is_allowed("client1".to_string(), now) {
            overload_allowed += 1;
        }
    }

    // Recovery
    limiter.simulate_normal_load();
    
    let mut recovery_allowed = 0;
    for _ in 0..50 {
        if limiter.is_allowed("client1".to_string(), now) {
            recovery_allowed += 1;
        }
    }

    // Verify adaptive behavior
    assert!(overload_allowed < normal_allowed);
    assert!(recovery_allowed > overload_allowed);
}