use distributed_limiter::RateLimiter;
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

#[test]
fn test_single_client_limit() {
    // Create a rate limiter with limit 3 requests per 1 second.
    let limiter = RateLimiter::new(3, Duration::from_secs(1));
    let client = "client_test";

    // First 3 requests should be allowed.
    assert!(limiter.is_allowed(client));
    assert!(limiter.is_allowed(client));
    assert!(limiter.is_allowed(client));

    // Fourth request should be rejected.
    assert!(!limiter.is_allowed(client));

    // Wait for the time window to reset.
    thread::sleep(Duration::from_secs(1));

    // After the window resets, requests should be allowed again.
    assert!(limiter.is_allowed(client));
}

#[test]
fn test_multiple_clients() {
    // Create a rate limiter with limit 2 requests per 1 second.
    let limiter = RateLimiter::new(2, Duration::from_secs(1));
    let client1 = "client1";
    let client2 = "client2";

    // Client1 should be allowed for 2 requests.
    assert!(limiter.is_allowed(client1));
    assert!(limiter.is_allowed(client1));
    // The 3rd request should be rejected.
    assert!(!limiter.is_allowed(client1));

    // Client2 has a separate count and should also be allowed for 2 requests.
    assert!(limiter.is_allowed(client2));
    assert!(limiter.is_allowed(client2));
    // The 3rd request for client2 should be rejected.
    assert!(!limiter.is_allowed(client2));
}

#[test]
fn test_concurrent_access() {
    // Create a rate limiter with a generous limit for the duration.
    let limiter = Arc::new(RateLimiter::new(100, Duration::from_secs(1)));
    let client = "concurrent_client";
    let mut handles = Vec::new();
    let start = Instant::now();

    // Spawn multiple threads to invoke is_allowed concurrently.
    for _ in 0..10 {
        let limiter_clone = Arc::clone(&limiter);
        let client_clone = client.to_string();
        let handle = thread::spawn(move || {
            let mut allowed_count = 0;
            // Each thread attempts 20 requests.
            for _ in 0..20 {
                if limiter_clone.is_allowed(&client_clone) {
                    allowed_count += 1;
                }
                // Sleep briefly to simulate processing time.
                thread::sleep(Duration::from_millis(5));
            }
            allowed_count
        });
        handles.push(handle);
    }

    let mut total_allowed = 0;
    for handle in handles {
        total_allowed += handle.join().unwrap();
    }
    // Ensure that the total allowed requests do not exceed the configured limit.
    assert!(total_allowed <= 100, "Total allowed requests {} exceed limit", total_allowed);

    // Ensure that the test duration covers the entire rate window.
    let elapsed = start.elapsed();
    if elapsed < Duration::from_secs(1) {
        thread::sleep(Duration::from_secs(1) - elapsed);
    }
}

#[test]
fn test_rate_reset() {
    // Create a rate limiter with limit 2 requests per 1 second.
    let limiter = RateLimiter::new(2, Duration::from_secs(1));
    let client = "reset_test";

    // Fill the quota.
    assert!(limiter.is_allowed(client));
    assert!(limiter.is_allowed(client));
    assert!(!limiter.is_allowed(client));

    // Wait for half the window; still should be rejected.
    thread::sleep(Duration::from_millis(500));
    assert!(!limiter.is_allowed(client));

    // Wait additional time to ensure the window has expired.
    thread::sleep(Duration::from_millis(600));
    // Now the requests should be accepted as the window has reset.
    assert!(limiter.is_allowed(client));
    assert!(limiter.is_allowed(client));
    // Again, exceeding the limit should be rejected.
    assert!(!limiter.is_allowed(client));
}