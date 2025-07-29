#[cfg(test)]
mod tests {
    use std::sync::{Arc, Mutex};
    use std::thread;
    use std::time::{Duration, Instant};

    // Assuming the existence of a `distributed_ratelimit` module exposing an `is_allowed` function.
    use distributed_ratelimit::is_allowed;

    #[test]
    fn basic_allow_test() {
        let client = "client1";
        let endpoint = "/test";
        let capacity = 5;
        let rate_per_second = 5;

        // The first 'capacity' requests should be allowed.
        for _ in 0..capacity {
            let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
                .expect("Expected successful call.");
            assert!(allowed, "Request should be allowed.");
        }

        // Next request should be disallowed.
        let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
            .expect("Expected successful call.");
        assert!(!allowed, "Request should be disallowed as capacity is reached.");
    }

    #[test]
    fn sliding_window_test() {
        let client = "client2";
        let endpoint = "/test";
        let capacity = 3;
        let rate_per_second = 3;

        // Consume the quota.
        for _ in 0..capacity {
            let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
                .expect("Expected successful call.");
            assert!(allowed, "Request should be allowed.");
        }

        // Next request should be disallowed.
        let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
            .expect("Expected successful call.");
        assert!(!allowed, "Request should be disallowed initially.");

        // Wait for more than one second to allow the sliding window to reset.
        thread::sleep(Duration::from_millis(1100));

        // Now, requests should be allowed again.
        for _ in 0..capacity {
            let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
                .expect("Expected successful call after window reset.");
            assert!(allowed, "Request should be allowed after window reset.");
        }
    }

    #[test]
    fn concurrent_requests_test() {
        let client = "client3";
        let endpoint = "/test";
        let capacity = 10;
        let rate_per_second = 10;
        let num_threads = 20;

        // Use a synchronized counter to count the number of allowed requests.
        let allowed_counter = Arc::new(Mutex::new(0));

        let mut handles = Vec::new();

        for _ in 0..num_threads {
            let counter = Arc::clone(&allowed_counter);
            let client = client.to_string();
            let endpoint = endpoint.to_string();
            let handle = thread::spawn(move || {
                if let Ok(allowed) = is_allowed(&client, &endpoint, capacity, rate_per_second) {
                    if allowed {
                        let mut num = counter.lock().unwrap();
                        *num += 1;
                    }
                }
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().expect("Thread panicked.");
        }

        let total_allowed = *allowed_counter.lock().unwrap();
        // The total number of allowed requests should not exceed the capacity.
        assert_eq!(total_allowed, capacity, "Total allowed requests should equal the capacity.");
    }

    #[test]
    fn test_error_handling() {
        // This test assumes that, for instance, when a client id equals "error",
        // the function simulates an error scenario (e.g., a back-end failure).
        let result = is_allowed("error", "/error", 1, 1);
        assert!(result.is_err(), "An error should be returned when a backend error occurs.");
    }
}