use resource_route::find_route;

#[test]
fn test_valid_route_shorter_path() {
    // Test with two possible paths:
    // Path A: 0 -> 1 -> 4 with cost 5+10 = 15, max resource = max(5,15,30)=30.
    // Path B: 0 -> 2 -> 3 -> 4 with cost 3+4+5 = 12, max resource = max(5,10,20,30)=30.
    // Expected: Since both have same max resource usage (30), choose the shorter path.
    // Path A has 2 edges while Path B has 3 edges.
    let n = 5;
    let resource_limits = vec![5, 15, 10, 20, 30];
    let edges = vec![
        (0, 1, 5),
        (1, 4, 10),
        (0, 2, 3),
        (2, 3, 4),
        (3, 4, 5)
    ];
    let start_node = 0;
    let end_node = 4;
    let required_resource = 25;
    let max_total_cost = 20;
    
    let result = find_route(n, resource_limits.clone(), edges.clone(), start_node, end_node, required_resource, max_total_cost);
    
    let expected_resource_usage = 30;
    let expected_path = vec![0, 1, 4];
    
    assert!(result.is_some(), "Expected a valid route, got None");
    let (res_usage, path) = result.unwrap();
    assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match");
    assert_eq!(path, expected_path, "Path does not match expected shorter path");
}

#[test]
fn test_no_route_due_to_cost() {
    // Test where the only available path exceeds max_total_cost.
    let n = 3;
    let resource_limits = vec![20, 30, 40];
    let edges = vec![
        (0, 1, 100),
        (1, 2, 100)
    ];
    let start_node = 0;
    let end_node = 2;
    let required_resource = 35;
    let max_total_cost = 50;
    
    let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
    assert!(result.is_none(), "Expected None due to cost constraint, but got a route");
}

#[test]
fn test_insufficient_destination_resource() {
    // Test where the destination node does not have enough resources.
    let n = 3;
    let resource_limits = vec![50, 60, 20]; // destination node has 20, which is less than required_resource of 25.
    let edges = vec![
        (0, 1, 10),
        (1, 2, 10)
    ];
    let start_node = 0;
    let end_node = 2;
    let required_resource = 25;
    let max_total_cost = 50;
    
    let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
    assert!(result.is_none(), "Expected None due to insufficient destination resource, but got a route");
}

#[test]
fn test_multiple_paths_different_resource_usage() {
    // Test with two paths having different maximum resource usages:
    // Path A: 0 -> 1 -> 3 with cost 5+15=20, max resource = max(10,20,30)=30.
    // Path B: 0 -> 2 -> 3 with cost 10+5=15, max resource = max(10,40,30)=40.
    // Expected optimal is Path A.
    let n = 4;
    let resource_limits = vec![10, 20, 40, 30];
    let edges = vec![
        (0, 1, 5),
        (1, 3, 15),
        (0, 2, 10),
        (2, 3, 5)
    ];
    let start_node = 0;
    let end_node = 3;
    let required_resource = 25;
    let max_total_cost = 30;
    
    let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
    
    let expected_resource_usage = 30;
    let expected_path = vec![0, 1, 3];
    
    assert!(result.is_some(), "Expected a valid route, got None");
    let (res_usage, path) = result.unwrap();
    assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match the expected optimal value");
    assert_eq!(path, expected_path, "Path does not match the expected optimal path");
}

#[test]
fn test_start_equals_end() {
    // Test where start and end nodes are the same.
    let n = 1;
    let resource_limits = vec![100];
    let edges: Vec<(usize, usize, u64)> = vec![];
    let start_node = 0;
    let end_node = 0;
    let required_resource = 50;
    let max_total_cost = 0;
    
    let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
    
    // The only path is [0] and resource usage equals resource_limits[0] = 100.
    let expected_resource_usage = 100;
    let expected_path = vec![0];
    
    assert!(result.is_some(), "Expected a valid route for start equals end, got None");
    let (res_usage, path) = result.unwrap();
    assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match for start equals end case");
    assert_eq!(path, expected_path, "Path does not match for start equals end case");
}

#[test]
fn test_tie_break_fewer_edges() {
    // Test when multiple paths yield the same maximum resource usage,
    // prefer the one with fewer edges.
    // Available paths:
    // Path A: 0 -> 1 -> 4 with cost 5+10 = 15, max resource = max(10,50,60)=60.
    // Path B: 0 -> 4 direct with cost 25, max resource = max(10,60)=60.
    // Path C: 0 -> 2 -> 3 -> 4 with cost 5+5+10 = 20, max resource = max(10,20,40,60)=60.
    // Expected optimal: Path B due to having only 1 edge.
    let n = 5;
    let resource_limits = vec![10, 50, 20, 40, 60];
    let edges = vec![
        (0, 1, 5),
        (1, 4, 10),
        (0, 2, 5),
        (2, 3, 5),
        (3, 4, 10),
        (0, 4, 25)
    ];
    let start_node = 0;
    let end_node = 4;
    let required_resource = 50;
    let max_total_cost = 30;
    
    let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
    
    let expected_resource_usage = 60;
    let expected_path = vec![0, 4];
    
    assert!(result.is_some(), "Expected a valid route, got None");
    let (res_usage, path) = result.unwrap();
    assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match for tie-break case");
    assert_eq!(path, expected_path, "Path does not match expected fewer-edge path");
}