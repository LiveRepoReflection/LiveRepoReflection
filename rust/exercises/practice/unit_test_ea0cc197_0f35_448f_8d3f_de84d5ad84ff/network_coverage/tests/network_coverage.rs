use network_coverage::max_population_coverage;

const EPS: f64 = 1e-6;

#[test]
fn test_empty_graph() {
    let graph: Vec<(usize, usize, usize)> = vec![];
    let population: Vec<usize> = vec![];
    let budget = 100;
    let radius = 10;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 0.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}

#[test]
fn test_budget_zero() {
    // With budget 0, only one base station is allowed. The optimal choice is the node with the maximum population.
    let graph = vec![(0, 1, 2), (1, 2, 2), (0, 2, 4)];
    let population = vec![30, 10, 20];
    let budget = 0;
    let radius = 3;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 30.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}

#[test]
fn test_single_node() {
    // A single node with no edges should return its own population value.
    let graph: Vec<(usize, usize, usize)> = vec![];
    let population = vec![100];
    let budget = 50;
    let radius = 5;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 100.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}

#[test]
fn test_cycle_graph() {
    // Four nodes arranged in a cycle. Optimal selection is to choose two opposite nodes.
    // For instance, choosing nodes 0 and 2:
    // - The distance between 0 and 2 is 10 (> R = 6) so there is no interference.
    // - Total effective coverage = 100 + 80 = 180.
    let graph = vec![
        (0, 1, 5),
        (1, 2, 5),
        (2, 3, 5),
        (3, 0, 5),
        (0, 2, 8),
        (1, 3, 8)
    ];
    let population = vec![100, 50, 80, 20];
    let budget = 10;
    let radius = 6;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 180.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}

#[test]
fn test_complete_graph() {
    // A complete graph of 3 nodes where every two nodes are connected with cost 1.
    // The MST cost for spanning three nodes is 1+1 = 2 (which is equal to the budget).
    // All nodes interfere with each other because all pairwise distances (1) are within R = 2.
    // Effective coverage of each node becomes 50/3, summing up to 50.
    let graph = vec![(0, 1, 1), (1, 2, 1), (0, 2, 1)];
    let population = vec![50, 50, 50];
    let budget = 2;
    let radius = 2;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 50.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}

#[test]
fn test_chain_graph() {
    // A chain graph of 5 nodes with edges of cost 2.
    // With radius R = 3, adjacent nodes interfere, but nodes separated by one vertex do not.
    // The optimal selection is to deploy nodes 2 and 4:
    // - The cable to connect them goes through node 3 with cost 2+2 = 4, which is within the budget 6.
    // - Since the distance between nodes 2 and 4 is 4 (> R), they do not interfere.
    // Total effective coverage = 30 + 50 = 80.
    let graph = vec![(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2)];
    let population = vec![10, 20, 30, 40, 50];
    let budget = 6;
    let radius = 3;
    let result = max_population_coverage(graph, population, budget, radius);
    let expected = 80.0;
    assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
}