use distributed_median::*;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;
use rand::{Rng, thread_rng};

#[test]
fn test_empty_median() {
    let aggregator = MedianAggregator::new(3, 0.01).unwrap();
    
    assert!(aggregator.get_median().is_err());
}

#[test]
fn test_single_value() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    aggregator.update(0, 42).unwrap();
    
    assert_eq!(aggregator.get_median().unwrap(), 42.0);
}

#[test]
fn test_simple_median() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    aggregator.update(0, 10).unwrap();
    aggregator.update(0, 20).unwrap();
    aggregator.update(0, 30).unwrap();
    
    assert_eq!(aggregator.get_median().unwrap(), 20.0);
}

#[test]
fn test_even_number_of_elements() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    aggregator.update(0, 10).unwrap();
    aggregator.update(0, 20).unwrap();
    aggregator.update(0, 30).unwrap();
    aggregator.update(0, 40).unwrap();
    
    // Median of [10, 20, 30, 40] is (20 + 30) / 2 = 25
    assert_eq!(aggregator.get_median().unwrap(), 25.0);
}

#[test]
fn test_duplicate_values() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    aggregator.update(0, 10).unwrap();
    aggregator.update(0, 20).unwrap();
    aggregator.update(0, 20).unwrap();  // Duplicate
    aggregator.update(0, 30).unwrap();
    
    // Median of [10, 20, 20, 30] is (20 + 20) / 2 = 20
    assert_eq!(aggregator.get_median().unwrap(), 20.0);
}

#[test]
fn test_multiple_workers() {
    let aggregator = MedianAggregator::new(3, 0.01).unwrap();
    
    aggregator.update(0, 10).unwrap();
    aggregator.update(1, 20).unwrap();
    aggregator.update(2, 30).unwrap();
    aggregator.update(0, 40).unwrap();
    aggregator.update(1, 50).unwrap();
    
    // Median of [10, 20, 30, 40, 50] is 30
    assert_eq!(aggregator.get_median().unwrap(), 30.0);
}

#[test]
fn test_invalid_worker_id() {
    let aggregator = MedianAggregator::new(2, 0.01).unwrap();
    
    assert!(aggregator.update(2, 10).is_err());  // Worker ID 2 is out of range
}

#[test]
fn test_concurrent_updates() {
    let num_workers = 4;
    let aggregator = Arc::new(MedianAggregator::new(num_workers, 0.01).unwrap());
    let barrier = Arc::new(Barrier::new(num_workers));
    let values_per_worker = 1000;
    
    let mut handles = vec![];
    
    for worker_id in 0..num_workers {
        let aggregator_clone = Arc::clone(&aggregator);
        let barrier_clone = Arc::clone(&barrier);
        
        let handle = thread::spawn(move || {
            let mut rng = thread_rng();
            
            // Wait for all threads to be ready
            barrier_clone.wait();
            
            for _ in 0..values_per_worker {
                let value = rng.gen_range(1..10000);
                aggregator_clone.update(worker_id, value).unwrap();
            }
        });
        
        handles.push(handle);
    }
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Just verify we can get a median after concurrent updates
    assert!(aggregator.get_median().is_ok());
}

#[test]
fn test_approximation_error() {
    // This test verifies the approximation error guarantee
    // Since our implementation might use approximate data structures,
    // we'll need to test that the approximation error is within bounds
    
    let error_rate = 0.05; // 5% error allowed
    let aggregator = MedianAggregator::new(1, error_rate).unwrap();
    
    // Insert a sorted sequence of 1000 values
    let n = 1000;
    for i in 0..n {
        aggregator.update(0, i).unwrap();
    }
    
    // The true median is (n-1)/2 for odd number of elements
    let true_median = (n - 1) as f64 / 2.0;
    let approx_median = aggregator.get_median().unwrap();
    
    // Calculate the maximum allowed error
    let max_allowed_error = error_rate * (n - 1) as f64;
    let actual_error = (approx_median - true_median).abs();
    
    assert!(actual_error <= max_allowed_error, 
            "Error {} exceeds maximum allowed error {}", actual_error, max_allowed_error);
}

#[test]
fn test_large_values() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    aggregator.update(0, u64::MAX / 2).unwrap();
    aggregator.update(0, u64::MAX / 4).unwrap();
    aggregator.update(0, u64::MAX / 3).unwrap();
    
    // The median should be u64::MAX / 3
    assert_eq!(aggregator.get_median().unwrap(), (u64::MAX / 3) as f64);
}

#[test]
fn test_dynamic_median_updates() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    // Test that the median updates correctly as we add values
    aggregator.update(0, 10).unwrap();
    assert_eq!(aggregator.get_median().unwrap(), 10.0);
    
    aggregator.update(0, 20).unwrap();
    assert_eq!(aggregator.get_median().unwrap(), 15.0);
    
    aggregator.update(0, 15).unwrap();
    assert_eq!(aggregator.get_median().unwrap(), 15.0);
    
    aggregator.update(0, 5).unwrap();
    assert_eq!(aggregator.get_median().unwrap(), 12.5);
}

#[test]
fn test_edge_cases() {
    // Test creating with zero workers
    assert!(MedianAggregator::new(0, 0.01).is_err());
    
    // Test with invalid error rate
    assert!(MedianAggregator::new(1, -0.01).is_err());
    assert!(MedianAggregator::new(1, 1.5).is_err());
}

#[test]
fn test_stress_test() {
    let num_workers = 8;
    let aggregator = Arc::new(MedianAggregator::new(num_workers, 0.01).unwrap());
    let barrier = Arc::new(Barrier::new(num_workers + 1)); // +1 for the main thread
    let updates_per_worker = 5000;
    
    let mut handles = vec![];
    
    for worker_id in 0..num_workers {
        let aggregator_clone = Arc::clone(&aggregator);
        let barrier_clone = Arc::clone(&barrier);
        
        let handle = thread::spawn(move || {
            let mut rng = thread_rng();
            
            // Wait for all threads to be ready
            barrier_clone.wait();
            
            for _ in 0..updates_per_worker {
                let value = rng.gen_range(1..100000);
                aggregator_clone.update(worker_id, value).unwrap();
                
                // Small sleep to simulate real-world conditions
                if rng.gen_bool(0.01) {
                    thread::sleep(Duration::from_micros(1));
                }
            }
        });
        
        handles.push(handle);
    }
    
    // Wait for all worker threads to start
    barrier.wait();
    
    // Periodically get the median while updates are happening
    for _ in 0..20 {
        thread::sleep(Duration::from_millis(10));
        let _ = aggregator.get_median(); // Just make sure it doesn't panic
    }
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Make sure we can still get a median after all that stress
    assert!(aggregator.get_median().is_ok());
}

#[test]
fn test_memory_usage_over_time() {
    let aggregator = MedianAggregator::new(1, 0.01).unwrap();
    
    // Insert a large number of values
    let base: u64 = 10;
    for i in 0..10000 {
        aggregator.update(0, base.pow(i % 10)).unwrap();
    }
    
    // Just make sure it completes - a bad implementation would
    // run out of memory or become extremely slow
    assert!(aggregator.get_median().is_ok());
}