use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use dist_limit::RateLimiter;

#[test]
fn test_single_user_limit() {
    // Configure "user1" with a limit of 5 requests per second.
    let mut limiter = RateLimiter::new();
    limiter.set_rate("user1", 5, Duration::from_secs(1));

    // Allow 5 requests.
    for _ in 0..5 {
        assert!(limiter.allow("user1"), "Request should be allowed");
    }
    // The 6th request should be rejected.
    assert!(!limiter.allow("user1"), "Request should be denied after limit is reached");

    // Wait for the rate limit window to pass.
    thread::sleep(Duration::from_secs(1));
    // Now a new request should be allowed.
    assert!(limiter.allow("user1"), "Request should be allowed after window reset");
}

#[test]
fn test_sliding_window() {
    // Configure "user2" with a limit of 2 requests per 1000ms sliding window.
    let mut limiter = RateLimiter::new();
    limiter.set_rate("user2", 2, Duration::from_millis(1000));

    // Make the first request.
    assert!(limiter.allow("user2"), "First request should be allowed");
    // Wait 500ms.
    thread::sleep(Duration::from_millis(500));
    // Make second request.
    assert!(limiter.allow("user2"), "Second request should be allowed");
    // Immediate third request should be rejected.
    assert!(!limiter.allow("user2"), "Immediate third request should be denied");

    // Wait an additional 600ms (total elapsed time > 1000ms since the first request).
    thread::sleep(Duration::from_millis(600));
    // Now the sliding window should have dropped the first request.
    assert!(limiter.allow("user2"), "Request should be allowed after sliding window advances");
}

#[test]
fn test_multiple_users() {
    // Configure two users with different rate limits.
    let mut limiter = RateLimiter::new();
    limiter.set_rate("userA", 3, Duration::from_secs(1));
    limiter.set_rate("userB", 2, Duration::from_secs(1));

    // userA: Allow exactly 3 requests.
    for _ in 0..3 {
        assert!(limiter.allow("userA"), "userA request should be allowed");
    }
    assert!(!limiter.allow("userA"), "userA should be rate limited after 3 requests");

    // userB: Allow exactly 2 requests.
    for _ in 0..2 {
        assert!(limiter.allow("userB"), "userB request should be allowed");
    }
    assert!(!limiter.allow("userB"), "userB should be rate limited after 2 requests");
}

#[test]
fn test_concurrent_requests() {
    // Configure a rate limit for a common user "concurrent".
    let limiter = Arc::new({
        let mut lim = RateLimiter::new();
        lim.set_rate("concurrent", 10, Duration::from_millis(1000));
        lim
    });

    let num_threads = 20;
    let iterations = 5;
    let barrier = Arc::new(Barrier::new(num_threads));
    let allowed_counter = Arc::new(Mutex::new(0));

    let mut handles = Vec::new();
    for _ in 0..num_threads {
        let limiter_clone = Arc::clone(&limiter);
        let barrier_clone = Arc::clone(&barrier);
        let counter_clone = Arc::clone(&allowed_counter);
        let handle = thread::spawn(move || {
            // Ensure all threads start concurrently.
            barrier_clone.wait();
            for _ in 0..iterations {
                if limiter_clone.allow("concurrent") {
                    let mut count = counter_clone.lock().unwrap();
                    *count += 1;
                }
                // Small delay between requests.
                thread::sleep(Duration::from_millis(10));
            }
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
    // The total allowed requests should not exceed the configured limit per window multiplied by the number of windows spanned.
    let total_allowed = *allowed_counter.lock().unwrap();
    // Since each thread makes several iterations, the rate limiter should enforce the limit per window.
    assert!(total_allowed <= 10 * iterations, "Total allowed requests exceeded the limit across threads");
}

#[test]
fn test_rate_limit_reset_over_time() {
    // Configure "reset_test" with a limit of 3 requests per 500ms.
    let mut limiter = RateLimiter::new();
    limiter.set_rate("reset_test", 3, Duration::from_millis(500));

    // Use 3 requests.
    for _ in 0..3 {
        assert!(limiter.allow("reset_test"), "Request should be allowed within limit");
    }
    // Ensure further request is blocked.
    assert!(!limiter.allow("reset_test"), "Request should be denied after limit is reached");

    // Wait for one complete window period.
    thread::sleep(Duration::from_millis(500));
    // In the new window, allow 3 requests again.
    for _ in 0..3 {
        assert!(limiter.allow("reset_test"), "New window should allow requests");
    }
    // Check that the limit is again imposed.
    assert!(!limiter.allow("reset_test"), "Request should be denied after using up the limit in the new window");
}