use std::collections::{HashSet, VecDeque, HashMap};

/// Finds the minimum number of gateway nodes required to ensure that every node in
/// subnetwork1 can communicate with every node in subnetwork2.
///
/// # Arguments
///
/// * `n` - The total number of nodes in the network (0 to n-1)
/// * `adj_matrix` - The adjacency matrix representing the network connections
/// * `subnetwork1` - Vector of node IDs in the first subnetwork
/// * `subnetwork2` - Vector of node IDs in the second subnetwork
///
/// # Returns
///
/// The minimum number of gateway nodes needed
pub fn min_gateway_nodes(
    n: usize,
    adj_matrix: &Vec<Vec<bool>>,
    subnetwork1: &Vec<usize>,
    subnetwork2: &Vec<usize>,
) -> usize {
    // Find connected components within each subnetwork
    let components1 = find_connected_components(n, adj_matrix, subnetwork1);
    let components2 = find_connected_components(n, adj_matrix, subnetwork2);
    
    // The minimum number of gateways needed is the maximum of:
    // 1. Number of connected components in subnetwork1
    // 2. Number of connected components in subnetwork2
    std::cmp::max(components1.len(), components2.len())
}

/// Finds all connected components within a subnetwork using BFS
///
/// # Arguments
///
/// * `n` - Total number of nodes in the network
/// * `adj_matrix` - The adjacency matrix representing the network connections
/// * `subnetwork` - Vector of node IDs in the subnetwork
///
/// # Returns
///
/// A vector of connected components, where each component is a set of node IDs
fn find_connected_components(
    n: usize,
    adj_matrix: &Vec<Vec<bool>>,
    subnetwork: &Vec<usize>,
) -> Vec<HashSet<usize>> {
    // Create a set of nodes in the subnetwork for efficient lookup
    let subnetwork_set: HashSet<usize> = subnetwork.iter().cloned().collect();
    
    // Keep track of which nodes have been visited
    let mut visited: Vec<bool> = vec![false; n];
    
    // Store the connected components
    let mut components: Vec<HashSet<usize>> = Vec::new();
    
    // Process each node in the subnetwork
    for &node in subnetwork {
        // Skip if already visited
        if visited[node] {
            continue;
        }
        
        // Start a new component
        let mut component = HashSet::new();
        let mut queue = VecDeque::new();
        
        // Initialize BFS
        queue.push_back(node);
        visited[node] = true;
        
        // BFS to find all connected nodes within the subnetwork
        while let Some(current) = queue.pop_front() {
            component.insert(current);
            
            // Check all adjacent nodes
            for neighbor in 0..n {
                if adj_matrix[current][neighbor] && 
                   subnetwork_set.contains(&neighbor) && 
                   !visited[neighbor] {
                    visited[neighbor] = true;
                    queue.push_back(neighbor);
                }
            }
        }
        
        // Add the completed component to our list
        components.push(component);
    }
    
    components
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_case() {
        let n = 5;
        let adj_matrix = vec![
            vec![false, true, false, false, false],
            vec![true, false, true, false, false],
            vec![false, true, false, false, false],
            vec![false, false, false, false, true],
            vec![false, false, false, true, false],
        ];
        let subnetwork1 = vec![0, 1, 2];
        let subnetwork2 = vec![3, 4];
        
        assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 1);
    }

    #[test]
    fn test_disconnected_components() {
        let n = 6;
        let adj_matrix = vec![
            vec![false, true, false, false, false, false],
            vec![true, false, false, false, false, false],
            vec![false, false, false, false, false, false],
            vec![false, false, false, false, true, false],
            vec![false, false, false, true, false, false],
            vec![false, false, false, false, false, false],
        ];
        let subnetwork1 = vec![0, 1, 2];
        let subnetwork2 = vec![3, 4, 5];
        
        // subnetwork1 has 2 components: [0,1] and [2]
        // subnetwork2 has 2 components: [3,4] and [5]
        // so we need max(2,2) = 2 gateways
        assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 2);
    }
}