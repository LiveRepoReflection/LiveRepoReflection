#[test]
fn test_basic_two_partitions() {
    let n = 5;
    let edges = vec![(0, 1, 10), (1, 2, 5), (2, 3, 12), (3, 4, 8), (0, 4, 3)];
    let risk_scores = vec![15, 8, 20, 5, 10];
    let k = 2;
    let max_size = 3;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    // Verify basic constraints
    assert_eq!(result.len(), n, "Each node should be assigned to a partition");
    assert!(result.iter().all(|&x| x < k), "Partition IDs should be less than k");
    
    // Verify partition sizes
    let mut sizes = vec![0; k];
    for &partition_id in &result {
        sizes[partition_id] += 1;
    }
    assert!(sizes.iter().all(|&size| size <= max_size), "Partition size exceeds maximum allowed");
}

#[test]
fn test_single_partition() {
    let n = 3;
    let edges = vec![(0, 1, 1), (1, 2, 1)];
    let risk_scores = vec![1, 1, 1];
    let k = 1;
    let max_size = 3;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    assert!(result.iter().all(|&x| x == 0), "All nodes should be in partition 0");
}

#[test]
fn test_maximum_partitions() {
    let n = 4;
    let edges = vec![(0, 1, 1), (1, 2, 1), (2, 3, 1)];
    let risk_scores = vec![1, 1, 1, 1];
    let k = 4;
    let max_size = 1;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    // Check that each node is in its own partition
    let mut used_partitions = std::collections::HashSet::new();
    for partition_id in result {
        assert!(used_partitions.insert(partition_id), "Each node should be in a unique partition");
    }
    assert_eq!(used_partitions.len(), k, "Should use exactly k partitions");
}

#[test]
fn test_disconnected_graph() {
    let n = 6;
    let edges = vec![(0, 1, 1), (1, 2, 1), (4, 5, 1)]; // Nodes 3 is isolated
    let risk_scores = vec![10, 10, 10, 5, 20, 20];
    let k = 3;
    let max_size = 2;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    assert_eq!(result.len(), n);
    assert!(result.iter().all(|&x| x < k));
    
    // Verify partition sizes
    let mut sizes = vec![0; k];
    for &partition_id in &result {
        sizes[partition_id] += 1;
    }
    assert!(sizes.iter().all(|&size| size <= max_size));
}

#[test]
fn test_high_risk_nodes() {
    let n = 4;
    let edges = vec![(0, 1, 1), (1, 2, 1), (2, 3, 1)];
    let risk_scores = vec![1000, 1000, 1, 1];
    let k = 2;
    let max_size = 2;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    // High risk nodes should ideally be in different partitions
    let partition_of_high_risk = (result[0], result[1]);
    assert_ne!(partition_of_high_risk.0, partition_of_high_risk.1, 
        "High risk nodes should be in different partitions");
}

#[test]
fn test_high_fragility_edges() {
    let n = 4;
    let edges = vec![(0, 1, 1000), (1, 2, 1), (2, 3, 1)];
    let risk_scores = vec![10, 10, 10, 10];
    let k = 2;
    let max_size = 2;
    
    let result = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    // Verify basic constraints
    assert_eq!(result.len(), n);
    assert!(result.iter().all(|&x| x < k));
}

#[test]
fn test_edge_cases() {
    // Test minimum possible inputs
    let result1 = network_partitioning::partition(1, vec![], vec![1], 1, 1);
    assert_eq!(result1.len(), 1);
    assert_eq!(result1[0], 0);
    
    // Test with exactly max_size nodes per partition
    let n = 4;
    let edges = vec![(0, 1, 1), (2, 3, 1)];
    let risk_scores = vec![1, 1, 1, 1];
    let k = 2;
    let max_size = 2;
    
    let result2 = network_partitioning::partition(n, edges, risk_scores, k, max_size);
    
    let mut sizes = vec![0; k];
    for &partition_id in &result2 {
        sizes[partition_id] += 1;
    }
    assert!(sizes.iter().all(|&size| size <= max_size));
}

#[test]
#[should_panic]
fn test_invalid_input() {
    // Test with invalid k value
    let n = 3;
    let edges = vec![(0, 1, 1), (1, 2, 1)];
    let risk_scores = vec![1, 1, 1];
    let k = 0; // Invalid: k must be >= 1
    let max_size = 2;
    
    network_partitioning::partition(n, edges, risk_scores, k, max_size);
}
