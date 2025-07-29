use risky_path::find_optimal_path;

#[test]
fn test_direct_path() {
    // Simple grid with no dynamic obstacles.
    let grid = vec![
        vec!['.', '.', '.'],
        vec!['.', '.', '.'],
        vec!['.', '.', '.'],
    ];
    let risk_grid = vec![
        vec![1, 1, 1],
        vec![1, 1, 1],
        vec![1, 1, 1],
    ];
    let obstacle_paths: Vec<Vec<(usize, usize)>> = Vec::new();
    let start = (0, 0);
    let destination = (2, 2);
    let t = 5;
    let result = find_optimal_path(grid, risk_grid, obstacle_paths, start, destination, t);
    assert!(result.is_some());
    let path = result.unwrap();
    // Check that the path starts and ends at the correct positions.
    assert_eq!(path.first().cloned().unwrap(), start);
    assert_eq!(path.last().cloned().unwrap(), destination);
}

#[test]
fn test_obstacle_collision_avoidance() {
    // Grid with a static obstacle and one dynamic obstacle.
    let grid = vec![
        vec!['.', '.', '.', '.'],
        vec!['.', '#', '.', '.'],
        vec!['.', '.', '.', '.'],
        vec!['.', '.', '.', '.'],
    ];
    let risk_grid = vec![
        vec![1, 2, 1, 1],
        vec![1, 5, 2, 1],
        vec![1, 2, 1, 2],
        vec![1, 1, 1, 1],
    ];
    // One dynamic obstacle with a looping path.
    let obstacle_paths = vec![
        vec![(0, 2), (1, 2), (2, 2), (2, 1)]
    ];
    let start = (0, 0);
    let destination = (3, 3);
    let t = 10;
    let result = find_optimal_path(grid, risk_grid, obstacle_paths, start, destination, t);
    assert!(result.is_some());
    let path = result.unwrap();
    // Verify start and destination
    assert_eq!(path.first().cloned().unwrap(), start);
    assert_eq!(path.last().cloned().unwrap(), destination);
}

#[test]
fn test_unreachable_destination() {
    // Grid where the destination is blocked by static obstacles.
    let grid = vec![
        vec!['.', '#', '.'],
        vec!['#', '#', '.'],
        vec!['.', '#', '.'],
    ];
    let risk_grid = vec![
        vec![1, 1, 1],
        vec![1, 1, 1],
        vec![1, 1, 1],
    ];
    let obstacle_paths: Vec<Vec<(usize, usize)>> = Vec::new();
    let start = (0, 0);
    let destination = (2, 2);
    let t = 10;
    let result = find_optimal_path(grid, risk_grid, obstacle_paths, start, destination, t);
    assert!(result.is_none());
}

#[test]
fn test_insufficient_time() {
    // Grid with no obstacles but insufficient time steps to reach the destination.
    let grid = vec![
        vec!['.', '.', '.'],
        vec!['.', '.', '.'],
        vec!['.', '.', '.'],
    ];
    let risk_grid = vec![
        vec![1, 1, 1],
        vec![1, 1, 1],
        vec![1, 1, 1],
    ];
    let obstacle_paths: Vec<Vec<(usize, usize)>> = Vec::new();
    let start = (0, 0);
    let destination = (2, 2);
    let t = 2; // Manhattan distance is 4, so it's impossible.
    let result = find_optimal_path(grid, risk_grid, obstacle_paths, start, destination, t);
    assert!(result.is_none());
}