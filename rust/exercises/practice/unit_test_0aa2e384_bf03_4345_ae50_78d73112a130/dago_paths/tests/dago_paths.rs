use std::collections::HashMap;
use dago_paths::find_paths;

#[test]
fn test_empty_graph() {
    let nodes = HashMap::new();
    let paths = find_paths(&nodes, 1, 2, 2);
    assert!(paths.is_empty());
}

#[test]
fn test_single_node_no_paths() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2), (2, 3)]);
    let paths = find_paths(&nodes, 1, 4, 2);
    assert!(paths.is_empty());
}

#[test]
fn test_single_node_single_path() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2), (2, 3)]);
    let paths = find_paths(&nodes, 1, 3, 2);
    assert_eq!(paths, vec![vec![1, 2, 3]]);
}

#[test]
fn test_multiple_nodes_single_path() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    nodes.insert(2, vec![(2, 3)]);
    let paths = find_paths(&nodes, 1, 3, 2);
    assert_eq!(paths, vec![vec![1, 2, 3]]);
}

#[test]
fn test_multiple_paths_same_length() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2), (1, 3)]);
    nodes.insert(2, vec![(2, 4)]);
    nodes.insert(3, vec![(3, 4)]);
    let paths = find_paths(&nodes, 1, 4, 2);
    assert_eq!(paths.len(), 2);
    assert!(paths.contains(&vec![1, 2, 4]));
    assert!(paths.contains(&vec![1, 3, 4]));
}

#[test]
fn test_cycle_in_graph() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    nodes.insert(2, vec![(2, 3), (2, 1)]);
    nodes.insert(3, vec![(3, 4)]);
    let paths = find_paths(&nodes, 1, 4, 3);
    assert_eq!(paths, vec![vec![1, 2, 3, 4]]);
}

#[test]
fn test_unavailable_node() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    // Node 2 is missing from the nodes map
    nodes.insert(3, vec![(3, 4)]);
    let paths = find_paths(&nodes, 1, 4, 2);
    assert!(paths.is_empty());
}

#[test]
fn test_path_length_zero() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    let paths = find_paths(&nodes, 1, 1, 0);
    assert_eq!(paths, vec![vec![1]]);
}

#[test]
fn test_large_path_length() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    nodes.insert(2, vec![(2, 3)]);
    nodes.insert(3, vec![(3, 4)]);
    let paths = find_paths(&nodes, 1, 4, 10);
    assert!(paths.is_empty());
}

#[test]
fn test_disconnected_graph() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2)]);
    nodes.insert(3, vec![(3, 4)]);
    let paths = find_paths(&nodes, 1, 4, 1);
    assert!(paths.is_empty());
}

#[test]
fn test_multiple_nodes_multiple_paths() {
    let mut nodes = HashMap::new();
    nodes.insert(1, vec![(1, 2), (1, 3)]);
    nodes.insert(2, vec![(2, 4), (2, 5)]);
    nodes.insert(3, vec![(3, 4)]);
    nodes.insert(4, vec![(4, 6)]);
    nodes.insert(5, vec![(5, 6)]);
    let paths = find_paths(&nodes, 1, 6, 3);
    assert_eq!(paths.len(), 3);
    assert!(paths.contains(&vec![1, 2, 4, 6]));
    assert!(paths.contains(&vec![1, 2, 5, 6]));
    assert!(paths.contains(&vec![1, 3, 4, 6]));
}