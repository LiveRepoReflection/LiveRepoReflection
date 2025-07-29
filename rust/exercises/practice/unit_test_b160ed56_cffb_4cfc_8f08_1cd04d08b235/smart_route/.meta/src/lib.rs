use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;

// Type aliases to make the code more readable
pub type RouterID = i32;
pub type Capacity = f64;
pub type Utilization = f64;
pub type Network = HashMap<RouterID, Vec<(RouterID, Capacity, Utilization)>>;

// Helper struct for the Dijkstra algorithm
#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u64, // Cost represented as microseconds for better precision
    router: RouterID,
    previous: RouterID,
}

// Custom ordering for the priority queue
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost) // Reversed for min-heap
            .then_with(|| self.router.cmp(&other.router))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Calculate transmission time for a link, including congestion penalty
fn calculate_transmission_time(capacity: Capacity, utilization: Utilization, data_size: f64) -> f64 {
    let available_bandwidth = capacity - utilization;
    
    if available_bandwidth <= 0.0 {
        // Infinite cost for fully congested links
        return f64::INFINITY;
    }
    
    let base_time = data_size / available_bandwidth;
    
    // Apply congestion penalty - more severe as utilization approaches capacity
    let congestion_factor = 1.0 + (utilization / capacity).powi(3) * 10.0;
    
    base_time * congestion_factor
}

// Convert floating point time to integer microseconds for priority queue
fn time_to_microseconds(time: f64) -> u64 {
    if time.is_infinite() {
        u64::MAX
    } else {
        (time * 1_000_000.0) as u64
    }
}

/// Find the optimal route from source to destination that minimizes transmission time
/// 
/// # Arguments
/// * `network` - A network represented as an adjacency list
/// * `source` - The source router ID
/// * `destination` - The destination router ID
/// * `data_size` - The size of the data to be transmitted
/// * `simulate_network_updates` - A function that simulates network traffic changes
/// 
/// # Returns
/// A vector of router IDs representing the optimal route, or an empty vector if no route exists
pub fn find_optimal_route<F>(
    network: Network,
    source: RouterID,
    destination: RouterID,
    data_size: f64,
    simulate_network_updates: F,
) -> Vec<RouterID>
where
    F: Fn(Network) -> Network,
{
    // First, simulate network updates
    let updated_network = simulate_network_updates(network);
    
    // Check if source and destination exist
    if !updated_network.contains_key(&source) || !updated_network.contains_key(&destination) {
        return Vec::new();
    }
    
    // Early exit if source and destination are the same
    if source == destination {
        return vec![source];
    }
    
    // Set up data structures for Dijkstra's algorithm
    let mut heap = BinaryHeap::new();
    let mut costs: HashMap<RouterID, u64> = HashMap::new();
    let mut predecessors: HashMap<RouterID, RouterID> = HashMap::new();
    let mut visited: HashSet<RouterID> = HashSet::new();
    
    // Initialize with source router
    heap.push(State {
        cost: 0,
        router: source,
        previous: 0, // Dummy value for source
    });
    costs.insert(source, 0);
    
    // Run Dijkstra's algorithm
    while let Some(State { cost, router, previous }) = heap.pop() {
        // Skip if we've already found a better path to this router
        if cost > *costs.get(&router).unwrap_or(&u64::MAX) {
            continue;
        }
        
        // If we've reached the destination, we can stop
        if router == destination {
            predecessors.insert(router, previous);
            break;
        }
        
        // Skip if we've already processed this router
        if visited.contains(&router) {
            continue;
        }
        
        // Mark router as visited
        visited.insert(router);
        predecessors.insert(router, previous);
        
        // Look at neighbors
        if let Some(connections) = updated_network.get(&router) {
            for &(next_router, capacity, utilization) in connections {
                // Skip if we've already processed this router
                if visited.contains(&next_router) {
                    continue;
                }
                
                // Calculate time to transmit over this link
                let transmission_time = calculate_transmission_time(capacity, utilization, data_size);
                
                // Skip links that are fully congested
                if transmission_time.is_infinite() {
                    continue;
                }
                
                // Calculate new cost to reach this neighbor
                let next_cost = cost + time_to_microseconds(transmission_time);
                
                // Update if we found a better path
                if next_cost < *costs.get(&next_router).unwrap_or(&u64::MAX) {
                    costs.insert(next_router, next_cost);
                    heap.push(State {
                        cost: next_cost,
                        router: next_router,
                        previous: router,
                    });
                }
            }
        }
    }
    
    // Reconstruct the path if we found one
    if !predecessors.contains_key(&destination) {
        return Vec::new(); // No path found
    }
    
    // Backtrack from destination to source
    let mut path = Vec::new();
    let mut current = destination;
    
    while current != source {
        path.push(current);
        current = *predecessors.get(&current).unwrap();
    }
    
    path.push(source);
    path.reverse();
    
    path
}

// Additional optimization: Alternative path finding with adaptive path selection
fn find_alternative_paths(
    network: &Network,
    source: RouterID,
    destination: RouterID,
    data_size: f64,
    max_paths: usize,
) -> Vec<Vec<RouterID>> {
    let mut paths = Vec::new();
    let mut excluded_links: HashSet<(RouterID, RouterID)> = HashSet::new();
    
    // Find multiple paths by iteratively excluding used links
    for _ in 0..max_paths {
        let path = find_path_with_excluded_links(network, source, destination, data_size, &excluded_links);
        
        if path.is_empty() {
            break; // No more paths found
        }
        
        // Add links in this path to excluded set for next iteration
        for i in 0..path.len() - 1 {
            excluded_links.insert((path[i], path[i+1]));
        }
        
        paths.push(path);
    }
    
    paths
}

// Helper to find a path with certain links excluded
fn find_path_with_excluded_links(
    network: &Network,
    source: RouterID,
    destination: RouterID,
    data_size: f64,
    excluded_links: &HashSet<(RouterID, RouterID)>,
) -> Vec<RouterID> {
    // Similar to find_optimal_route but with excluded links
    let mut heap = BinaryHeap::new();
    let mut costs: HashMap<RouterID, u64> = HashMap::new();
    let mut predecessors: HashMap<RouterID, RouterID> = HashMap::new();
    let mut visited: HashSet<RouterID> = HashSet::new();
    
    heap.push(State {
        cost: 0,
        router: source,
        previous: 0,
    });
    costs.insert(source, 0);
    
    while let Some(State { cost, router, previous }) = heap.pop() {
        if cost > *costs.get(&router).unwrap_or(&u64::MAX) {
            continue;
        }
        
        if router == destination {
            predecessors.insert(router, previous);
            break;
        }
        
        if visited.contains(&router) {
            continue;
        }
        
        visited.insert(router);
        predecessors.insert(router, previous);
        
        if let Some(connections) = network.get(&router) {
            for &(next_router, capacity, utilization) in connections {
                // Skip excluded links
                if excluded_links.contains(&(router, next_router)) {
                    continue;
                }
                
                if visited.contains(&next_router) {
                    continue;
                }
                
                let transmission_time = calculate_transmission_time(capacity, utilization, data_size);
                if transmission_time.is_infinite() {
                    continue;
                }
                
                let next_cost = cost + time_to_microseconds(transmission_time);
                if next_cost < *costs.get(&next_router).unwrap_or(&u64::MAX) {
                    costs.insert(next_router, next_cost);
                    heap.push(State {
                        cost: next_cost,
                        router: next_router,
                        previous: router,
                    });
                }
            }
        }
    }
    
    if !predecessors.contains_key(&destination) {
        return Vec::new();
    }
    
    let mut path = Vec::new();
    let mut current = destination;
    
    while current != source {
        path.push(current);
        if let Some(&prev) = predecessors.get(&current) {
            current = prev;
        } else {
            return Vec::new(); // Shouldn't happen, but just in case
        }
    }
    
    path.push(source);
    path.reverse();
    
    path
}