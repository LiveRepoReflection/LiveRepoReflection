use std::collections::HashSet;

// This function signature is assumed to exist in your library.
// It takes the number of nodes (n), the desired number of partitions (k),
// and a vector of tuples representing the edges (u, v, cost). It returns a vector 
// of partitions, where each partition is represented as a vector of node IDs.
use net_partition::net_partition;

fn validate_partition(n: usize, k: usize, partitions: &Vec<Vec<usize>>) {
    // Check that exactly k partitions exist.
    assert_eq!(
        partitions.len(),
        k,
        "Number of partitions (found {}) must be equal to k ({}).",
        partitions.len(),
        k
    );

    // Check that all nodes [0, n) are present exactly once.
    let mut nodes_present = HashSet::new();
    for partition in partitions {
        for &node in partition {
            nodes_present.insert(node);
        }
    }
    assert_eq!(
        nodes_present.len(),
        n,
        "All nodes must be present exactly once. Expected {} nodes, found {}.",
        n,
        nodes_present.len()
    );
    for node in 0..n {
        assert!(
            nodes_present.contains(&node),
            "Missing node: {} in partitions.",
            node
        );
    }

    // Check balanced partition sizes: each partition must have a size between floor(n/k) and ceil(n/k).
    let lower = n / k;
    let upper = if n % k == 0 { lower } else { lower + 1 };
    let mut count_upper = 0;
    for partition in partitions {
        let size = partition.len();
        assert!(
            size >= lower && size <= upper,
            "Partition size {} is not within the allowed range [{}:{}].",
            size,
            lower,
            upper
        );
        if size == upper {
            count_upper += 1;
        }
    }
    let expected_upper = n % k;
    if expected_upper > 0 {
        assert_eq!(
            count_upper, expected_upper,
            "Expected {} partitions of size {}, but found {}.",
            expected_upper, upper, count_upper
        );
    }
}

#[test]
fn test_single_node() {
    let n = 1;
    let k = 1;
    let edges = vec![];
    let partitions = net_partition(n, k, edges);
    validate_partition(n, k, &partitions);
}

#[test]
fn test_triangle_graph() {
    // Graph: triangle between nodes 0, 1, 2.
    // Expected balanced partitions: when k = 2, partitions sizes should be 1 and 2.
    let n = 3;
    let k = 2;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 15),
        (0, 2, 20)
    ];
    let partitions = net_partition(n, k, edges);
    validate_partition(n, k, &partitions);
}

#[test]
fn test_disconnected_graph() {
    // Graph with two disconnected components: {0,1} and {2,3}.
    // For n = 4 and k = 2, the only balanced partition is two groups of 2 nodes.
    let n = 4;
    let k = 2;
    let edges = vec![
        (0, 1, 5),
        (2, 3, 5)
    ];
    let partitions = net_partition(n, k, edges);
    validate_partition(n, k, &partitions);

    // Check that at least one partition matches one of the components.
    let partition_sets: Vec<HashSet<_>> = partitions
        .iter()
        .map(|p| p.iter().copied().collect())
        .collect();
    let comp1: HashSet<_> = vec![0, 1].into_iter().collect();
    let comp2: HashSet<_> = vec![2, 3].into_iter().collect();
    let mut found_component = false;
    for p in &partition_sets {
        if p == &comp1 || p == &comp2 {
            found_component = true;
            break;
        }
    }
    assert!(
        found_component,
        "Expected at least one partition to match a connected component."
    );
}

#[test]
fn test_star_graph() {
    // Star graph: center node 0 connected to nodes 1, 2, 3, 4.
    // For n = 5 and k = 2, partitions should be balanced with sizes 2 and 3.
    let n = 5;
    let k = 2;
    let edges = vec![
        (0, 1, 1),
        (0, 2, 1),
        (0, 3, 1),
        (0, 4, 1)
    ];
    let partitions = net_partition(n, k, edges);
    validate_partition(n, k, &partitions);
}

#[test]
fn test_each_node_in_own_partition() {
    // When k equals n, each partition has exactly one node.
    let n = 5;
    let k = 5;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 10),
        (2, 3, 10),
        (3, 4, 10),
        (4, 0, 10)
    ];
    let partitions = net_partition(n, k, edges);
    validate_partition(n, k, &partitions);
    for partition in partitions {
        assert_eq!(
            partition.len(),
            1,
            "Each partition should contain exactly one node when k equals n."
        );
    }
}