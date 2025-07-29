use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};

use rate_limit::RateLimiter;

#[test]
fn test_basic_rate_limit() {
    // Create a new RateLimiter instance.
    // For this test, we configure client "client1" on endpoint "/api/test" with a limit of 3 requests per second.
    let mut limiter = RateLimiter::new();
    limiter.update_rate("client1", "/api/test", 3, 1);

    // Within one second, first 3 requests should be allowed.
    assert!(limiter.allow_request("client1", "/api/test"), "First request should be allowed");
    assert!(limiter.allow_request("client1", "/api/test"), "Second request should be allowed");
    assert!(limiter.allow_request("client1", "/api/test"), "Third request should be allowed");
    
    // Subsequent request within the same second should be blocked.
    assert!(!limiter.allow_request("client1", "/api/test"), "Fourth request should be blocked");

    // Wait for the time window to elapse.
    thread::sleep(Duration::from_millis(1100));

    // After the window resets, the request should be allowed again.
    assert!(limiter.allow_request("client1", "/api/test"), "Request after resetting window should be allowed");
}

#[test]
fn test_rate_limit_update() {
    // Create a RateLimiter instance and configure with an initial limit.
    let mut limiter = RateLimiter::new();
    limiter.update_rate("client2", "/api/endpoint", 1, 1);

    // With initial limit 1 per second, first request allowed, next blocked.
    assert!(limiter.allow_request("client2", "/api/endpoint"), "First request allowed with initial limit");
    assert!(!limiter.allow_request("client2", "/api/endpoint"), "Second request blocked with initial limit");

    // Update the rate limit to a higher value.
    limiter.update_rate("client2", "/api/endpoint", 5, 1);

    // Wait for the existing time window to pass.
    thread::sleep(Duration::from_millis(1100));

    // Now 5 requests should be allowed within the new time window.
    for i in 1..=5 {
        assert!(limiter.allow_request("client2", "/api/endpoint"), "Request {} should be allowed with updated limit", i);
    }
    assert!(!limiter.allow_request("client2", "/api/endpoint"), "Sixth request should be blocked with updated limit");
}

#[test]
fn test_concurrent_requests() {
    // Configure the limiter for concurrent use: client "client3", endpoint "/api/concurrent", limit of 10 per second.
    let limiter = Arc::new({
        let mut l = RateLimiter::new();
        l.update_rate("client3", "/api/concurrent", 10, 1);
        l
    });

    // Create a barrier for synchronizing 20 threads.
    let thread_count = 20;
    let barrier = Arc::new(Barrier::new(thread_count));
    let allowed_counter = Arc::new(std::sync::atomic::AtomicUsize::new(0));

    let mut handles = Vec::new();
    for _ in 0..thread_count {
        let limiter_clone = Arc::clone(&limiter);
        let barrier_clone = Arc::clone(&barrier);
        let allowed_counter_clone = Arc::clone(&allowed_counter);
        let handle = thread::spawn(move || {
            // Wait for all threads to be ready.
            barrier_clone.wait();
            if limiter_clone.allow_request("client3", "/api/concurrent") {
                allowed_counter_clone.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    // Only up to 10 requests should be allowed concurrently.
    let allowed = allowed_counter.load(std::sync::atomic::Ordering::SeqCst);
    assert!(allowed <= 10, "Allowed concurrent requests ({}) exceed limit", allowed);
}

#[test]
fn test_unknown_client_and_endpoint() {
    // Create a RateLimiter without any configuration for a specific client/endpoint combination.
    // Assume that if no configuration is provided, requests are allowed by default.
    // (This behavior may be adjusted depending on your design. Modify the assertion if needed.)
    let limiter = RateLimiter::new();
    assert!(limiter.allow_request("unknown_client", "/unknown/endpoint"), "Request for unknown client/endpoint should be allowed by default");
}

#[test]
fn test_multiple_time_windows() {
    // Test rate limiting on different time windows.
    let mut limiter = RateLimiter::new();

    // Configure two endpoints with different window durations.
    // client4: endpoint "/fast" gets 2 requests per second.
    limiter.update_rate("client4", "/fast", 2, 1);
    // client4: endpoint "/slow" gets 3 requests per minute.
    limiter.update_rate("client4", "/slow", 3, 60);

    // Test for "/fast"
    assert!(limiter.allow_request("client4", "/fast"), "Fast endpoint first request allowed");
    assert!(limiter.allow_request("client4", "/fast"), "Fast endpoint second request allowed");
    assert!(!limiter.allow_request("client4", "/fast"), "Fast endpoint third request should be blocked");

    thread::sleep(Duration::from_millis(1100));
    assert!(limiter.allow_request("client4", "/fast"), "Fast endpoint request after reset allowed");

    // Test for "/slow": Since the window is 60 seconds, allow only 3 requests.
    assert!(limiter.allow_request("client4", "/slow"), "Slow endpoint first request allowed");
    assert!(limiter.allow_request("client4", "/slow"), "Slow endpoint second request allowed");
    assert!(limiter.allow_request("client4", "/slow"), "Slow endpoint third request allowed");
    assert!(!limiter.allow_request("client4", "/slow"), "Slow endpoint fourth request should be blocked");
}

#[test]
fn test_atomicity_under_concurrency() {
    // Test that the rate limiter handles atomic updates correctly under heavy concurrency.
    let limiter = Arc::new({
        let mut l = RateLimiter::new();
        // Setting a limit of 50 per second for client "client5" endpoint "/atomic".
        l.update_rate("client5", "/atomic", 50, 1);
        l
    });

    let thread_count = 100;
    let barrier = Arc::new(Barrier::new(thread_count));
    let allowed_counter = Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let start_time = Instant::now();

    let mut handles = Vec::new();
    for _ in 0..thread_count {
        let limiter_clone = Arc::clone(&limiter);
        let barrier_clone = Arc::clone(&barrier);
        let allowed_counter_clone = Arc::clone(&allowed_counter);
        let handle = thread::spawn(move || {
            // Synchronize start time among threads.
            barrier_clone.wait();
            if limiter_clone.allow_request("client5", "/atomic") {
                allowed_counter_clone.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let elapsed = start_time.elapsed();
    // Check that the total allowed requests do not exceed the limit.
    let allowed = allowed_counter.load(std::sync::atomic::Ordering::SeqCst);
    assert!(allowed <= 50, "Under concurrent access, allowed requests ({}) exceed limit", allowed);

    // Ensure that the test completes within the time window.
    assert!(elapsed < Duration::from_secs(1), "Test took too long to execute");
}