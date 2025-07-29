use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;

/// Optimizes the routing paths for a set of requests in a data center network.
///
/// # Arguments
/// * `n` - Number of servers in the data center (0 to n-1)
/// * `edges` - Network topology represented as bidirectional links (u, v, latency)
/// * `requests` - Routing requests from source to destination
///
/// # Returns
/// * Vector of optimal paths for each request (empty vector if no path exists)
pub fn optimize_routing(
    n: usize,
    edges: Vec<(usize, usize, u32)>,
    requests: Vec<(usize, usize)>,
) -> Vec<Vec<usize>> {
    // Create the adjacency list representation of the graph
    let graph = build_adjacency_list(n, &edges);
    
    // Initialize the result vector for paths
    let mut result = Vec::with_capacity(requests.len());
    
    // Process each request
    for (src, dest) in requests {
        if src == dest {
            // If source and destination are the same, the path is just the node itself
            result.push(vec![src]);
        } else {
            // Find the shortest path for this request
            let path = find_shortest_path(&graph, src, dest, n);
            result.push(path);
        }
    }
    
    result
}

/// Builds an adjacency list representation of the graph from the edges.
fn build_adjacency_list(n: usize, edges: &[(usize, usize, u32)]) -> Vec<Vec<(usize, u32)>> {
    let mut graph = vec![Vec::new(); n];
    
    // Add each bidirectional edge to the adjacency list
    for &(u, v, weight) in edges {
        graph[u].push((v, weight));
        graph[v].push((u, weight)); // Because edges are bidirectional
    }
    
    graph
}

/// Represents a node in the priority queue for Dijkstra's algorithm
#[derive(Copy, Clone, Eq, PartialEq)]
struct Node {
    vertex: usize,
    distance: u32,
}

// Custom implementation to create a min-heap based on distance
impl Ord for Node {
    fn cmp(&self, other: &Self) -> Ordering {
        // Flip the ordering to create a min-heap
        other.distance.cmp(&self.distance)
            .then_with(|| self.vertex.cmp(&other.vertex))
    }
}

impl PartialOrd for Node {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Implements Dijkstra's algorithm to find the shortest path between source and destination.
fn find_shortest_path(
    graph: &[Vec<(usize, u32)>],
    source: usize,
    destination: usize,
    n: usize,
) -> Vec<usize> {
    // Array to store distances from source
    let mut distances = vec![u32::MAX; n];
    distances[source] = 0;
    
    // Previous node in the optimal path
    let mut prev_node = vec![None; n];
    
    // Priority queue for Dijkstra's algorithm
    let mut pq = BinaryHeap::new();
    pq.push(Node { vertex: source, distance: 0 });
    
    // Visited nodes
    let mut visited = HashSet::new();
    
    // Dijkstra's algorithm
    while let Some(Node { vertex, distance }) = pq.pop() {
        // If this is the destination, we can terminate early
        if vertex == destination {
            break;
        }
        
        // Skip if already processed this vertex
        if visited.contains(&vertex) {
            continue;
        }
        
        // Mark this node as visited
        visited.insert(vertex);
        
        // Check all neighbors
        for &(neighbor, weight) in &graph[vertex] {
            if visited.contains(&neighbor) {
                continue;
            }
            
            let new_distance = distance.saturating_add(weight);
            
            // If a shorter path is found
            if new_distance < distances[neighbor] {
                distances[neighbor] = new_distance;
                prev_node[neighbor] = Some(vertex);
                pq.push(Node { vertex: neighbor, distance: new_distance });
            }
        }
    }
    
    // Reconstruct the path if destination is reachable
    reconstruct_path(source, destination, &prev_node)
}

/// Reconstructs the path from source to destination using the previous node array.
fn reconstruct_path(
    source: usize,
    destination: usize,
    prev_node: &[Option<usize>],
) -> Vec<usize> {
    // If destination is not reachable
    if prev_node[destination].is_none() && source != destination {
        return Vec::new();
    }
    
    // Reconstruct the path
    let mut path = Vec::new();
    let mut current = destination;
    
    // Start from destination and work backwards
    path.push(current);
    
    while let Some(previous) = prev_node[current] {
        path.push(previous);
        current = previous;
        
        // We've reached the source
        if previous == source {
            break;
        }
    }
    
    // Reverse to get path from source to destination
    path.reverse();
    
    path
}

/// Advanced version: Pre-compute all-pairs shortest paths for frequent queries
/// This function would be useful if there are many repeat queries or if the graph is dense
pub fn optimize_routing_with_precomputation(
    n: usize,
    edges: Vec<(usize, usize, u32)>,
    requests: Vec<(usize, usize)>,
) -> Vec<Vec<usize>> {
    // Build the adjacency list
    let graph = build_adjacency_list(n, &edges);
    
    // Count unique source nodes in requests to determine if precomputation is beneficial
    let mut unique_sources = HashSet::new();
    for (src, _) in &requests {
        unique_sources.insert(*src);
    }
    
    // Determine if precomputation is worth it based on number of unique sources vs total requests
    let use_precomputation = unique_sources.len() * 3 < requests.len() || unique_sources.len() * 3 > n;
    
    let mut result = Vec::with_capacity(requests.len());
    
    if use_precomputation {
        // Precompute shortest paths from all unique sources
        let mut precomputed_paths: HashMap<usize, (Vec<u32>, Vec<Option<usize>>)> = HashMap::new();
        
        for &source in &unique_sources {
            let (distances, prev_nodes) = compute_all_paths_from_source(&graph, source, n);
            precomputed_paths.insert(source, (distances, prev_nodes));
        }
        
        // Use precomputed paths for each request
        for (src, dest) in &requests {
            if src == dest {
                result.push(vec![*src]);
                continue;
            }
            
            let (_, prev_nodes) = precomputed_paths.get(src).unwrap();
            result.push(reconstruct_path(*src, *dest, prev_nodes));
        }
    } else {
        // Use the standard approach for fewer requests
        for (src, dest) in requests {
            if src == dest {
                result.push(vec![src]);
            } else {
                let path = find_shortest_path(&graph, src, dest, n);
                result.push(path);
            }
        }
    }
    
    result
}

/// Computes shortest paths from a single source to all other nodes.
fn compute_all_paths_from_source(
    graph: &[Vec<(usize, u32)>],
    source: usize,
    n: usize,
) -> (Vec<u32>, Vec<Option<usize>>) {
    // Array to store distances from source
    let mut distances = vec![u32::MAX; n];
    distances[source] = 0;
    
    // Previous node in the optimal path
    let mut prev_node = vec![None; n];
    
    // Priority queue for Dijkstra's algorithm
    let mut pq = BinaryHeap::new();
    pq.push(Node { vertex: source, distance: 0 });
    
    // Visited nodes
    let mut visited = HashSet::new();
    
    // Dijkstra's algorithm to compute all paths from the source
    while let Some(Node { vertex, distance }) = pq.pop() {
        if visited.contains(&vertex) {
            continue;
        }
        
        visited.insert(vertex);
        
        for &(neighbor, weight) in &graph[vertex] {
            if visited.contains(&neighbor) {
                continue;
            }
            
            let new_distance = distance.saturating_add(weight);
            
            if new_distance < distances[neighbor] {
                distances[neighbor] = new_distance;
                prev_node[neighbor] = Some(vertex);
                pq.push(Node { vertex: neighbor, distance: new_distance });
            }
        }
    }
    
    (distances, prev_node)
}