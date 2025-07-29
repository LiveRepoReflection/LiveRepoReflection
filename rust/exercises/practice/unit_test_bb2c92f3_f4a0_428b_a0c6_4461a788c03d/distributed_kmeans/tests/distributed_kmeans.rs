use distributed_kmeans::distributed_kmeans;

fn approx_equal(a: &Vec<Vec<f64>>, b: &Vec<Vec<f64>>, eps: f64) -> bool {
    if a.len() != b.len() {
        return false;
    }
    for (vec_a, vec_b) in a.iter().zip(b.iter()) {
        if vec_a.len() != vec_b.len() {
            return false;
        }
        for (x, y) in vec_a.iter().zip(vec_b.iter()) {
            if (x - y).abs() > eps {
                return false;
            }
        }
    }
    true
}

#[test]
fn test_single_node() {
    let data = vec![
        vec![1.0, 2.0],
        vec![1.5, 1.8],
        vec![5.0, 8.0],
        vec![8.0, 8.0],
    ];
    let num_nodes = 1;
    let k = 2;
    let iterations = 5;
    let initial_centroids = vec![vec![1.0, 2.0], vec![5.0, 8.0]];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    // Expected centroids are the averages of the two clusters:
    // cluster1: average of [1.0,2.0] and [1.5,1.8], cluster2: average of [5.0,8.0] and [8.0,8.0]
    let expected = vec![vec![(1.0 + 1.5) / 2.0, (2.0 + 1.8) / 2.0], vec![(5.0 + 8.0) / 2.0, (8.0 + 8.0) / 2.0]];
    assert!(approx_equal(&result, &expected, 0.1), "Single node test failed. Expected {:?}, got {:?}", expected, result);
}

#[test]
fn test_multiple_nodes() {
    let data = vec![
        vec![1.0, 1.0],
        vec![2.0, 1.0],
        vec![1.0, 2.0],
        vec![2.0, 2.0],
        vec![10.0, 10.0],
        vec![11.0, 10.0],
        vec![10.0, 11.0],
        vec![11.0, 11.0],
    ];
    let num_nodes = 2;
    let k = 2;
    let iterations = 5;
    let initial_centroids = vec![vec![1.0, 1.0], vec![10.0, 10.0]];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    // Expected centroids: one for lower 2x2 group and one for upper 2x2 group.
    let expected = vec![vec![1.5, 1.5], vec![10.5, 10.5]];
    assert!(approx_equal(&result, &expected, 0.1), "Multiple nodes test failed. Expected {:?}, got {:?}", expected, result);
}

#[test]
fn test_empty_data() {
    let data: Vec<Vec<f64>> = vec![];
    let num_nodes = 1;
    let k = 0;
    let iterations = 3;
    let initial_centroids: Vec<Vec<f64>> = vec![];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    let expected: Vec<Vec<f64>> = vec![];
    assert!(approx_equal(&result, &expected, 0.0), "Empty data test failed. Expected {:?}, got {:?}", expected, result);
}

#[test]
fn test_k_larger_than_data() {
    let data = vec![
        vec![1.0, 2.0],
        vec![3.0, 4.0],
    ];
    let num_nodes = 1;
    let k = 3;
    let iterations = 3;
    let initial_centroids = vec![vec![1.0, 2.0], vec![3.0, 4.0], vec![5.0, 6.0]];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    // When k is larger than the available data points, some centroids may not receive any assignments.
    // In such cases, the centroids without assignments should remain as their initial value.
    let expected = vec![vec![1.0, 2.0], vec![3.0, 4.0], vec![5.0, 6.0]];
    assert!(approx_equal(&result, &expected, 0.1), "K larger than data test failed. Expected {:?}, got {:?}", expected, result);
}

#[test]
fn test_node_with_no_assignments() {
    // This simulates a scenario where one node might not contribute to a particular cluster.
    let data = vec![
        vec![1.0, 1.0],
        vec![1.1, 1.0],
        vec![10.0, 10.0],
    ];
    // Partitioning into two nodes; one node gets the two points from the lower cluster,
    // and the other gets the single point from the upper cluster.
    let num_nodes = 2;
    let k = 2;
    let iterations = 5;
    let initial_centroids = vec![vec![1.0, 1.0], vec![10.0, 10.0]];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    let expected = vec![vec![(1.0 + 1.1) / 2.0, 1.0], vec![10.0, 10.0]];
    assert!(approx_equal(&result, &expected, 0.1), "Node with no assignments test failed. Expected {:?}, got {:?}", expected, result);
}

#[test]
fn test_high_iterations() {
    let data = vec![
        vec![0.0, 0.0],
        vec![0.1, 0.1],
        vec![10.0, 10.0],
        vec![10.1, 10.1],
    ];
    let num_nodes = 2;
    let k = 2;
    let iterations = 20;
    let initial_centroids = vec![vec![0.0, 0.0], vec![10.0, 10.0]];
    let result = distributed_kmeans(data.clone(), num_nodes, k, iterations, initial_centroids.clone());
    // Expected centroids are the averages of the two clusters.
    let expected = vec![vec![(0.0 + 0.1) / 2.0, (0.0 + 0.1) / 2.0], vec![(10.0 + 10.1) / 2.0, (10.0 + 10.1) / 2.0]];
    assert!(approx_equal(&result, &expected, 0.1), "High iterations test failed. Expected {:?}, got {:?}", expected, result);
}