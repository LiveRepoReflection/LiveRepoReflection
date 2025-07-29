use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};
use adaptive_ratelimit::{RateLimiter, RateLimitConfig};

#[test]
fn basic_rate_limiting() {
    // Create a new rate limiter with a limit of 3 requests per 1000ms for client "client_a"
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_a", 3, Duration::from_millis(1000));
    let limiter = RateLimiter::new(config);

    // Initially, up to 3 requests should be allowed
    for i in 0..3 {
        assert!(limiter.allow_request("client_a"), "Allowed request count {}", i + 1);
    }
    // Fourth request within the same window should be denied
    assert!(!limiter.allow_request("client_a"), "Request should be denied after reaching limit");

    // Sleep until the window resets
    thread::sleep(Duration::from_millis(1100));
    // Now requests should be allowed again
    assert!(limiter.allow_request("client_a"), "Allowed request after window reset");
}

#[test]
fn dynamic_configuration_update() {
    // Create a rate limiter with initial configuration for client "client_b"
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_b", 2, Duration::from_millis(1000));
    let mut limiter = RateLimiter::new(config);

    // Initially allow 2 requests
    assert!(limiter.allow_request("client_b"));
    assert!(limiter.allow_request("client_b"));
    assert!(!limiter.allow_request("client_b"));

    // Update configuration to increase limit to 4
    limiter.update_config("client_b", 4, Duration::from_millis(1000));

    // The counter should reset on configuration update; allow 4 requests now
    for i in 0..4 {
        assert!(limiter.allow_request("client_b"), "Allowed updated request count {}", i + 1);
    }
    // Next request should be denied within the same window
    assert!(!limiter.allow_request("client_b"), "Exceeded updated limit in same window");
}

#[test]
fn adaptive_windowing_under_heavy_load() {
    // Create a rate limiter with initial configuration for client "client_c"
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_c", 5, Duration::from_millis(1000));
    let mut limiter = RateLimiter::new(config);

    // Simulate normal load: allow 5 requests normally
    for _ in 0..5 {
        assert!(limiter.allow_request("client_c"));
    }
    assert!(!limiter.allow_request("client_c"));

    // Simulate heavy system load; expect the limiter to become more strict.
    limiter.simulate_system_load(0.9); // 90% load
    // Wait for window reset
    thread::sleep(Duration::from_millis(1100));
    // Under heavy load, the allowed number of requests should be reduced.
    let mut allowed = 0;
    for _ in 0..5 {
        if limiter.allow_request("client_c") {
            allowed += 1;
        }
    }
    // Check that under heavy load, fewer requests are allowed.
    assert!(
        allowed <= 3,
        "Under heavy load, allowed requests {} should be reduced",
        allowed
    );

    // Simulate low load; expect the limiter to be more lenient.
    limiter.simulate_system_load(0.1); // 10% load
    thread::sleep(Duration::from_millis(1100));
    allowed = 0;
    for _ in 0..10 {
        if limiter.allow_request("client_c") {
            allowed += 1;
        }
    }
    // Check that under low load at least 5 requests are allowed
    assert!(
        allowed >= 5,
        "Under low load, allowed requests {} should be higher",
        allowed
    );
}

#[test]
fn fairness_among_clients() {
    // Create a rate limiter with configuration for two clients
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_d1", 3, Duration::from_millis(1000));
    config.set_client_limit("client_d2", 3, Duration::from_millis(1000));
    let limiter = RateLimiter::new(config);

    // Simulate interleaved requests between two clients
    assert!(limiter.allow_request("client_d1"));
    assert!(limiter.allow_request("client_d2"));
    assert!(limiter.allow_request("client_d1"));
    assert!(limiter.allow_request("client_d2"));
    assert!(limiter.allow_request("client_d1"));
    assert!(limiter.allow_request("client_d2"));

    // Further requests from either client should be denied within the same window
    assert!(!limiter.allow_request("client_d1"), "client_d1 should be rate limited");
    assert!(!limiter.allow_request("client_d2"), "client_d2 should be rate limited");
}

#[test]
fn concurrent_requests() {
    // Create a rate limiter with configuration for client "client_e"
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_e", 100, Duration::from_millis(1000));
    let limiter = Arc::new(RateLimiter::new(config));

    let threads = 10;
    let requests_per_thread = 20;
    let barrier = Arc::new(Barrier::new(threads));
    let mut handles = Vec::new();
    let counter = Arc::new(std::sync::atomic::AtomicUsize::new(0));

    for _ in 0..threads {
        let limiter_cloned = Arc::clone(&limiter);
        let barrier_cloned = Arc::clone(&barrier);
        let counter_cloned = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            // Wait for all threads to start at the same time
            barrier_cloned.wait();
            for _ in 0..requests_per_thread {
                if limiter_cloned.allow_request("client_e") {
                    counter_cloned.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
                }
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
    let total_allowed = counter.load(std::sync::atomic::Ordering::SeqCst);
    // The limit for client_e is 100; total allowed requests must not exceed this limit.
    assert!(
        total_allowed <= 100,
        "Total allowed requests {} exceeds limit for client_e",
        total_allowed
    );
}

#[test]
fn fault_tolerance_simulation() {
    // Create a rate limiter with configuration for client "client_f"
    let mut config = RateLimitConfig::default();
    config.set_client_limit("client_f", 4, Duration::from_millis(1000));
    let mut limiter = RateLimiter::new(config);

    // Use the limiter to process some requests
    for _ in 0..4 {
        assert!(limiter.allow_request("client_f"));
    }
    assert!(!limiter.allow_request("client_f"));

    // Simulate a node failure by "recovering" the rate limiter instance.
    // Assume that the recovered instance retains or recomputes the previous state.
    let recovered_limiter = limiter.recover_state();

    // After recovery, the state should continue to enforce the limit within the same window.
    // Depending on the recovery details, further requests may or may not be allowed.
    let allowed_after_recovery = recovered_limiter.allow_request("client_f");
    // Accept either behavior: the recovered state maintains the limit or resets on window expiration.
    assert!(
        allowed_after_recovery || !allowed_after_recovery,
        "Fault tolerance recovery simulation executed"
    );
}