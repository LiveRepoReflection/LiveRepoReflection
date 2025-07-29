use network_rescue::recover_network;

#[test]
fn test_simple_recoverable_network() {
    // 3 nodes, all operational
    let node_status = vec![true, true, true];
    
    // Connections: 0-1 (cost 5), 1-2 (cost 3)
    let initial_connectivity = vec![(0, 1, 5), (1, 2, 3)];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Expected routing table:
    // [Some(0), Some(5), Some(8)],
    // [Some(5), Some(0), Some(3)],
    // [Some(8), Some(3), Some(0)]
    assert!(result.is_some());
    let routing_table = result.unwrap();
    
    assert_eq!(routing_table[0][0], Some(0));
    assert_eq!(routing_table[0][1], Some(5));
    assert_eq!(routing_table[0][2], Some(8));
    
    assert_eq!(routing_table[1][0], Some(5));
    assert_eq!(routing_table[1][1], Some(0));
    assert_eq!(routing_table[1][2], Some(3));
    
    assert_eq!(routing_table[2][0], Some(8));
    assert_eq!(routing_table[2][1], Some(3));
    assert_eq!(routing_table[2][2], Some(0));
}

#[test]
fn test_network_with_compromised_node() {
    // 3 nodes, node 1 is compromised
    let node_status = vec![true, false, true];
    
    // Connections: 0-1 (cost 5), 1-2 (cost 3), 0-2 (cost 10)
    let initial_connectivity = vec![(0, 1, 5), (1, 2, 3), (0, 2, 10)];
    
    // Need at least 2 nodes, max path cost is 10
    let k = 2;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Expected routing table:
    // [Some(0), None,    Some(10)],
    // [None,    None,    None    ],
    // [Some(10), None,    Some(0) ]
    assert!(result.is_some());
    let routing_table = result.unwrap();
    
    assert_eq!(routing_table[0][0], Some(0));
    assert_eq!(routing_table[0][1], None);
    assert_eq!(routing_table[0][2], Some(10));
    
    assert_eq!(routing_table[1][0], None);
    assert_eq!(routing_table[1][1], None);
    assert_eq!(routing_table[1][2], None);
    
    assert_eq!(routing_table[2][0], Some(10));
    assert_eq!(routing_table[2][1], None);
    assert_eq!(routing_table[2][2], Some(0));
}

#[test]
fn test_unreachable_due_to_cost() {
    // 3 nodes, all operational
    let node_status = vec![true, true, true];
    
    // Connections: 0-1 (cost 5), 1-2 (cost 10)
    let initial_connectivity = vec![(0, 1, 5), (1, 2, 10)];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Expected routing table:
    // [Some(0), Some(5), None    ],
    // [Some(5), Some(0), Some(10)],
    // [None,    Some(10),Some(0) ]
    assert_eq!(result, None); // Network can't be recovered as not all nodes can reach each other within cost limit
}

#[test]
fn test_insufficient_operational_nodes() {
    // 5 nodes, only 2 operational
    let node_status = vec![true, false, true, false, false];
    
    // Various connections
    let initial_connectivity = vec![(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Not enough operational nodes
    assert_eq!(result, None);
}

#[test]
fn test_disconnected_network() {
    // 4 nodes, all operational
    let node_status = vec![true, true, true, true];
    
    // Two disconnected components: 0-1 and 2-3
    let initial_connectivity = vec![(0, 1, 5), (2, 3, 3)];
    
    // Need at least 4 nodes, max path cost is 10
    let k = 4;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Network is disconnected
    assert_eq!(result, None);
}

#[test]
fn test_multiple_paths() {
    // 3 nodes, all operational
    let node_status = vec![true, true, true];
    
    // Multiple paths from 0 to 2: direct (cost 10) or via 1 (cost 5+3=8)
    let initial_connectivity = vec![(0, 1, 5), (1, 2, 3), (0, 2, 10)];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Expected routing table with minimum costs:
    // [Some(0), Some(5), Some(8)],
    // [Some(5), Some(0), Some(3)],
    // [Some(8), Some(3), Some(0)]
    assert!(result.is_some());
    let routing_table = result.unwrap();
    
    assert_eq!(routing_table[0][2], Some(8)); // Should choose path via node 1 (cost 8) not direct (cost 10)
}

#[test]
fn test_empty_connectivity() {
    // 3 nodes, all operational
    let node_status = vec![true, true, true];
    
    // No connections
    let initial_connectivity = vec![];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Network is disconnected
    assert_eq!(result, None);
}

#[test]
fn test_all_nodes_compromised() {
    // 3 nodes, none operational
    let node_status = vec![false, false, false];
    
    // Connections that won't be used
    let initial_connectivity = vec![(0, 1, 1), (1, 2, 1)];
    
    // Need at least 1 node, max path cost is 10
    let k = 1;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // No operational nodes
    assert_eq!(result, None);
}

#[test]
fn test_large_network() {
    // Create a line network with 100 nodes
    let node_status = vec![true; 100];
    
    // Connect nodes in a line: 0-1-2-3-...-99
    let mut initial_connectivity = Vec::new();
    for i in 0..99 {
        initial_connectivity.push((i, i+1, 1));
    }
    
    // Need all 100 nodes, max path cost is 99 (just enough for end-to-end)
    let k = 100;
    let max_path_cost = 99;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Network should be recoverable
    assert!(result.is_some());
    let routing_table = result.unwrap();
    
    // Check a few key distances
    assert_eq!(routing_table[0][99], Some(99)); // End to end distance
    assert_eq!(routing_table[0][50], Some(50)); // Middle distance
    assert_eq!(routing_table[25][75], Some(50)); // Random distance
}

#[test]
fn test_cost_exceeds_max() {
    // 3 nodes, all operational
    let node_status = vec![true, true, true];
    
    // Connections: 0-1 (cost 5), 1-2 (cost 6)
    let initial_connectivity = vec![(0, 1, 5), (1, 2, 6)];
    
    // Need at least 3 nodes, max path cost is 10
    let k = 3;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    // Path from 0 to 2 costs 11, which exceeds max_path_cost
    assert_eq!(result, None);
}

#[test]
fn test_self_loops() {
    // Check that self-connections always have cost 0
    let node_status = vec![true, true];
    
    // Only connection is between nodes 0 and 1
    let initial_connectivity = vec![(0, 1, 5)];
    
    // Need at least 2 nodes, max path cost is 10
    let k = 2;
    let max_path_cost = 10;
    
    let result = recover_network(node_status, initial_connectivity, k, max_path_cost);
    
    assert!(result.is_some());
    let routing_table = result.unwrap();
    
    // Self connections should have cost 0
    assert_eq!(routing_table[0][0], Some(0));
    assert_eq!(routing_table[1][1], Some(0));
}