use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use dist_rate_limit::{DistributedRateLimiter, RateLimitError};

#[test]
fn test_under_limit() {
    // Create a rate limiter with a limit of 5 requests per 1 second.
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 5, Duration::from_secs(1));
    let client = "client_under_limit";

    // Make 5 successful requests.
    for _ in 0..5 {
        let result = rl.allow(client);
        assert!(result.is_ok(), "Expected request to be allowed under limit");
    }

    // The 6th request should exceed the limit.
    let result = rl.allow(client);
    assert!(result.is_err(), "Expected request to be denied after exceeding limit");

    // Optionally, check that the error is the expected RateLimitError variant.
    if let Err(e) = result {
        match e {
            RateLimitError::Exceeded => {},
            _ => panic!("Unexpected error variant"),
        }
    }
}

#[test]
fn test_window_reset() {
    // Create a rate limiter with a limit of 3 requests per 1 second.
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 3, Duration::from_secs(1));
    let client = "client_window_reset";

    // Make 3 successful requests.
    for _ in 0..3 {
        assert!(rl.allow(client).is_ok());
    }

    // Next request should be denied.
    assert!(rl.allow(client).is_err());

    // Sleep for longer than the rate limiting window to allow the window to reset.
    thread::sleep(Duration::from_secs(2));

    // After the window reset, request should be allowed again.
    assert!(rl.allow(client).is_ok());
}

#[test]
fn test_multiple_clients() {
    // Create a rate limiter with a limit of 3 requests per 1 second.
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 3, Duration::from_secs(1));
    let client1 = "client_multiple_1";
    let client2 = "client_multiple_2";

    // Both clients should be able to make up to 3 requests independently.
    for _ in 0..3 {
        assert!(rl.allow(client1).is_ok());
        assert!(rl.allow(client2).is_ok());
    }

    // Both should now be rate limited.
    assert!(rl.allow(client1).is_err());
    assert!(rl.allow(client2).is_err());
}

#[test]
fn test_concurrent_requests() {
    // Create a rate limiter with a limit of 50 requests per 2 seconds.
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 50, Duration::from_secs(2));
    let client = "client_concurrent";
    let rl = Arc::new(rl);

    // Shared counter to track number of allowed requests.
    let allowed_counter = Arc::new(Mutex::new(0));

    let mut handles = Vec::new();
    for _ in 0..100 {
        let rl_clone = Arc::clone(&rl);
        let counter_clone = Arc::clone(&allowed_counter);
        let client_id = client.to_string();
        let handle = thread::spawn(move || {
            if rl_clone.allow(&client_id).is_ok() {
                let mut count = counter_clone.lock().unwrap();
                *count += 1;
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    // Ensure that exactly 50 requests were allowed.
    let allowed = *allowed_counter.lock().unwrap();
    assert_eq!(allowed, 50, "Expected 50 allowed requests, got {}", allowed);
}

#[test]
fn test_rate_limiter_resilience() {
    // Test to ensure that the rate limiter handles consecutive windows correctly.
    // Create a rate limiter with a limit of 2 requests per 1 second.
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 2, Duration::from_secs(1));
    let client = "client_resilience";

    // Capture start time of operations.
    let start = Instant::now();

    // Perform operations over 3 consecutive windows.
    for _ in 0..3 {
        // In each window, 2 requests should be allowed.
        for _ in 0..2 {
            assert!(rl.allow(client).is_ok());
        }
        // The 3rd request in the same window should be rejected.
        assert!(rl.allow(client).is_err());
        // Wait until the window expires.
        while start.elapsed().as_secs_f32() % 1.0 < 0.9 {
            thread::sleep(Duration::from_millis(50));
        }
        // Sleep a little extra to ensure the next window.
        thread::sleep(Duration::from_millis(150));
    }
}