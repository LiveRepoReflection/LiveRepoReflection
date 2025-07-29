use std::sync::{Arc, Mutex};
use std::thread;
use dist_median::{Coordinator, Worker};

#[test]
fn test_empty_coordinator() {
    let mut coordinator = Coordinator::new();
    // When no numbers have been added, the median should be None.
    assert!(coordinator.get_median().is_none());
}

#[test]
fn test_single_worker_odd() {
    let coordinator = Arc::new(Mutex::new(Coordinator::new()));
    let worker = Worker::new(1, Arc::clone(&coordinator));
    
    // Submit an odd number of values: [3, 1, 4]
    worker.submit(3);
    worker.submit(1);
    worker.submit(4);
    
    // Sorted order: [1, 3, 4] => median is 3
    let median = coordinator.lock().unwrap().get_median().unwrap();
    assert_eq!(median, 3.0);
}

#[test]
fn test_single_worker_even() {
    let coordinator = Arc::new(Mutex::new(Coordinator::new()));
    let worker = Worker::new(1, Arc::clone(&coordinator));
    
    // Submit an even number of values: [1, 3]
    worker.submit(1);
    worker.submit(3);
    
    // Median = (1 + 3) / 2 = 2.0
    let median = coordinator.lock().unwrap().get_median().unwrap();
    assert_eq!(median, 2.0);
}

#[test]
fn test_multiple_workers() {
    let coordinator = Arc::new(Mutex::new(Coordinator::new()));
    let worker1 = Worker::new(1, Arc::clone(&coordinator));
    let worker2 = Worker::new(2, Arc::clone(&coordinator));
    
    // Worker 1 submits: [10, 20, 30]
    worker1.submit(10);
    worker1.submit(20);
    worker1.submit(30);
    
    // Worker 2 submits: [5, 15, 25]
    worker2.submit(5);
    worker2.submit(15);
    worker2.submit(25);
    
    // Combined sorted: [5, 10, 15, 20, 25, 30] => median = (15 + 20) / 2 = 17.5
    let median = coordinator.lock().unwrap().get_median().unwrap();
    assert_eq!(median, 17.5);
}

#[test]
fn test_concurrent_updates() {
    let coordinator = Arc::new(Mutex::new(Coordinator::new()));
    let mut handles = Vec::new();

    // Spawn 4 threads simulating 4 worker nodes.
    // Each worker submits a contiguous block of 100 numbers.
    // Thread 0: 1-100, Thread 1: 101-200, Thread 2: 201-300, Thread 3: 301-400.
    for i in 0..4 {
        let coordinator_clone = Arc::clone(&coordinator);
        let start = i * 100 + 1;
        let end = i * 100 + 100;
        let handle = thread::spawn(move || {
            let worker = Worker::new(i as u64, Arc::clone(&coordinator_clone));
            for num in start..=end {
                worker.submit(num);
            }
        });
        handles.push(handle);
    }
    
    // Wait for all threads to complete.
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Total numbers are 1 to 400.
    // The median is the average of the 200th and 201st numbers: (200 + 201) / 2 = 200.5.
    let median = coordinator.lock().unwrap().get_median().unwrap();
    assert_eq!(median, 200.5);
}

#[test]
fn test_large_input_sequential() {
    let mut coordinator = Coordinator::new();
    
    // Simulate a single worker submitting a large sequence: 1 to 1000.
    for i in 1..=1000 {
        coordinator.update(0, i);
    }
    
    // For 1 to 1000, median = (500 + 501) / 2 = 500.5.
    let median = coordinator.get_median().unwrap();
    assert_eq!(median, 500.5);
}