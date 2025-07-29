use optimal_pathways::find_optimal_path;

#[test]
fn test_basic_path() {
    let n = 3;
    let edges = vec![
        (0, 1, 10, 5, 100),  // (from, to, time, cost, capacity)
        (1, 2, 20, 10, 50),
        (0, 2, 30, 15, 75),
    ];
    let result = find_optimal_path(n, edges, 0, 2, 40, 40);
    assert_eq!(result, Some(15));
}

#[test]
fn test_no_path_exists() {
    let n = 3;
    let edges = vec![
        (0, 1, 10, 5, 100),
        (1, 0, 10, 5, 100),
    ];
    let result = find_optimal_path(n, edges, 0, 2, 100, 50);
    assert_eq!(result, None);
}

#[test]
fn test_exceeds_weight_capacity() {
    let n = 2;
    let edges = vec![
        (0, 1, 10, 5, 40),
    ];
    let result = find_optimal_path(n, edges, 0, 1, 100, 50);
    assert_eq!(result, None);
}

#[test]
fn test_exceeds_time_limit() {
    let n = 2;
    let edges = vec![
        (0, 1, 100, 5, 100),
    ];
    let result = find_optimal_path(n, edges, 0, 1, 50, 40);
    assert_eq!(result, None);
}

#[test]
fn test_same_source_destination() {
    let n = 1;
    let edges = vec![];
    let result = find_optimal_path(n, edges, 0, 0, 100, 50);
    assert_eq!(result, Some(0));
}

#[test]
fn test_multiple_paths() {
    let n = 4;
    let edges = vec![
        (0, 1, 10, 10, 100),
        (1, 3, 20, 20, 100),
        (0, 2, 15, 15, 100),
        (2, 3, 15, 15, 100),
    ];
    let result = find_optimal_path(n, edges, 0, 3, 40, 50);
    assert_eq!(result, Some(30));
}

#[test]
fn test_multiple_edges_between_same_nodes() {
    let n = 2;
    let edges = vec![
        (0, 1, 10, 20, 100),
        (0, 1, 20, 10, 100),
        (0, 1, 30, 5, 40),
    ];
    let result = find_optimal_path(n, edges, 0, 1, 25, 50);
    assert_eq!(result, Some(10));
}

#[test]
fn test_complex_network() {
    let n = 5;
    let edges = vec![
        (0, 1, 10, 10, 100),
        (1, 2, 10, 10, 100),
        (2, 4, 10, 10, 100),
        (0, 3, 15, 5, 100),
        (3, 4, 15, 5, 100),
        (0, 4, 50, 5, 100),
    ];
    let result = find_optimal_path(n, edges, 0, 4, 35, 60);
    assert_eq!(result, Some(10));
}

#[test]
fn test_large_weights() {
    let n = 2;
    let edges = vec![
        (0, 1, 10, 10, 1_000_000),
    ];
    let result = find_optimal_path(n, edges, 0, 1, 15, 999_999);
    assert_eq!(result, Some(10));
}

#[test]
fn test_cycle_handling() {
    let n = 4;
    let edges = vec![
        (0, 1, 10, 10, 100),
        (1, 2, 10, 10, 100),
        (2, 1, 10, 5, 100),
        (2, 3, 10, 10, 100),
    ];
    let result = find_optimal_path(n, edges, 0, 3, 40, 50);
    assert_eq!(result, Some(30));
}