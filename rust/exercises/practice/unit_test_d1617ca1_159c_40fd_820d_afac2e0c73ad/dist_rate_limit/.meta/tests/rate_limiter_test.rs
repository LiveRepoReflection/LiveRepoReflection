use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use dist_rate_limit::{DistributedRateLimiter, RateLimitError};

#[test]
fn test_under_limit() {
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 5, Duration::from_secs(1));
    let client = "client_under_limit";
    for _ in 0..5 {
        let result = rl.allow(client);
        assert!(result.is_ok(), "Expected request to be allowed under limit");
    }
    let result = rl.allow(client);
    assert!(result.is_err(), "Expected request to be denied after exceeding limit");
    if let Err(e) = result {
        match e {
            RateLimitError::Exceeded => {},
            _ => panic!("Unexpected error variant"),
        }
    }
}

#[test]
fn test_window_reset() {
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 3, Duration::from_secs(1));
    let client = "client_window_reset";
    for _ in 0..3 {
        assert!(rl.allow(client).is_ok());
    }
    assert!(rl.allow(client).is_err());
    thread::sleep(Duration::from_secs(2));
    assert!(rl.allow(client).is_ok());
}

#[test]
fn test_multiple_clients() {
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 3, Duration::from_secs(1));
    let client1 = "client_multiple_1";
    let client2 = "client_multiple_2";
    for _ in 0..3 {
        assert!(rl.allow(client1).is_ok());
        assert!(rl.allow(client2).is_ok());
    }
    assert!(rl.allow(client1).is_err());
    assert!(rl.allow(client2).is_err());
}

#[test]
fn test_concurrent_requests() {
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 50, Duration::from_secs(2));
    let client = "client_concurrent";
    let rl = Arc::new(rl);
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
    let allowed = *allowed_counter.lock().unwrap();
    assert_eq!(allowed, 50, "Expected 50 allowed requests, got {}", allowed);
}

#[test]
fn test_rate_limiter_resilience() {
    let rl = DistributedRateLimiter::new("redis://127.0.0.1/", 2, Duration::from_secs(1));
    let client = "client_resilience";
    let start = Instant::now();
    for _ in 0..3 {
        for _ in 0..2 {
            assert!(rl.allow(client).is_ok());
        }
        assert!(rl.allow(client).is_err());
        while start.elapsed().as_secs_f32() % 1.0 < 0.9 {
            thread::sleep(Duration::from_millis(50));
        }
        thread::sleep(Duration::from_millis(150));
    }
}