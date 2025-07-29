use route_optim::optimal_route;

fn calculate_route_metrics(
    route: &[usize],
    edges: &[(usize, usize, u32, u32)],
) -> Option<(u32, u32)> {
    // Build an adjacency list mapping from (from, to) -> (time, cost)
    let mut adj = std::collections::HashMap::new();
    for &(from, to, time, cost) in edges {
        // If multiple edges exist, choose the one with minimal time; if tie, minimal cost.
        let entry = adj.entry((from, to)).or_insert((time, cost));
        if time < entry.0 || (time == entry.0 && cost < entry.1) {
            *entry = (time, cost);
        }
    }
    let mut total_time = 0;
    let mut total_cost = 0;
    for pair in route.windows(2) {
        let from = pair[0];
        let to = pair[1];
        if let Some(&(time, cost)) = adj.get(&(from, to)) {
            total_time += time;
            total_cost += cost;
        } else {
            return None; // invalid edge in route
        }
    }
    Some((total_time, total_cost))
}

fn route_contains_all(route: &[usize], destinations: &[usize]) -> bool {
    for &dest in destinations {
        if !route.contains(&dest) {
            return false;
        }
    }
    true
}

#[test]
fn test_single_destination_example() {
    // Example provided in description:
    let num_intersections = 4;
    let edges = vec![
        (0, 1, 10, 5),
        (0, 2, 15, 2),
        (1, 3, 12, 3),
        (2, 3, 10, 4),
        (3, 0, 5, 1),
    ];
    let destination_nodes = vec![3];
    let time_limit = 50;
    let budget = 10;

    let route_option = optimal_route(num_intersections, edges.clone(), destination_nodes.clone(), time_limit, budget);
    assert!(route_option.is_some(), "Expected a valid route, got None");
    let route = route_option.unwrap();
    // Check that route starts and ends with depot (node 0)
    assert_eq!(route.first(), Some(&0));
    assert_eq!(route.last(), Some(&0));
    // Check that the route visits all required destination nodes once at least.
    assert!(route_contains_all(&route, &destination_nodes), "Route does not visit all destination nodes");
    // Validate metrics are within constraints.
    let metrics = calculate_route_metrics(&route, &edges).expect("Route contains an invalid edge");
    assert!(metrics.0 <= time_limit, "Total travel time {} exceeds time limit {}", metrics.0, time_limit);
    assert!(metrics.1 <= budget, "Total toll cost {} exceeds budget {}", metrics.1, budget);
}

#[test]
fn test_multiple_destinations() {
    // A scenario with multiple destination nodes.
    let num_intersections = 6;
    let edges = vec![
        // from, to, time, cost
        (0, 1, 5, 2),
        (1, 2, 10, 1),
        (2, 5, 5, 2),
        (0, 3, 7, 3),
        (3, 4, 5, 2),
        (4, 5, 7, 3),
        (1, 3, 3, 1),
        (2, 4, 2, 2),
        (4, 0, 10, 5),
        (5, 0, 8, 2),
        (3, 0, 12, 4),
    ];
    let destination_nodes = vec![2, 4];
    let time_limit = 40;
    let budget = 15;
    
    let route_option = optimal_route(num_intersections, edges.clone(), destination_nodes.clone(), time_limit, budget);
    assert!(route_option.is_some(), "Expected a valid route, got None");
    let route = route_option.unwrap();
    assert_eq!(route.first(), Some(&0));
    assert_eq!(route.last(), Some(&0));
    assert!(route_contains_all(&route, &destination_nodes));
    let metrics = calculate_route_metrics(&route, &edges).expect("Route contains an invalid edge"); 
    assert!(metrics.0 <= time_limit, "Total travel time {} exceeds time limit {}", metrics.0, time_limit);
    assert!(metrics.1 <= budget, "Total toll cost {} exceeds budget {}", metrics.1, budget);
}

#[test]
fn test_no_valid_route_due_to_time() {
    // Constraint is too tight for any route, expect None.
    let num_intersections = 4;
    let edges = vec![
        (0, 1, 20, 2),
        (1, 2, 20, 2),
        (2, 3, 20, 2),
        (3, 0, 20, 2),
        (0, 2, 50, 5),
    ];
    let destination_nodes = vec![2, 3];
    let time_limit = 50; // too low to complete any cycle including destinations.
    let budget = 20;
    
    let route_option = optimal_route(num_intersections, edges.clone(), destination_nodes.clone(), time_limit, budget);
    assert!(route_option.is_none(), "Expected no valid route due to time constraints");
}

#[test]
fn test_no_valid_route_due_to_budget() {
    // Constraint is too tight in terms of budget, expect None.
    let num_intersections = 4;
    let edges = vec![
        (0, 1, 5, 10),
        (1, 2, 5, 10),
        (2, 3, 5, 10),
        (3, 0, 5, 10),
        (0, 2, 7, 15),
    ];
    let destination_nodes = vec![2, 3];
    let time_limit = 30;
    let budget = 20; // Too little budget for any valid path.
    
    let route_option = optimal_route(num_intersections, edges.clone(), destination_nodes.clone(), time_limit, budget);
    assert!(route_option.is_none(), "Expected no valid route due to budget constraints");
}

#[test]
fn test_parallel_edges_and_cycles() {
    // Graph contains parallel edges and cycles. Ensure that the function picks the optimal route.
    let num_intersections = 5;
    let edges = vec![
        (0, 1, 3, 1),
        (0, 1, 5, 0), // parallel edge; suboptimal in time but lower cost.
        (1, 2, 4, 2),
        (2, 3, 6, 3),
        (3, 1, 2, 1), // cycle back to 1.
        (3, 4, 3, 2),
        (4, 0, 5, 2),
        (1, 4, 10, 0),
        (2, 4, 8, 5),
    ];
    let destination_nodes = vec![2, 4];
    let time_limit = 30;
    let budget = 10;
    
    let route_option = optimal_route(num_intersections, edges.clone(), destination_nodes.clone(), time_limit, budget);
    assert!(route_option.is_some(), "Expected a valid route in graph with cycles");
    let route = route_option.unwrap();
    assert_eq!(route.first(), Some(&0));
    assert_eq!(route.last(), Some(&0));
    assert!(route_contains_all(&route, &destination_nodes));
    let metrics = calculate_route_metrics(&route, &edges).expect("Route contains an invalid edge");
    assert!(metrics.0 <= time_limit, "Total travel time {} exceeds time limit {}", metrics.0, time_limit);
    assert!(metrics.1 <= budget, "Total toll cost {} exceeds budget {}", metrics.1, budget);
}