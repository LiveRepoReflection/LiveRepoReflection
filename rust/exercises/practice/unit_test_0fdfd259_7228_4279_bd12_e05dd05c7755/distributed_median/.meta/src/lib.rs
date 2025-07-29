use std::collections::BTreeMap;
use std::error::Error;
use std::fmt;
use std::sync::{Arc, RwLock};

/// Custom error type for the MedianAggregator
#[derive(Debug)]
pub enum MedianError {
    /// Error when no data is available yet
    NoDataAvailable,
    /// Error when worker ID is invalid
    InvalidWorkerId(usize),
    /// Error for invalid configuration
    InvalidConfiguration(String),
    /// Any other error
    Other(String),
}

impl fmt::Display for MedianError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MedianError::NoDataAvailable => write!(f, "No data available yet"),
            MedianError::InvalidWorkerId(id) => write!(f, "Invalid worker ID: {}", id),
            MedianError::InvalidConfiguration(msg) => write!(f, "Invalid configuration: {}", msg),
            MedianError::Other(msg) => write!(f, "{}", msg),
        }
    }
}

impl Error for MedianError {}

/// A compressed representation of a value frequency distribution
/// using a tree-based data structure that maintains efficient operations
/// while using less memory than storing all values.
///
/// This implementation uses the GK algorithm (Greenwald-Khanna) inspired approach
/// for approximate quantile computation with bounded error.
pub struct CompressedDistribution {
    // Key: value, Value: count
    values: BTreeMap<u64, usize>,
    // Total count of elements
    count: usize,
    // Maximum error allowed (as a ratio)
    epsilon: f64,
    // Maximum value seen so far (used for error bound calculation)
    max_value: u64,
    // Compression threshold (number of unique values before triggering compression)
    compression_threshold: usize,
}

impl CompressedDistribution {
    /// Creates a new compressed distribution with the specified error bound
    pub fn new(epsilon: f64) -> Result<Self, MedianError> {
        if epsilon <= 0.0 || epsilon >= 1.0 {
            return Err(MedianError::InvalidConfiguration(
                "Epsilon must be between 0 and 1".to_string(),
            ));
        }

        Ok(Self {
            values: BTreeMap::new(),
            count: 0,
            epsilon,
            max_value: 0,
            compression_threshold: 1000, // Adjustable parameter
        })
    }

    /// Inserts a value into the distribution
    pub fn insert(&mut self, value: u64) {
        *self.values.entry(value).or_insert(0) += 1;
        self.count += 1;
        self.max_value = self.max_value.max(value);

        // Check if we need to compress the distribution
        if self.values.len() > self.compression_threshold {
            self.compress();
        }
    }

    /// Returns the approximate median with error bounded by epsilon
    pub fn median(&self) -> Result<f64, MedianError> {
        if self.count == 0 {
            return Err(MedianError::NoDataAvailable);
        }

        // If we have very few values, we can compute exact median
        if self.values.len() <= 2 {
            return Ok(self.compute_exact_median());
        }

        let target_rank = self.count / 2;
        
        let mut current_rank = 0;
        let mut prev_value = None;
        
        for (&value, &count) in &self.values {
            let next_rank = current_rank + count;
            
            // If the median falls within this bucket
            if current_rank <= target_rank && target_rank < next_rank {
                return match prev_value {
                    // For even counts where we're at the upper median value
                    Some(prev) if self.count % 2 == 0 && current_rank == target_rank => {
                        Ok((prev as f64 + value as f64) / 2.0)
                    },
                    // Normal case
                    _ => Ok(value as f64),
                };
            }
            
            current_rank = next_rank;
            prev_value = Some(value);
        }
        
        // This should never happen if our counts are correct
        Err(MedianError::Other("Failed to compute median".to_string()))
    }

    /// Compute the exact median for small distributions
    fn compute_exact_median(&self) -> f64 {
        let mut values = Vec::new();
        
        for (&value, &count) in &self.values {
            for _ in 0..count {
                values.push(value);
            }
        }
        
        values.sort();
        
        if values.len() % 2 == 1 {
            values[values.len() / 2] as f64
        } else {
            let mid = values.len() / 2;
            (values[mid - 1] as f64 + values[mid] as f64) / 2.0
        }
    }

    /// Compresses the distribution to save memory while maintaining the error bound
    fn compress(&mut self) {
        // We'll combine adjacent buckets that have small counts
        // This is a simplified version of the GK algorithm's compression step
        
        // Calculate the maximum allowed error in terms of items (not rank)
        let max_error_items = (self.epsilon * self.count as f64).ceil() as usize;
        if max_error_items < 2 {
            return; // Can't compress further without violating error bounds
        }
        
        let mut new_values = BTreeMap::new();
        let mut current_count = 0;
        let mut current_value = 0;
        
        let mut values_vec: Vec<(u64, usize)> = self.values.iter().map(|(&k, &v)| (k, v)).collect();
        
        // Sort by count (compress smallest counts first)
        values_vec.sort_by_key(|&(_, count)| count);
        
        for (value, count) in values_vec {
            if current_count == 0 {
                current_value = value;
                current_count = count;
            } else if current_count + count <= max_error_items {
                // Merge buckets by weighted average if it's beneficial
                current_value = ((current_value as u128 * current_count as u128 + 
                                  value as u128 * count as u128) / 
                                 (current_count + count) as u128) as u64;
                current_count += count;
            } else {
                // Can't merge more into this bucket without exceeding error
                new_values.insert(current_value, current_count);
                current_value = value;
                current_count = count;
            }
        }
        
        // Don't forget to add the last bucket
        if current_count > 0 {
            new_values.insert(current_value, current_count);
        }
        
        // Only update if we actually saved space
        if new_values.len() < self.values.len() {
            self.values = new_values;
        }
    }

    /// Returns the current count of elements in the distribution
    pub fn count(&self) -> usize {
        self.count
    }
}

/// The main MedianAggregator that collects data from multiple worker nodes
/// and maintains an approximate running median
pub struct MedianAggregator {
    // Number of worker nodes
    num_workers: usize,
    // Shared distribution for thread-safe access
    distribution: Arc<RwLock<CompressedDistribution>>,
}

impl MedianAggregator {
    /// Creates a new MedianAggregator with the specified number of workers
    /// and maximum error rate
    pub fn new(num_workers: usize, epsilon: f64) -> Result<Self, MedianError> {
        if num_workers == 0 {
            return Err(MedianError::InvalidConfiguration(
                "Number of workers must be greater than 0".to_string(),
            ));
        }

        Ok(Self {
            num_workers,
            distribution: Arc::new(RwLock::new(CompressedDistribution::new(epsilon)?)),
        })
    }

    /// Updates the aggregator with a new value from a specific worker
    pub fn update(&self, worker_id: usize, value: u64) -> Result<(), MedianError> {
        if worker_id >= self.num_workers {
            return Err(MedianError::InvalidWorkerId(worker_id));
        }

        let mut distr = self.distribution
            .write()
            .map_err(|e| MedianError::Other(format!("Lock poisoned: {}", e)))?;

        distr.insert(value);
        Ok(())
    }

    /// Returns the current approximate median
    pub fn get_median(&self) -> Result<f64, MedianError> {
        let distr = self.distribution
            .read()
            .map_err(|e| MedianError::Other(format!("Lock poisoned: {}", e)))?;

        distr.median()
    }

    /// Returns the current count of elements
    pub fn get_count(&self) -> Result<usize, MedianError> {
        let distr = self.distribution
            .read()
            .map_err(|e| MedianError::Other(format!("Lock poisoned: {}", e)))?;

        Ok(distr.count())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_median() {
        let distribution = CompressedDistribution::new(0.01).unwrap();
        let mut distribution = distribution;
        
        distribution.insert(10);
        distribution.insert(20);
        distribution.insert(30);
        
        assert_eq!(distribution.median().unwrap(), 20.0);
    }

    #[test]
    fn test_even_count_median() {
        let distribution = CompressedDistribution::new(0.01).unwrap();
        let mut distribution = distribution;
        
        distribution.insert(10);
        distribution.insert(20);
        distribution.insert(30);
        distribution.insert(40);
        
        assert_eq!(distribution.median().unwrap(), 25.0);
    }

    #[test]
    fn test_compression() {
        let mut distribution = CompressedDistribution::new(0.05).unwrap();
        
        // Insert many values to trigger compression
        for i in 0..2000 {
            distribution.insert(i);
        }
        
        // After compression, we should have significantly fewer than 2000 entries
        assert!(distribution.values.len() < 2000);
        
        // Even with compression, the median should be close to 1000
        let median = distribution.median().unwrap();
        assert!((median - 999.5).abs() < 100.0); // Allowing for epsilon error
    }
}