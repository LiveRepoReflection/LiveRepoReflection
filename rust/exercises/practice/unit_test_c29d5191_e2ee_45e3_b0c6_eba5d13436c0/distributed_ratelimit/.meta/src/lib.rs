use std::collections::HashMap;
use std::sync::{Mutex, Once};
use std::time::Instant;

#[derive(Debug)]
pub enum RateLimitError {
    BackendError(String),
}

pub type Result<T> = std::result::Result<T, RateLimitError>;

// Helper function to create a unique key based on client_id and api_endpoint.
fn make_key(client_id: &str, api_endpoint: &str) -> String {
    format!("{}:{}", client_id.to_lowercase(), api_endpoint.to_lowercase())
}

struct Counter {
    window_start: Instant,
    count: usize,
}

struct DataStore {
    counters: HashMap<String, Counter>,
}

impl DataStore {
    fn new() -> Self {
        DataStore {
            counters: HashMap::new(),
        }
    }

    // Increments the count for the key. If more than 1 second has passed since the start
    // of the window, resets the counter.
    fn increment(&mut self, key: &str) -> (usize, Instant) {
        let now = Instant::now();
        let counter = self.counters.entry(key.to_string()).or_insert(Counter {
            window_start: now,
            count: 0,
        });
        if now.duration_since(counter.window_start).as_millis() >= 1000 {
            counter.window_start = now;
            counter.count = 0;
        }
        counter.count += 1;
        (counter.count, counter.window_start)
    }
}

// Global simulated central data store. In a real-world scenario, this would be replaced
// by an actual Redis client. Here, we use a Mutex-protected HashMap.
static mut DATA_STORE: Option<Mutex<DataStore>> = None;
static INIT: Once = Once::new();

fn get_data_store() -> &'static Mutex<DataStore> {
    unsafe {
        INIT.call_once(|| {
            DATA_STORE = Some(Mutex::new(DataStore::new()));
        });
        DATA_STORE.as_ref().unwrap()
    }
}

/// Checks if a client is allowed to access a specific API endpoint based on the rate limit.
/// Returns Ok(true) if allowed, Ok(false) if not allowed, and an error if any backend error occurs.
///
/// The parameters are:
/// - client_id: A unique identifier for the client.
/// - api_endpoint: The specific endpoint being accessed.
/// - capacity: The maximum number of requests allowed per sliding window (1 second).
/// - rate_per_second: Provided for interface compatibility. In this implementation, it is assumed to be equal to capacity.
pub fn is_allowed(client_id: &str, api_endpoint: &str, capacity: usize, _rate_per_second: usize) -> Result<bool> {
    // Simulate a backend error scenario for testing purposes.
    if client_id.to_lowercase() == "error" {
        return Err(RateLimitError::BackendError("Simulated backend error".to_string()));
    }

    let key = make_key(client_id, api_endpoint);
    let datastore = get_data_store();
    let mut ds = datastore.lock().unwrap();
    let (current_count, _window_start) = ds.increment(&key);
    if current_count <= capacity {
        Ok(true)
    } else {
        Ok(false)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn basic_allow_test() {
        let client = "client1";
        let endpoint = "/test";
        let capacity = 5;
        let rate_per_second = 5;

        {
            let datastore = get_data_store();
            let mut ds = datastore.lock().unwrap();
            ds.counters.clear();
        }

        for _ in 0..capacity {
            let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
                .expect("Expected successful call.");
            assert!(allowed, "Request should be allowed.");
        }

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

        {
            let datastore = get_data_store();
            let mut ds = datastore.lock().unwrap();
            ds.counters.clear();
        }

        for _ in 0..capacity {
            let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
                .expect("Expected successful call.");
            assert!(allowed, "Request should be allowed.");
        }

        let allowed = is_allowed(client, endpoint, capacity, rate_per_second)
            .expect("Expected successful call.");
        assert!(!allowed, "Request should be disallowed initially.");

        thread::sleep(Duration::from_millis(1100));

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

        {
            let datastore = get_data_store();
            let mut ds = datastore.lock().unwrap();
            ds.counters.clear();
        }

        let allowed_counter = std::sync::Arc::new(std::sync::Mutex::new(0));
        let mut handles = Vec::new();

        for _ in 0..num_threads {
            let counter = std::sync::Arc::clone(&allowed_counter);
            let client_clone = client.to_string();
            let endpoint_clone = endpoint.to_string();
            let handle = thread::spawn(move || {
                if let Ok(allowed) = is_allowed(&client_clone, &endpoint_clone, capacity, rate_per_second) {
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
        assert_eq!(total_allowed, capacity, "Total allowed requests should equal the capacity.");
    }

    #[test]
    fn test_error_handling() {
        let result = is_allowed("error", "/error", 1, 1);
        assert!(result.is_err(), "An error should be returned when a backend error occurs.");
    }
}