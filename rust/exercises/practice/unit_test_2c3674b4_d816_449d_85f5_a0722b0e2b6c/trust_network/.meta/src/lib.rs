use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;
use std::sync::{Arc, RwLock};

// Node for Dijkstra's algorithm with modified priority for maximum trust
#[derive(Copy, Clone, Eq, PartialEq)]
struct TrustNode {
    user_id: u32,
    trust_value: u64, // Using u64 to represent f64 for comparing in BinaryHeap
}

// Custom ordering for BinaryHeap to create a max-heap based on trust values
impl Ord for TrustNode {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse order for max-heap (highest trust first)
        self.trust_value.cmp(&other.trust_value)
    }
}

impl PartialOrd for TrustNode {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Convert between f64 trust scores and u64 for comparison in BinaryHeap
// This preserves 4 decimal places of precision as required
fn f64_to_u64(value: f64) -> u64 {
    (value * 10000.0).round() as u64
}

fn u64_to_f64(value: u64) -> f64 {
    value as f64 / 10000.0
}

// Core graph structure to represent the trust network
#[derive(Debug, Clone, Default)]
pub struct TrustNetwork {
    // For each user, store a map of trusted users and their trust scores
    adjacency_list: HashMap<u32, HashMap<u32, f64>>,
}

impl TrustNetwork {
    pub fn new() -> Self {
        Self {
            adjacency_list: HashMap::new(),
        }
    }
    
    pub fn add_trust_assertion(&mut self, from: u32, to: u32, trust_score: Option<f64>) {
        if let Some(score) = trust_score {
            // Validate trust score
            if score < 0.0 || score > 1.0 {
                return;
            }
            
            // Add or update the trust assertion
            self.adjacency_list
                .entry(from)
                .or_insert_with(HashMap::new)
                .insert(to, score);
        } else {
            // Remove the trust assertion if it exists
            if let Some(edges) = self.adjacency_list.get_mut(&from) {
                edges.remove(&to);
                // Clean up empty maps
                if edges.is_empty() {
                    self.adjacency_list.remove(&from);
                }
            }
        }
    }
    
    pub fn highest_trust_path(&self, source: u32, destination: u32) -> f64 {
        // Special case: trust to self is always 1.0
        if source == destination {
            return 1.0;
        }
        
        // Implementation of a modified Dijkstra's algorithm
        // that finds the path with the highest minimum trust value
        
        // Max trust value seen so far for each node
        let mut max_trust: HashMap<u32, f64> = HashMap::new();
        
        // Priority queue for processing nodes
        // We use BinaryHeap as a max-heap (highest trust first)
        let mut priority_queue = BinaryHeap::new();
        
        // Initialize source node with trust 1.0 (max possible)
        max_trust.insert(source, 1.0);
        priority_queue.push(TrustNode {
            user_id: source,
            trust_value: f64_to_u64(1.0),
        });
        
        // Process nodes until queue is empty
        while let Some(TrustNode { user_id, trust_value }) = priority_queue.pop() {
            let current_trust = u64_to_f64(trust_value);
            
            // If we reached destination, return the trust value
            if user_id == destination {
                return current_trust;
            }
            
            // Skip if we already found a better path
            if let Some(&best_trust) = max_trust.get(&user_id) {
                if best_trust > current_trust {
                    continue;
                }
            }
            
            // Process all neighbors
            if let Some(neighbors) = self.adjacency_list.get(&user_id) {
                for (&neighbor, &edge_trust) in neighbors {
                    // Calculate new trust value (minimum of current path and this edge)
                    let new_trust = current_trust.min(edge_trust);
                    
                    // Update if this path has higher trust
                    let should_update = match max_trust.get(&neighbor) {
                        Some(&existing_trust) => new_trust > existing_trust,
                        None => true,
                    };
                    
                    if should_update {
                        max_trust.insert(neighbor, new_trust);
                        priority_queue.push(TrustNode {
                            user_id: neighbor,
                            trust_value: f64_to_u64(new_trust),
                        });
                    }
                }
            }
        }
        
        // No path exists
        0.0
    }
}

// Thread-safe version using RwLock
pub struct ConcurrentTrustNetwork {
    network: Arc<RwLock<TrustNetwork>>,
}

impl ConcurrentTrustNetwork {
    pub fn new() -> Self {
        Self {
            network: Arc::new(RwLock::new(TrustNetwork::new())),
        }
    }
    
    pub fn add_trust_assertion(&self, from: u32, to: u32, trust_score: Option<f64>) {
        // Get write lock to update the network
        if let Ok(mut network) = self.network.write() {
            network.add_trust_assertion(from, to, trust_score);
        }
    }
    
    pub fn highest_trust_path(&self, source: u32, destination: u32) -> f64 {
        // Get read lock to query the network
        if let Ok(network) = self.network.read() {
            network.highest_trust_path(source, destination)
        } else {
            // Return 0.0 if lock acquisition fails
            0.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_path() {
        let mut network = TrustNetwork::new();
        network.add_trust_assertion(1, 2, Some(0.8));
        network.add_trust_assertion(2, 3, Some(0.9));
        network.add_trust_assertion(1, 3, Some(0.5));
        
        assert_eq!(network.highest_trust_path(1, 3), 0.8);
    }

    #[test]
    fn test_remove_assertion() {
        let mut network = TrustNetwork::new();
        network.add_trust_assertion(1, 2, Some(0.8));
        network.add_trust_assertion(2, 3, Some(0.9));
        network.add_trust_assertion(1, 3, Some(0.5));
        
        assert_eq!(network.highest_trust_path(1, 3), 0.8);
        
        network.add_trust_assertion(2, 3, None);
        assert_eq!(network.highest_trust_path(1, 3), 0.5);
    }
    
    #[test]
    fn test_no_path() {
        let mut network = TrustNetwork::new();
        network.add_trust_assertion(1, 2, Some(0.8));
        network.add_trust_assertion(3, 4, Some(0.9));
        
        assert_eq!(network.highest_trust_path(1, 4), 0.0);
        assert_eq!(network.highest_trust_path(1, 3), 0.0);
    }
    
    #[test]
    fn test_self_path() {
        let mut network = TrustNetwork::new();
        network.add_trust_assertion(1, 2, Some(0.8));
        
        assert_eq!(network.highest_trust_path(1, 1), 1.0);
    }
    
    #[test]
    fn test_float_precision() {
        let mut network = TrustNetwork::new();
        network.add_trust_assertion(1, 2, Some(0.8123));
        network.add_trust_assertion(2, 3, Some(0.8124));
        
        let result = network.highest_trust_path(1, 3);
        assert!((result - 0.8123).abs() < 0.0001);
    }
}