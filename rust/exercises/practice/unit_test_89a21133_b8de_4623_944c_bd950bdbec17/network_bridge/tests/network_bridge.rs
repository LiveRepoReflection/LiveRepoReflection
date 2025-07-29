use network_bridge::min_gateway_nodes;

#[test]
fn test_simple_case() {
    // Two small disconnected networks, as in the example
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
fn test_disconnected_networks() {
    // Two completely isolated networks with no internal connections
    let n = 6;
    let adj_matrix = vec![
        vec![false, false, false, false, false, false],
        vec![false, false, false, false, false, false],
        vec![false, false, false, false, false, false],
        vec![false, false, false, false, false, false],
        vec![false, false, false, false, false, false],
        vec![false, false, false, false, false, false],
    ];
    let subnetwork1 = vec![0, 1];
    let subnetwork2 = vec![3, 4];
    
    // Since both subnetworks have no internal connections, 
    // we need two gateway nodes to ensure full connectivity
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 2);
}

#[test]
fn test_fully_connected_subnetworks() {
    // Two fully connected subnetworks that are disconnected from each other
    let n = 6;
    let adj_matrix = vec![
        vec![false, true, true, false, false, false],
        vec![true, false, true, false, false, false],
        vec![true, true, false, false, false, false],
        vec![false, false, false, false, true, true],
        vec![false, false, false, true, false, true],
        vec![false, false, false, true, true, false],
    ];
    let subnetwork1 = vec![0, 1, 2];
    let subnetwork2 = vec![3, 4, 5];
    
    // Since each subnetwork is fully connected internally,
    // we only need one gateway to connect them
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 1);
}

#[test]
fn test_single_node_subnetworks() {
    // Two single-node networks
    let n = 4;
    let adj_matrix = vec![
        vec![false, true, false, false],
        vec![true, false, false, false],
        vec![false, false, false, true],
        vec![false, false, true, false],
    ];
    let subnetwork1 = vec![0];
    let subnetwork2 = vec![3];
    
    // Need one gateway to connect the two nodes
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 1);
}

#[test]
fn test_complex_network() {
    // A more complex network with multiple components
    let n = 10;
    let mut adj_matrix = vec![vec![false; n]; n];
    
    // Set up connections within subnetwork1 (nodes 0-4)
    adj_matrix[0][1] = true; adj_matrix[1][0] = true;
    adj_matrix[1][2] = true; adj_matrix[2][1] = true;
    adj_matrix[2][3] = true; adj_matrix[3][2] = true;
    
    // Set up connections within subnetwork2 (nodes 5-9)
    adj_matrix[5][6] = true; adj_matrix[6][5] = true;
    adj_matrix[6][7] = true; adj_matrix[7][6] = true;
    adj_matrix[7][8] = true; adj_matrix[8][7] = true;
    adj_matrix[8][9] = true; adj_matrix[9][8] = true;
    
    let subnetwork1 = vec![0, 1, 2, 3, 4];
    let subnetwork2 = vec![5, 6, 7, 8, 9];
    
    // Node 4 in subnetwork1 is disconnected, and all nodes in subnetwork2 form a line
    // We need two gateways to ensure all nodes can communicate
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 2);
}

#[test]
fn test_partially_connected_subnetworks() {
    // Two partially connected subnetworks
    let n = 8;
    let mut adj_matrix = vec![vec![false; n]; n];
    
    // Set up connections
    adj_matrix[0][1] = true; adj_matrix[1][0] = true;
    adj_matrix[1][2] = true; adj_matrix[2][1] = true;
    adj_matrix[4][5] = true; adj_matrix[5][4] = true;
    adj_matrix[5][6] = true; adj_matrix[6][5] = true;
    
    let subnetwork1 = vec![0, 1, 2, 3];
    let subnetwork2 = vec![4, 5, 6, 7];
    
    // Node 3 in subnetwork1 and node 7 in subnetwork2 are disconnected
    // We need 2 gateways
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 2);
}

#[test]
fn test_large_isolated_networks() {
    // Two large networks with no internal connections
    let n = 200;
    let adj_matrix = vec![vec![false; n]; n];
    
    // Create two large subnetworks
    let subnetwork1: Vec<usize> = (0..50).collect();
    let subnetwork2: Vec<usize> = (100..150).collect();
    
    // With no internal connections in either network, 
    // we need enough gateways to connect every node
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 50);
}

#[test]
fn test_one_connected_one_isolated() {
    // One fully connected network and one with no connections
    let n = 10;
    let mut adj_matrix = vec![vec![false; n]; n];
    
    // Make subnetwork1 fully connected
    for i in 0..4 {
        for j in 0..4 {
            if i != j {
                adj_matrix[i][j] = true;
            }
        }
    }
    
    let subnetwork1 = vec![0, 1, 2, 3];
    let subnetwork2 = vec![5, 6, 7, 8, 9];
    
    // Since subnetwork1 is fully connected but subnetwork2 has no internal connections,
    // we need 5 gateways (one to connect to subnetwork1, and then one for each node in subnetwork2)
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 5);
}

#[test]
fn test_edge_case_overlapping_nodes() {
    // Test where gateway can be an existing node from either subnetwork
    let n = 8;
    let adj_matrix = vec![
        vec![false, true, true, true, false, false, false, false],
        vec![true, false, true, true, false, false, false, false],
        vec![true, true, false, true, false, false, false, false],
        vec![true, true, true, false, false, false, false, false],
        vec![false, false, false, false, false, true, true, true],
        vec![false, false, false, false, true, false, true, true],
        vec![false, false, false, false, true, true, false, true],
        vec![false, false, false, false, true, true, true, false],
    ];
    
    let subnetwork1 = vec![0, 1, 2, 3];
    let subnetwork2 = vec![4, 5, 6, 7];
    
    // Both subnetworks are cliques (fully connected internally)
    // We only need 1 gateway to connect them
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 1);
}

#[test]
fn test_edge_case_single_nodes() {
    // Test with just two nodes
    let n = 2;
    let adj_matrix = vec![
        vec![false, false],
        vec![false, false],
    ];
    
    let subnetwork1 = vec![0];
    let subnetwork2 = vec![1];
    
    // Need 1 gateway to connect the two isolated nodes
    assert_eq!(min_gateway_nodes(n, &adj_matrix, &subnetwork1, &subnetwork2), 1);
}