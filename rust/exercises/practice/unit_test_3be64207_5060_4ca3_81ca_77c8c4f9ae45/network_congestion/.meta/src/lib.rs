use std::collections::{HashMap, HashSet};

pub fn minimize_congestion(
    n: usize,
    edges: Vec<(usize, usize, i32)>,
    packet_routes: Vec<(usize, usize, i32)>,
    routing_table: HashMap<(usize, usize), Vec<usize>>,
) -> i32 {
    // Create a set of undirected edges for connectivity checking.
    let mut edge_set = HashSet::new();
    for (u, v, _) in edges.iter() {
        let (a, b) = if u < v { (*u, *v) } else { (*v, *u) };
        edge_set.insert((a, b));
    }
    
    // Initialize congestion vector for each node, with 0 load initially.
    let mut congestion = vec![0; n];

    // Process each packet route.
    for &(source, destination, size) in packet_routes.iter() {
        // Retrieve the route from the routing table.
        let route = match routing_table.get(&(source, destination)) {
            Some(r) => r,
            None => return -1, // If no route exists, return -1.
        };

        // Validate the route starts with source and ends with destination.
        if route.first() != Some(&source) || route.last() != Some(&destination) {
            return -1;
        }

        // For each consecutive pair in the route, verify that an edge exists.
        for window in route.windows(2) {
            if let [a, b] = window {
                let (x, y) = if a < b { (*a, *b) } else { (*b, *a) };
                if !edge_set.contains(&(x, y)) {
                    return -1;
                }
            }
        }

        // Add the packet size to the congestion for each node on the route.
        for &node in route.iter() {
            if node >= n {
                return -1;
            }
            congestion[node] += size;
        }
    }
    
    // Determine and return the maximum congestion across all nodes.
    *congestion.iter().max().unwrap_or(&0)
}