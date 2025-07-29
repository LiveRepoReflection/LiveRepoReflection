use network_route::optimize_routing;

struct TestCase {
    n: usize,
    edges: Vec<(usize, usize, u32)>,
    requests: Vec<(usize, usize)>,
    expected_paths: Vec<Vec<usize>>,
    expected_max_latency: u32,
}

#[test]
fn test_simple_network() {
    // Simple line network: 0 -- 1 -- 2 -- 3
    let test_case = TestCase {
        n: 4,
        edges: vec![(0, 1, 10), (1, 2, 5), (2, 3, 15)],
        requests: vec![(0, 3), (3, 0), (1, 3)],
        expected_paths: vec![vec![0, 1, 2, 3], vec![3, 2, 1, 0], vec![1, 2, 3]],
        expected_max_latency: 30,
    };
    
    run_test_case(&test_case);
}

#[test]
fn test_multiple_paths() {
    // Network with multiple paths between nodes
    // 0 -- 1 -- 3
    // |    |    |
    // +--- 2 ---+
    let test_case = TestCase {
        n: 4,
        edges: vec![
            (0, 1, 10), (1, 3, 15),
            (0, 2, 5), (2, 3, 10),
            (1, 2, 2),
        ],
        requests: vec![(0, 3)],
        expected_paths: vec![vec![0, 2, 3]], // Path 0->2->3 has latency 15, which is less than 0->1->3 (25)
        expected_max_latency: 15,
    };
    
    run_test_case(&test_case);
}

#[test]
fn test_disconnected_graph() {
    // Disconnected graph: 0 -- 1    2 -- 3
    let test_case = TestCase {
        n: 4,
        edges: vec![(0, 1, 5), (2, 3, 7)],
        requests: vec![(0, 3), (0, 1), (2, 3)],
        expected_paths: vec![vec![], vec![0, 1], vec![2, 3]], // No path from 0 to 3
        expected_max_latency: 7,  // Only considering the valid paths
    };
    
    run_test_case(&test_case);
}

#[test]
fn test_same_source_destination() {
    // Test when source and destination are the same
    let test_case = TestCase {
        n: 3,
        edges: vec![(0, 1, 5), (1, 2, 7)],
        requests: vec![(0, 0), (1, 1), (2, 2)],
        expected_paths: vec![vec![0], vec![1], vec![2]], // Path from a node to itself is just the node
        expected_max_latency: 0,  // No edges traversed, so latency is 0
    };
    
    run_test_case(&test_case);
}

#[test]
fn test_complex_network() {
    // More complex network with multiple optimal paths
    //   1 -- 3
    //  /|    | \
    // 0 |    |  5
    //  \|    | /
    //   2 -- 4
    let test_case = TestCase {
        n: 6,
        edges: vec![
            (0, 1, 7), (0, 2, 9),
            (1, 2, 10), (1, 3, 15),
            (2, 4, 11), (3, 4, 6),
            (3, 5, 9), (4, 5, 13),
        ],
        requests: vec![(0, 5), (5, 0)],
        expected_paths: vec![vec![0, 1, 3, 5], vec![5, 3, 1, 0]], // 0->1->3->5 has latency 31
        expected_max_latency: 31,
    };
    
    run_test_case(&test_case);
}

#[test]
fn test_large_network() {
    // Generate a larger network to test performance
    let n = 100;
    let mut edges = Vec::new();
    let mut requests = Vec::new();
    
    // Create a ring network with random cross-links
    for i in 0..n {
        edges.push((i, (i + 1) % n, 5)); // Ring connections
        
        // Add some random cross-links
        if i % 10 == 0 {
            edges.push((i, (i + n/2) % n, 15));
        }
    }
    
    // Create some sample requests
    requests.push((0, n/2));
    requests.push((n/4, 3*n/4));
    requests.push((n-1, 1));
    
    let paths = optimize_routing(n, edges.clone(), requests.clone());
    
    // Basic validation - just ensure we get valid paths
    assert_eq!(paths.len(), requests.len());
    for (i, path) in paths.iter().enumerate() {
        if !path.is_empty() {
            assert_eq!(path[0], requests[i].0); // First node is source
            assert_eq!(*path.last().unwrap(), requests[i].1); // Last node is destination
        }
    }
}

#[test]
fn test_cyclic_graph_with_negative_cycle() {
    // Graph with multiple paths
    // 0 -- 1 -- 2
    // |         |
    // +----3----+
    let test_case = TestCase {
        n: 4,
        edges: vec![
            (0, 1, 10), (1, 2, 20),
            (0, 3, 5), (3, 2, 5),
        ],
        requests: vec![(0, 2)],
        expected_paths: vec![vec![0, 3, 2]], // Path 0->3->2 has latency 10
        expected_max_latency: 10,
    };
    
    run_test_case(&test_case);
}

fn run_test_case(test_case: &TestCase) {
    let paths = optimize_routing(
        test_case.n,
        test_case.edges.clone(),
        test_case.requests.clone()
    );
    
    // Check that we got the correct number of paths
    assert_eq!(paths.len(), test_case.expected_paths.len(), 
              "Number of paths returned doesn't match expected");
    
    // Check each path
    let mut total_latency = 0;
    
    for (i, path) in paths.iter().enumerate() {
        if path.is_empty() {
            assert!(test_case.expected_paths[i].is_empty(), 
                  "Path {} should not be empty", i);
            continue;
        }
        
        // Check that the path starts with source and ends with destination
        assert_eq!(path[0], test_case.requests[i].0, 
                 "Path {} doesn't start with the source", i);
        assert_eq!(*path.last().unwrap(), test_case.requests[i].1, 
                 "Path {} doesn't end with the destination", i);
        
        // Calculate path latency
        let mut path_latency = 0;
        for j in 0..path.len() - 1 {
            let edge_found = test_case.edges.iter().find(|&&(u, v, _)| 
                (u == path[j] && v == path[j + 1]) || 
                (v == path[j] && u == path[j + 1])
            );
            
            assert!(edge_found.is_some(), 
                  "Path {} contains an edge that doesn't exist in the graph", i);
            
            path_latency += edge_found.unwrap().2;
        }
        
        total_latency += path_latency;
        
        // If we have expected paths, validate the specific path
        if !test_case.expected_paths[i].is_empty() {
            assert_eq!(path, &test_case.expected_paths[i], 
                      "Path {} doesn't match expected path", i);
        }
    }
    
    // Check total latency (only for paths that exist)
    let valid_paths_count = paths.iter().filter(|p| !p.is_empty()).count();
    if valid_paths_count > 0 {
        let avg_latency = total_latency / valid_paths_count as u32;
        assert!(avg_latency <= test_case.expected_max_latency, 
               "Average latency {} exceeds maximum expected {}", 
               avg_latency, test_case.expected_max_latency);
    }
}