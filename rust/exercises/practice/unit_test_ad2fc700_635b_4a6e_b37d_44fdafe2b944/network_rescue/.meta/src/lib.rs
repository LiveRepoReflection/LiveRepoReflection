use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Reverse;

pub fn recover_network(
    node_status: Vec<bool>,
    initial_connectivity: Vec<(usize, usize, u32)>,
    k: usize,
    max_path_cost: u32,
) -> Option<Vec<Vec<Option<u32>>>> {
    let n = node_status.len();
    
    // Check if we have enough operational nodes
    let operational_count = node_status.iter().filter(|&&operational| operational).count();
    if operational_count < k {
        return None;
    }
    
    // Create adjacency list representation of the network
    let mut graph: HashMap<usize, Vec<(usize, u32)>> = HashMap::new();
    
    // Initialize graph for all nodes (including non-operational ones)
    for node in 0..n {
        graph.insert(node, Vec::new());
    }
    
    // Add all connections to the graph
    for (u, v, cost) in initial_connectivity {
        // Only add connections if both endpoints are operational
        if node_status[u] && node_status[v] {
            graph.entry(u).or_default().push((v, cost));
            graph.entry(v).or_default().push((u, cost)); // Bidirectional
        }
    }
    
    // Initialize the result routing table with None values
    let mut routing_table = vec![vec![None; n]; n];
    
    // For each operational node, compute shortest paths to all other operational nodes
    let operational_nodes: Vec<usize> = (0..n)
        .filter(|&i| node_status[i])
        .collect();
    
    // Set self-loop distances to 0
    for &node in &operational_nodes {
        routing_table[node][node] = Some(0);
    }
    
    // Run Dijkstra's algorithm from each operational node
    for &start_node in &operational_nodes {
        let distances = dijkstra(&graph, start_node, &node_status, max_path_cost);
        
        // Update routing table with computed distances
        for &end_node in &operational_nodes {
            if start_node != end_node {
                routing_table[start_node][end_node] = distances.get(&end_node).copied();
            }
        }
    }
    
    // Check if all operational nodes can reach each other
    for &i in &operational_nodes {
        for &j in &operational_nodes {
            if i != j && routing_table[i][j].is_none() {
                // Found a pair of operational nodes that can't reach each other
                // within max_path_cost
                return None;
            }
        }
    }
    
    Some(routing_table)
}

// Dijkstra's algorithm to find shortest paths from start_node to all other nodes
fn dijkstra(
    graph: &HashMap<usize, Vec<(usize, u32)>>,
    start_node: usize,
    node_status: &[bool],
    max_path_cost: u32,
) -> HashMap<usize, u32> {
    let mut distances: HashMap<usize, u32> = HashMap::new();
    let mut visited: HashSet<usize> = HashSet::new();
    
    // Min-heap priority queue for Dijkstra
    let mut priority_queue = BinaryHeap::new();
    
    // Initialize distances
    distances.insert(start_node, 0);
    priority_queue.push(Reverse((0, start_node))); // (cost, node)
    
    while let Some(Reverse((current_cost, current_node))) = priority_queue.pop() {
        // If we've already processed this node, skip it
        if visited.contains(&current_node) {
            continue;
        }
        
        // Mark node as visited
        visited.insert(current_node);
        
        // If the current cost exceeds max_path_cost, we can stop exploring from this node
        if current_cost > max_path_cost {
            continue;
        }
        
        // Process all neighbors
        if let Some(neighbors) = graph.get(&current_node) {
            for &(neighbor, edge_cost) in neighbors {
                // Only consider operational nodes
                if !node_status[neighbor] {
                    continue;
                }
                
                // Calculate new cost to this neighbor
                let new_cost = current_cost + edge_cost;
                
                // Skip if new cost exceeds max_path_cost
                if new_cost > max_path_cost {
                    continue;
                }
                
                // Update distance if it's better
                let is_shorter = match distances.get(&neighbor) {
                    Some(&existing_cost) => new_cost < existing_cost,
                    None => true,
                };
                
                if is_shorter {
                    distances.insert(neighbor, new_cost);
                    priority_queue.push(Reverse((new_cost, neighbor)));
                }
            }
        }
    }
    
    distances
}