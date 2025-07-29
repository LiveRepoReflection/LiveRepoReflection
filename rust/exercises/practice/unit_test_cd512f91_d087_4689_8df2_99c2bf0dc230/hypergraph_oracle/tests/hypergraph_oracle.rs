use hypergraph_oracle::HypergraphConnectivityOracle;

#[test]
fn test_simple_example() {
    let mut oracle = HypergraphConnectivityOracle::new(5);
    
    oracle.add_hyperedge(vec![1, 2, 3]);
    oracle.add_hyperedge(vec![3, 4]);
    
    assert!(oracle.are_connected(1, 4));
    assert!(!oracle.are_connected(1, 5));
    
    oracle.add_hyperedge(vec![5]);
    assert!(!oracle.are_connected(1, 5));
    
    oracle.add_hyperedge(vec![2, 5]);
    assert!(oracle.are_connected(1, 5));
}

#[test]
fn test_single_vertex() {
    let mut oracle = HypergraphConnectivityOracle::new(1);
    assert!(oracle.are_connected(1, 1)); // A vertex is always connected to itself
    
    oracle.add_hyperedge(vec![1]);
    assert!(oracle.are_connected(1, 1));
}

#[test]
fn test_empty_hyperedge() {
    let mut oracle = HypergraphConnectivityOracle::new(5);
    oracle.add_hyperedge(vec![]);
    
    assert!(!oracle.are_connected(1, 2));
}

#[test]
fn test_disconnected_components() {
    let mut oracle = HypergraphConnectivityOracle::new(10);
    
    // Create two disconnected components
    oracle.add_hyperedge(vec![1, 2, 3]);
    oracle.add_hyperedge(vec![4, 5]);
    oracle.add_hyperedge(vec![6, 7, 8, 9]);
    
    // Vertices in the same component should be connected
    assert!(oracle.are_connected(1, 3));
    assert!(oracle.are_connected(4, 5));
    assert!(oracle.are_connected(6, 9));
    
    // Vertices in different components should not be connected
    assert!(!oracle.are_connected(1, 4));
    assert!(!oracle.are_connected(3, 6));
    assert!(!oracle.are_connected(5, 8));
    assert!(!oracle.are_connected(2, 10));
    
    // Connect the components
    oracle.add_hyperedge(vec![3, 6]);
    
    // Now vertices from the first and third components should be connected
    assert!(oracle.are_connected(1, 9));
    assert!(oracle.are_connected(2, 7));
    
    // But still not connected to the second component
    assert!(!oracle.are_connected(1, 4));
    assert!(!oracle.are_connected(8, 5));
    
    // Connect all components
    oracle.add_hyperedge(vec![5, 9]);
    
    // Now all vertices should be connected
    assert!(oracle.are_connected(1, 4));
    assert!(oracle.are_connected(2, 5));
    assert!(oracle.are_connected(3, 8));
    assert!(oracle.are_connected(7, 4));
    
    // Except vertex 10 which is still isolated
    assert!(!oracle.are_connected(1, 10));
    assert!(!oracle.are_connected(5, 10));
    assert!(!oracle.are_connected(9, 10));
}

#[test]
fn test_large_hyperedges() {
    let mut oracle = HypergraphConnectivityOracle::new(1000);
    
    // Create a large hyperedge
    let mut large_edge: Vec<usize> = (1..501).collect();
    oracle.add_hyperedge(large_edge);
    
    // Create another large hyperedge with some overlap
    let mut another_edge: Vec<usize> = (400..900).collect();
    oracle.add_hyperedge(another_edge);
    
    // Vertices from both hyperedges should be connected
    assert!(oracle.are_connected(100, 700));
    assert!(oracle.are_connected(1, 899));
    assert!(oracle.are_connected(500, 401));
    
    // Vertices outside these hyperedges should not be connected
    assert!(!oracle.are_connected(1, 901));
    assert!(!oracle.are_connected(950, 500));
    
    // Connect the rest
    oracle.add_hyperedge(vec![899, 950]);
    assert!(oracle.are_connected(1, 950));
    assert!(oracle.are_connected(600, 950));
}

#[test]
fn test_incremental_connectivity() {
    let mut oracle = HypergraphConnectivityOracle::new(10);
    
    // No connections initially
    for i in 1..=10 {
        for j in 1..=10 {
            if i == j {
                assert!(oracle.are_connected(i, j));
            } else {
                assert!(!oracle.are_connected(i, j));
            }
        }
    }
    
    // Add hyperedges one by one and check connectivity
    oracle.add_hyperedge(vec![1, 2]);
    assert!(oracle.are_connected(1, 2));
    assert!(!oracle.are_connected(1, 3));
    
    oracle.add_hyperedge(vec![3, 4, 5]);
    assert!(oracle.are_connected(3, 5));
    assert!(!oracle.are_connected(2, 3));
    
    oracle.add_hyperedge(vec![2, 4]);
    assert!(oracle.are_connected(1, 5));
    assert!(oracle.are_connected(3, 1));
    assert!(!oracle.are_connected(1, 6));
    
    oracle.add_hyperedge(vec![5, 6, 7]);
    assert!(oracle.are_connected(1, 7));
    assert!(oracle.are_connected(3, 6));
    assert!(!oracle.are_connected(1, 8));
    
    oracle.add_hyperedge(vec![8, 9]);
    assert!(oracle.are_connected(8, 9));
    assert!(!oracle.are_connected(7, 8));
    
    oracle.add_hyperedge(vec![7, 8]);
    // Now all vertices 1-9 should be connected
    for i in 1..=9 {
        for j in 1..=9 {
            assert!(oracle.are_connected(i, j));
        }
    }
    
    // But not vertex 10
    for i in 1..=9 {
        assert!(!oracle.are_connected(i, 10));
    }
}

#[test]
fn test_complex_connections() {
    let mut oracle = HypergraphConnectivityOracle::new(15);
    
    // Create a complex hypergraph structure
    oracle.add_hyperedge(vec![1, 2, 3]);
    oracle.add_hyperedge(vec![4, 5]);
    oracle.add_hyperedge(vec![6, 7, 8]);
    oracle.add_hyperedge(vec![9, 10, 11, 12]);
    oracle.add_hyperedge(vec![13, 14, 15]);
    
    // Initial connections within components
    assert!(oracle.are_connected(1, 3));
    assert!(oracle.are_connected(4, 5));
    assert!(oracle.are_connected(6, 8));
    assert!(oracle.are_connected(9, 12));
    assert!(oracle.are_connected(13, 15));
    
    // No connections between components
    assert!(!oracle.are_connected(3, 4));
    assert!(!oracle.are_connected(5, 7));
    assert!(!oracle.are_connected(8, 9));
    assert!(!oracle.are_connected(12, 13));
    
    // Connect some components
    oracle.add_hyperedge(vec![3, 5, 8]);
    
    // Check new connections
    assert!(oracle.are_connected(1, 4));
    assert!(oracle.are_connected(2, 7));
    assert!(oracle.are_connected(4, 6));
    assert!(!oracle.are_connected(3, 9));
    assert!(!oracle.are_connected(8, 14));
    
    // Connect more components
    oracle.add_hyperedge(vec![8, 11]);
    
    // Check new connections
    assert!(oracle.are_connected(1, 10));
    assert!(oracle.are_connected(5, 12));
    assert!(oracle.are_connected(6, 9));
    assert!(!oracle.are_connected(1, 13));
    
    // Connect all components
    oracle.add_hyperedge(vec![12, 15]);
    
    // Now all vertices should be connected
    for i in 1..=15 {
        for j in 1..=15 {
            assert!(oracle.are_connected(i, j));
        }
    }
}

#[test]
fn test_performance_many_small_hyperedges() {
    let n = 1000;
    let mut oracle = HypergraphConnectivityOracle::new(n);
    
    // Create n-1 hyperedges connecting consecutive vertices
    for i in 1..n {
        oracle.add_hyperedge(vec![i, i+1]);
    }
    
    // Check that all vertices are connected
    assert!(oracle.are_connected(1, n));
    assert!(oracle.are_connected(250, 750));
    
    // Add some random queries to test performance
    assert!(oracle.are_connected(123, 456));
    assert!(oracle.are_connected(789, 234));
    assert!(oracle.are_connected(567, 890));
}

#[test]
fn test_self_loops() {
    let mut oracle = HypergraphConnectivityOracle::new(5);
    
    // Add self-loops (hyperedges with just one vertex)
    oracle.add_hyperedge(vec![1]);
    oracle.add_hyperedge(vec![3]);
    oracle.add_hyperedge(vec![5]);
    
    // Self-loops don't connect to other vertices
    assert!(!oracle.are_connected(1, 2));
    assert!(!oracle.are_connected(3, 4));
    
    // Connect some vertices
    oracle.add_hyperedge(vec![1, 2]);
    oracle.add_hyperedge(vec![3, 4]);
    
    assert!(oracle.are_connected(1, 2));
    assert!(oracle.are_connected(3, 4));
    assert!(!oracle.are_connected(2, 3));
    assert!(!oracle.are_connected(1, 5));
    
    // Connect all components
    oracle.add_hyperedge(vec![2, 3, 5]);
    
    assert!(oracle.are_connected(1, 5));
    assert!(oracle.are_connected(1, 4));
    assert!(oracle.are_connected(3, 5));
}

#[test]
fn test_duplicate_hyperedges() {
    let mut oracle = HypergraphConnectivityOracle::new(5);
    
    // Add a hyperedge
    oracle.add_hyperedge(vec![1, 2, 3]);
    assert!(oracle.are_connected(1, 3));
    assert!(!oracle.are_connected(1, 4));
    
    // Add the same hyperedge again (should have no effect)
    oracle.add_hyperedge(vec![1, 2, 3]);
    assert!(oracle.are_connected(1, 3));
    assert!(!oracle.are_connected(1, 4));
    
    // Add a hyperedge with some overlap
    oracle.add_hyperedge(vec![3, 4, 5]);
    assert!(oracle.are_connected(1, 5));
    assert!(oracle.are_connected(2, 4));
    
    // Add it again (should have no effect)
    oracle.add_hyperedge(vec![3, 4, 5]);
    assert!(oracle.are_connected(1, 5));
    assert!(oracle.are_connected(2, 4));
}

#[test]
fn test_large_number_of_hyperedges() {
    let n = 100;
    let mut oracle = HypergraphConnectivityOracle::new(n);
    
    // Add many hyperedges in a star pattern
    for i in 2..=n {
        oracle.add_hyperedge(vec![1, i]);
    }
    
    // All vertices should be connected
    for i in 2..=n {
        for j in i+1..=n {
            assert!(oracle.are_connected(i, j));
        }
    }
    
    // Create a new oracle with grid pattern
    let mut oracle2 = HypergraphConnectivityOracle::new(n);
    
    // Create a grid pattern of connections
    for i in 1..=n/10 {
        let base = (i-1) * 10;
        for j in 1..10 {
            oracle2.add_hyperedge(vec![base + j, base + j + 1]);
        }
    }
    
    // Connect the rows
    for i in 1..n/10 {
        let row1 = (i-1) * 10 + 1;
        let row2 = i * 10 + 1;
        oracle2.add_hyperedge(vec![row1, row2]);
    }
    
    // Test connectivity
    assert!(oracle2.are_connected(1, n/10 * 10));
    assert!(oracle2.are_connected(5, 95));
    assert!(oracle2.are_connected(11, 22));
}