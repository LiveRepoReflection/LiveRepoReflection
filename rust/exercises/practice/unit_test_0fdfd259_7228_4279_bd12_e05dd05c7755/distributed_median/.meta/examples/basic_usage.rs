use distributed_median::MedianAggregator;
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use rand::{Rng, thread_rng};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a new aggregator with 4 workers and 1% maximum error
    let aggregator = Arc::new(MedianAggregator::new(4, 0.01)?);
    
    // Create worker threads
    let mut handles = vec![];
    
    for worker_id in 0..4 {
        let agg = Arc::clone(&aggregator);
        
        let handle = thread::spawn(move || {
            let mut rng = thread_rng();
            
            for i in 0..1000 {
                // Generate a random value - using different ranges for different workers
                // to better visualize the effect
                let value = match worker_id {
                    0 => rng.gen_range(1..100),
                    1 => rng.gen_range(100..1000),
                    2 => rng.gen_range(1000..5000),
                    _ => rng.gen_range(5000..10000),
                };
                
                // Update the aggregator
                if let Err(e) = agg.update(worker_id, value) {
                    eprintln!("Error updating aggregator: {}", e);
                }
                
                // Sleep briefly to simulate real-world conditions
                if i % 100 == 0 {
                    thread::sleep(Duration::from_millis(10));
                }
            }
        });
        
        handles.push(handle);
    }
    
    // Periodically print the current median
    for i in 0..20 {
        thread::sleep(Duration::from_millis(200));
        
        match aggregator.get_median() {
            Ok(median) => println!("Current median at step {}: {:.2}", i, median),
            Err(e) => println!("Couldn't get median: {}", e),
        }
        
        // Also print the count
        match aggregator.get_count() {
            Ok(count) => println!("Current count: {}", count),
            Err(e) => println!("Couldn't get count: {}", e),
        }
    }
    
    // Wait for all workers to finish
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Print final median
    println!("Final median: {:.2}", aggregator.get_median()?);
    println!("Final count: {}", aggregator.get_count()?);
    
    Ok(())
}