use dynamic_paths::DynamicPaths;

#[test]
fn test_initial_shortest_path() {
    // Grid:
    // 1 1 1
    // 1 100 1
    // 1 1 1
    let grid = vec![
        vec![1, 1, 1],
        vec![1, 100, 1],
        vec![1, 1, 1],
    ];
    // Starting source at (0, 0)
    let sources = vec![(0, 0)];
    let dp = DynamicPaths::new(grid, sources);
    // For allowed moves (up, down, left, right) with cost of a move equal to the cost
    // of the destination cell, one optimal path from (0,0) to (2,2) is:
    // (0,0) -> (0,1) [cost 1] -> (0,2) [cost 1] -> (1,2) [cost 1] -> (2,2) [cost 1]
    // Total cost = 1 + 1 + 1 + 1 = 4.
    let cost = dp.get_shortest_path(2, 2);
    assert_eq!(cost, 4);
}

#[test]
fn test_update_cost() {
    // Grid:
    // 1 1 1
    // 1 100 1
    // 1 1 1
    let grid = vec![
        vec![1, 1, 1],
        vec![1, 100, 1],
        vec![1, 1, 1],
    ];
    let sources = vec![(0, 0)];
    let mut dp = DynamicPaths::new(grid, sources);
    // Update two cells that are on one of the short paths:
    // Update (0,1) and (1,0) to a higher cost so that the cost increases along those routes.
    dp.update_cost(0, 1, 100);
    dp.update_cost(1, 0, 100);
    // Now, the optimal path from (0,0) to (2,2) avoids (0,1) and (1,0).
    // One possibility is: (0,0) -> (0,1) becomes expensive, so use:
    // (0,0) -> (0,1) [cost = 100] -> (0,2) [cost = 1] -> (1,2) [cost = 1] -> (2,2) [cost = 1]
    // Alternatively, (0,0) -> (1,0) [cost = 100] -> (2,0) [cost = 1] -> (2,1) [cost = 1] -> (2,2) [cost = 1]
    // So the expected minimal cost is 100 + 1 + 1 + 1 = 103.
    let cost = dp.get_shortest_path(2, 2);
    assert_eq!(cost, 103);
}

#[test]
fn test_update_sources() {
    // Grid:
    // 1 1 1
    // 1 1 1
    // 1 1 1
    let grid = vec![
        vec![1, 1, 1],
        vec![1, 1, 1],
        vec![1, 1, 1],
    ];
    // Initial source at (0, 0)
    let sources = vec![(0, 0)];
    let mut dp = DynamicPaths::new(grid, sources);
    // Verify that from (0,0) to (2,2): cost = (0,0)->(0,1)->(0,2)->(1,2)->(2,2) = 1+1+1+1 = 4.
    let cost_before = dp.get_shortest_path(2, 2);
    assert_eq!(cost_before, 4);
    // Update sources to only (2,2)
    dp.update_sources(vec![(2, 2)]);
    // Now, querying (2,2) should return 0 (since it's a source)
    let cost_at_source = dp.get_shortest_path(2, 2);
    assert_eq!(cost_at_source, 0);
    // Query a cell distant from (2,2), for example (0,0).
    // A valid minimal path from (2,2) to (0,0) with only up, down, left, right moves:
    // (2,2) -> (2,1) -> (2,0) -> (1,0) -> (0,0) equals 1+1+1+1 = 4.
    let cost_from_new_source = dp.get_shortest_path(0, 0);
    assert_eq!(cost_from_new_source, 4);
}

#[test]
fn test_no_source() {
    // Grid:
    // 1 2
    // 3 4
    let grid = vec![
        vec![1, 2],
        vec![3, 4],
    ];
    // Initialize with one source, then update to empty.
    let sources = vec![(0, 0)];
    let mut dp = DynamicPaths::new(grid, sources);
    // Update sources to empty vector.
    dp.update_sources(vec![]);
    // Query any cell (e.g., (1,1)) should return -1 since there are no valid sources.
    let cost = dp.get_shortest_path(1, 1);
    assert_eq!(cost, -1);
}

#[test]
fn test_query_out_of_bounds() {
    // Grid:
    // 1 1 1
    // 1 1 1
    // 1 1 1
    let grid = vec![
        vec![1, 1, 1],
        vec![1, 1, 1],
        vec![1, 1, 1],
    ];
    let sources = vec![(1, 1)];
    let dp = DynamicPaths::new(grid, sources);
    // Query a cell that is out of bounds. According to specification, if cell is outside the grid,
    // the method should handle it gracefully and return -1.
    let cost = dp.get_shortest_path(5, 5);
    assert_eq!(cost, -1);
}