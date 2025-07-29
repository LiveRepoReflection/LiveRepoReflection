use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct Node {
    pub id: i32,
    pub resource: i32,
    pub security: i32,
}

#[derive(Debug, Clone)]
pub struct Edge {
    pub source: i32,
    pub destination: i32,
    pub cost: i32,
    pub stability: f64,
}

pub fn find_max_reliability(
    nodes: &Vec<Node>,
    edges: &Vec<Edge>,
    origin: i32,
    destination: i32,
    min_required: i32,
    max_security: i32,
) -> f64 {
    let mut node_map: HashMap<i32, &Node> = HashMap::new();
    for node in nodes {
        node_map.insert(node.id, node);
    }
    // Verify that origin and destination exist.
    if !node_map.contains_key(&origin) || !node_map.contains_key(&destination) {
        return 0.0;
    }
    
    // Build an adjacency list mapping from node id to vector of edge indices.
    let mut adj: HashMap<i32, Vec<usize>> = HashMap::new();
    for (i, edge) in edges.iter().enumerate() {
        adj.entry(edge.source).or_default().push(i);
    }
    
    let start_node = node_map[&origin];
    // Check if starting node itself violates resource or security constraints.
    if start_node.resource < min_required || start_node.security > max_security {
        return 0.0;
    }
    
    let mut best_reliability: f64 = 0.0;
    let mut visited_edges = HashSet::new();
    
    // Depth-first search helper function.
    fn dfs(
        current: i32,
        destination: i32,
        current_reliability: f64,
        current_min_resource: i32,
        current_security: i32,
        min_required: i32,
        max_security: i32,
        adj: &HashMap<i32, Vec<usize>>,
        edges: &Vec<Edge>,
        node_map: &HashMap<i32, &Node>,
        visited_edges: &mut HashSet<usize>,
        best_reliability: &mut f64,
    ) {
        if current == destination {
            if current_min_resource >= min_required && current_security <= max_security {
                if current_reliability > *best_reliability {
                    *best_reliability = current_reliability;
                }
            }
            return;
        }
        
        if let Some(edge_indices) = adj.get(&current) {
            for &edge_idx in edge_indices {
                // Ensure each wormhole is used at most once.
                if visited_edges.contains(&edge_idx) {
                    continue;
                }
                let edge = &edges[edge_idx];
                let next_node_id = edge.destination;
                if let Some(next_node) = node_map.get(&next_node_id) {
                    let new_security = current_security + next_node.security;
                    let new_min_resource = if next_node.resource < current_min_resource {
                        next_node.resource
                    } else {
                        current_min_resource
                    };
                    // Prune paths that already exceed security threshold or can never meet resource requirement.
                    if new_security > max_security || new_min_resource < min_required {
                        continue;
                    }
                    let new_reliability = current_reliability * edge.stability;
                    visited_edges.insert(edge_idx);
                    dfs(
                        next_node_id,
                        destination,
                        new_reliability,
                        new_min_resource,
                        new_security,
                        min_required,
                        max_security,
                        adj,
                        edges,
                        node_map,
                        visited_edges,
                        best_reliability,
                    );
                    visited_edges.remove(&edge_idx);
                }
            }
        }
    }
    
    dfs(
        origin,
        destination,
        1.0,
        start_node.resource,
        start_node.security,
        min_required,
        max_security,
        &adj,
        edges,
        &node_map,
        &mut visited_edges,
        &mut best_reliability,
    );
    
    best_reliability
}