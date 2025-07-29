use std::collections::{HashMap, HashSet, VecDeque};

pub struct Link {
    pub from: usize,
    pub to: usize,
    pub capacity: u32,
}

pub struct TrafficDemand {
    pub source: usize,
    pub destination: usize,
    pub initial_rate: u32,
}

pub struct NetworkConfig {
    pub n: usize,                      // Number of nodes
    pub links: Vec<Link>,              // List of links
    pub traffic_demands: Vec<TrafficDemand>, // List of traffic demands
    pub time_units: u32,               // Number of time units to simulate
    pub alpha: f64,                    // Additive increase constant
    pub beta: f64,                     // Multiplicative decrease factor
}

// Represents a path through the network
struct Path {
    nodes: Vec<usize>,
    links: Vec<usize>,  // Index of links in the original links vector
}

// Represents a flow in the network
struct Flow {
    source: usize,
    destination: usize,
    rate: f64,
    path: Option<Path>,
}

/// Simulates the network congestion control algorithm
/// Returns the final sending rates for each traffic demand
pub fn simulate_network(config: &NetworkConfig) -> Vec<f64> {
    // Build adjacency list representation of the network
    let adj_list = build_adjacency_list(config);
    
    // Build links lookup for faster access
    let links_lookup = build_links_lookup(config);
    
    // Initialize flows from traffic demands
    let mut flows = initialize_flows(config);
    
    // Find paths for each flow
    find_paths_for_flows(&mut flows, &adj_list, &links_lookup, config.n);
    
    // Simulate for the given number of time units
    for _ in 0..config.time_units {
        // Calculate the current traffic on each link
        let link_traffic = calculate_link_traffic(&flows, config.links.len());
        
        // Check for congestion and adjust rates
        adjust_flow_rates(&mut flows, &link_traffic, config.links.as_slice(), config.alpha, config.beta);
    }
    
    // Extract final rates
    flows.iter()
        .map(|flow| flow.rate)
        .collect()
}

// Builds an adjacency list representation of the network
fn build_adjacency_list(config: &NetworkConfig) -> Vec<Vec<(usize, usize)>> {
    let mut adj_list = vec![Vec::new(); config.n];
    
    for (link_idx, link) in config.links.iter().enumerate() {
        // Add the link to the adjacency list: (to_node, link_index)
        adj_list[link.from].push((link.to, link_idx));
    }
    
    adj_list
}

// Builds a lookup map for links: (from, to) -> link_index
fn build_links_lookup(config: &NetworkConfig) -> HashMap<(usize, usize), usize> {
    let mut lookup = HashMap::new();
    
    for (link_idx, link) in config.links.iter().enumerate() {
        lookup.insert((link.from, link.to), link_idx);
    }
    
    lookup
}

// Initializes flows from traffic demands
fn initialize_flows(config: &NetworkConfig) -> Vec<Flow> {
    config.traffic_demands.iter()
        .map(|demand| Flow {
            source: demand.source,
            destination: demand.destination,
            rate: demand.initial_rate as f64,
            path: None,
        })
        .collect()
}

// Finds the shortest path for each flow using BFS
fn find_paths_for_flows(
    flows: &mut Vec<Flow>,
    adj_list: &Vec<Vec<(usize, usize)>>,
    links_lookup: &HashMap<(usize, usize), usize>,
    n: usize
) {
    for flow in flows.iter_mut() {
        // Skip flows where source == destination (self-loops)
        if flow.source == flow.destination {
            flow.rate = 0.0;
            continue;
        }
        
        // Find the shortest path using BFS
        if let Some(path) = find_shortest_path(flow.source, flow.destination, adj_list, links_lookup, n) {
            flow.path = Some(path);
        } else {
            // No path found, set rate to 0
            flow.rate = 0.0;
        }
    }
}

// Finds the shortest path from source to destination using BFS
fn find_shortest_path(
    source: usize,
    destination: usize,
    adj_list: &Vec<Vec<(usize, usize)>>,
    links_lookup: &HashMap<(usize, usize), usize>,
    n: usize
) -> Option<Path> {
    let mut queue = VecDeque::new();
    let mut visited = vec![false; n];
    let mut parent = vec![None; n];
    let mut parent_edge = vec![None; n];
    
    visited[source] = true;
    queue.push_back(source);
    
    while let Some(node) = queue.pop_front() {
        if node == destination {
            // Reconstruct the path
            let mut path_nodes = Vec::new();
            let mut path_links = Vec::new();
            let mut current = node;
            
            path_nodes.push(current);
            
            while let Some(prev) = parent[current] {
                path_links.push(parent_edge[current].unwrap());
                current = prev;
                path_nodes.push(current);
            }
            
            // Reverse to get correct order
            path_nodes.reverse();
            path_links.reverse();
            
            return Some(Path {
                nodes: path_nodes,
                links: path_links,
            });
        }
        
        // Sort neighbors by node index for consistent path selection
        // when there are multiple shortest paths
        let mut neighbors = adj_list[node].clone();
        neighbors.sort_by_key(|&(next, _)| next);
        
        for &(next, edge_idx) in &neighbors {
            if !visited[next] {
                visited[next] = true;
                parent[next] = Some(node);
                parent_edge[next] = Some(edge_idx);
                queue.push_back(next);
            }
        }
    }
    
    // No path found
    None
}

// Calculates the current traffic on each link
fn calculate_link_traffic(flows: &Vec<Flow>, num_links: usize) -> Vec<f64> {
    let mut traffic = vec![0.0; num_links];
    
    for flow in flows {
        // Skip flows with no path or zero rate
        if flow.rate == 0.0 || flow.path.is_none() {
            continue;
        }
        
        // Add this flow's rate to all links in its path
        if let Some(path) = &flow.path {
            for &link_idx in &path.links {
                traffic[link_idx] += flow.rate;
            }
        }
    }
    
    traffic
}

// Adjusts flow rates based on congestion
fn adjust_flow_rates(
    flows: &mut Vec<Flow>,
    link_traffic: &Vec<f64>,
    links: &[Link],
    alpha: f64,
    beta: f64
) {
    for flow in flows.iter_mut() {
        // Skip flows with no path
        if flow.path.is_none() {
            continue;
        }
        
        let path = flow.path.as_ref().unwrap();
        let mut is_congested = false;
        
        // Check if any link in the path is congested
        for &link_idx in &path.links {
            if link_traffic[link_idx] > links[link_idx].capacity as f64 {
                is_congested = true;
                break;
            }
        }
        
        // Apply AIMD algorithm
        if is_congested {
            // Multiplicative decrease
            flow.rate *= beta;
        } else {
            // Additive increase
            flow.rate += alpha;
        }
        
        // Ensure rate doesn't go below zero
        if flow.rate < 0.0 {
            flow.rate = 0.0;
        }
    }
}