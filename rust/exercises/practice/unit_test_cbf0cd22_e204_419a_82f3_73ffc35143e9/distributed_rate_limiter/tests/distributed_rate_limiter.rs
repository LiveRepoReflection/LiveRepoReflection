use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};

use distributed_rate_limiter::RateLimiter;

#[test]
fn test_basic_rate_limiting() {
    // Set a rate limit of 3 requests per 1 second.
    let redis_url = "redis://127.0.0.1/";
    let requests_per_window = 3;
    let window_secs = 1;
    let limiter = RateLimiter::new(redis_url, requests_per_window, window_secs)
        .expect("Failed to initialize RateLimiter");

    // Clear the counter for a fresh test by waiting an extra second.
    thread::sleep(Duration::from_secs(1));

    // First three calls should be allowed.
    for _ in 0..requests_per_window {
        let allowed = limiter.is_allowed("client_basic").expect("Failed checking rate limit");
        assert!(allowed, "Request should be allowed");
    }
    // The fourth request should be rejected.
    let allowed = limiter.is_allowed("client_basic").expect("Failed checking rate limit");
    assert!(!allowed, "Request should be rate limited");
}

#[test]
fn test_rate_limiting_reset() {
    // Set a rate limit of 2 requests per 2 seconds.
    let redis_url = "redis://127.0.0.1/";
    let requests_per_window = 2;
    let window_secs = 2;
    let limiter = RateLimiter::new(redis_url, requests_per_window, window_secs)
        .expect("Failed to initialize RateLimiter");

    // Wait to ensure a clear state.
    thread::sleep(Duration::from_secs(2));

    // Use up the limit.
    for _ in 0..requests_per_window {
        let allowed = limiter.is_allowed("client_reset").expect("Failed checking rate limit");
        assert!(allowed, "Request should be allowed");
    }
    // Next request should be rejected.
    let allowed = limiter.is_allowed("client_reset").expect("Failed checking rate limit");
    assert!(!allowed, "Request should be rate limited");

    // Wait for the window to expire.
    thread::sleep(Duration::from_secs(window_secs + 1));

    // After expiration, requests should be allowed again.
    let allowed = limiter.is_allowed("client_reset").expect("Failed checking rate limit");
    assert!(allowed, "Request should be allowed after window expiration");
}

#[test]
fn test_concurrent_rate_limiting() {
    // Set a rate limit of 50 requests per 3 seconds.
    let redis_url = "redis://127.0.0.1/";
    let requests_per_window = 50;
    let window_secs = 3;
    let limiter = Arc::new(
        RateLimiter::new(redis_url, requests_per_window, window_secs)
            .expect("Failed to initialize RateLimiter"),
    );

    // Wait to ensure a clear state.
    thread::sleep(Duration::from_secs(3));

    let client_id = "client_concurrent";
    let num_threads = 100;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::with_capacity(num_threads);

    // Each thread will call is_allowed once at the same time.
    for _ in 0..num_threads {
        let limiter_clone = Arc::clone(&limiter);
        let barrier_clone = Arc::clone(&barrier);
        let client = client_id.to_string();
        let handle = thread::spawn(move || {
            // Wait for all threads to be ready.
            barrier_clone.wait();
            limiter_clone.is_allowed(&client).unwrap_or(false)
        });
        handles.push(handle);
    }

    let mut allowed_count = 0;
    for handle in handles {
        if handle.join().expect("Thread panicked") {
            allowed_count += 1;
        }
    }
    // The number of allowed requests should not exceed the configured limit.
    assert!(
        allowed_count <= requests_per_window,
        "Allowed requests ({}) should not exceed limit ({})",
        allowed_count,
        requests_per_window
    );
}