use std::sync::{Arc, Barrier};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::thread;
use std::time::Duration;

use distributed_ratelimiter::{Cluster, Config, RateLimiter};

#[test]
fn test_token_consumption() {
    let config = Config {
        capacity: 5,
        refill_rate: 1.0, // tokens per second
    };
    let mut limiter = RateLimiter::new("client_1".to_string(), config);
    
    // Consume tokens up to capacity.
    for _ in 0..5 {
        assert!(limiter.allow_request(), "Expected request to be allowed");
    }
    // Next request should be rejected since bucket is empty.
    assert!(!limiter.allow_request(), "Expected request to be rejected due to empty bucket");
}

#[test]
fn test_bucket_refill() {
    let config = Config {
        capacity: 3,
        refill_rate: 1.0, // 1 token per second
    };
    let mut limiter = RateLimiter::new("client_2".to_string(), config);
    
    // Deplete the bucket.
    for _ in 0..3 {
        assert!(limiter.allow_request(), "Expected request to be allowed");
    }
    assert!(!limiter.allow_request(), "Expected request to be rejected after bucket is empty");

    // Sleep to allow the bucket to refill.
    thread::sleep(Duration::from_secs(2));

    // After 2 seconds, at least 2 tokens should be available.
    let mut allowed = 0;
    for _ in 0..2 {
        if limiter.allow_request() {
            allowed += 1;
        }
    }
    assert_eq!(allowed, 2, "Expected exactly 2 tokens to be refilled");
}

#[test]
fn test_distributed_consumption() {
    let config = Config {
        capacity: 10,
        refill_rate: 2.0, // 2 tokens per second
    };
    let mut cluster = Cluster::new(3, config);
    
    // Simulate requests for multiple clients.
    let clients = vec!["client_a", "client_b", "client_c"];
    for client in clients.iter() {
        // Consume tokens until the limit is reached.
        for _ in 0..10 {
            let allowed = cluster.route_request(client);
            assert!(allowed, "Expected request from {} to be allowed", client);
        }
        // Next request should be rejected as the token bucket is empty.
        let allowed = cluster.route_request(client);
        assert!(!allowed, "Expected request from {} to be rejected after bucket depletes", client);
    }
}

#[test]
fn test_node_failure() {
    let config = Config {
        capacity: 5,
        refill_rate: 1.0,
    };
    let mut cluster = Cluster::new(2, config);
    
    // Verify that a request is allowed before any failure.
    assert!(cluster.route_request("client_fail"), "Expected initial request to be allowed");

    // Simulate node failure.
    cluster.kill_node(0);
    
    // After failure, requests should be handled by the remaining node(s).
    let allowed_after_failure = cluster.route_request("client_fail");
    assert!(allowed_after_failure, "Expected request to be allowed after node failure");

    // Recover node and test again.
    cluster.recover_node(0);
    assert!(cluster.route_request("client_fail"), "Expected request to be allowed after node recovery");
}

#[test]
fn test_concurrent_requests() {
    let config = Config {
        capacity: 20,
        refill_rate: 5.0,
    };
    let limiter = Arc::new(RateLimiter::new("client_concurrent".to_string(), config));
    let barrier = Arc::new(Barrier::new(10));
    let success_counter = Arc::new(AtomicUsize::new(0));

    let mut handles = vec![];

    // Spawn 10 threads concurrently issuing requests.
    for _ in 0..10 {
        let limiter_clone = Arc::clone(&limiter);
        let barrier_clone = Arc::clone(&barrier);
        let counter_clone = Arc::clone(&success_counter);
        let handle = thread::spawn(move || {
            // Wait until all threads are ready.
            barrier_clone.wait();
            for _ in 0..5 {
                if limiter_clone.allow_request() {
                    counter_clone.fetch_add(1, Ordering::SeqCst);
                }
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    let total_allowed = success_counter.load(Ordering::SeqCst);
    // The total number of allowed requests should not exceed the bucket capacity.
    assert!(total_allowed <= 20, "Expected at most 20 allowed requests, got {}", total_allowed);
}