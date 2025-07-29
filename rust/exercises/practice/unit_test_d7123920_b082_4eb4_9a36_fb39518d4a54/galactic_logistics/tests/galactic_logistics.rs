use galactic_logistics::{Network, RoutingResult};

#[test]
fn test_single_route_basic() {
    let mut network = Network::new();
    // Add a route from station 1 to 2 with travel time 10 and capacity 200.
    let add_msg = network.add_route(1, 2, 10, 200);
    assert_eq!(add_msg, "Trade route added");
    
    let result = network.find_route(1, 2, 150, &vec![]);
    match result {
        Ok(RoutingResult::Single(route)) => {
            assert_eq!(route, vec![1, 2]);
        }
        Ok(RoutingResult::Split(_)) => {
            panic!("Expected a single route but received cargo splitting.");
        }
        Err(msg) => {
            panic!("Expected a valid route but got error: {}", msg);
        }
    }
}

#[test]
fn test_blocked_route() {
    let mut network = Network::new();
    // Add a route from station 1 to 2.
    let add_msg = network.add_route(1, 2, 10, 200);
    assert_eq!(add_msg, "Trade route added");
    
    // Block the route from 1 to 2.
    let block_msg = network.block_route(1, 2);
    assert_eq!(block_msg, "Trade route blocked");
    
    // Attempt to find a route while the route is blocked.
    let result = network.find_route(1, 2, 150, &vec![(1, 2)]);
    if let Err(msg) = result {
        assert_eq!(msg, "No route available");
    } else {
        panic!("Expected an error due to blocked route.");
    }
}

#[test]
fn test_update_routes() {
    let mut network = Network::new();
    // Add two routes from station 1 to 2.
    let msg1 = network.add_route(1, 2, 10, 100);
    assert_eq!(msg1, "Trade route added");
    let msg2 = network.add_route(1, 2, 20, 150);
    assert_eq!(msg2, "Trade route added");

    // Attempt to find a route for cargo 120; should choose a route with enough capacity.
    let result = network.find_route(1, 2, 120, &vec![]);
    match result {
        Ok(RoutingResult::Single(route)) => {
            // Since both routes use stations [1,2], we expect the returned route to be [1,2].
            assert_eq!(route, vec![1, 2]);
        }
        _ => panic!("Expected a single route with adequate capacity."),
    }

    // Remove the second route which has capacity 150.
    let remove_msg = network.remove_route(1, 2, 20, 150);
    assert_eq!(remove_msg, "Trade route removed");

    // Now the remaining route cannot handle a cargo of 120 (capacity is 100).
    let result = network.find_route(1, 2, 120, &vec![]);
    if let Err(msg) = result {
        assert_eq!(msg, "Cargo exceeds network capacity");
    } else {
        panic!("Expected an error due to insufficient capacity after removal.");
    }
}

#[test]
fn test_cargo_splitting() {
    let mut network = Network::new();
    // Create two distinct routes from station 1 to 5:
    // Route A: 1 -> 2 -> 5 with total travel time = 5 + 10 = 15 and capacity = 80.
    // Route B: 1 -> 3 -> 5 with total travel time = 10 + 10 = 20 and capacity = 60.
    let add_msg_a1 = network.add_route(1, 2, 5, 80);
    assert_eq!(add_msg_a1, "Trade route added");
    let add_msg_a2 = network.add_route(2, 5, 10, 80);
    assert_eq!(add_msg_a2, "Trade route added");

    let add_msg_b1 = network.add_route(1, 3, 10, 60);
    assert_eq!(add_msg_b1, "Trade route added");
    let add_msg_b2 = network.add_route(3, 5, 10, 60);
    assert_eq!(add_msg_b2, "Trade route added");

    // Request a cargo of 120, which cannot be transported by a single route.
    let result = network.find_route(1, 5, 120, &vec![]);
    match result {
        Ok(RoutingResult::Split(routes)) => {
            // Expect two splits.
            assert_eq!(routes.len(), 2);
            let mut total_cargo = 0;
            for (route, cargo) in &routes {
                // Each route must start with 1 and end with 5.
                assert_eq!(route.first(), Some(&1));
                assert_eq!(route.last(), Some(&5));
                total_cargo += cargo;
                // Verify capacity constraints per known route.
                if *route == vec![1, 2, 5] {
                    assert!(*cargo <= 80);
                } else if *route == vec![1, 3, 5] {
                    assert!(*cargo <= 60);
                } else {
                    panic!("Unexpected route encountered: {:?}", route);
                }
            }
            assert_eq!(total_cargo, 120);
        },
        Ok(RoutingResult::Single(_)) => {
            panic!("Expected cargo splitting, but a single route was returned.");
        },
        Err(msg) => {
            panic!("Expected split routes but encountered error: {}", msg);
        }
    }
}

#[test]
fn test_unblock_route() {
    let mut network = Network::new();
    // Add a route from station 1 to 5 via station 4.
    let msg1 = network.add_route(1, 4, 8, 100);
    assert_eq!(msg1, "Trade route added");
    let msg2 = network.add_route(4, 5, 12, 100);
    assert_eq!(msg2, "Trade route added");

    // Block the route from 1 to 4.
    let block_msg = network.block_route(1, 4);
    assert_eq!(block_msg, "Trade route blocked");

    // Attempt to find the route with the blocked segment.
    let result_blocked = network.find_route(1, 5, 80, &vec![(1, 4)]);
    if let Err(msg) = result_blocked {
        assert_eq!(msg, "No route available");
    } else {
        panic!("Expected an error due to the blocked route.");
    }

    // Unblock the route and verify the route is now available.
    let unblock_msg = network.unblock_route(1, 4);
    assert_eq!(unblock_msg, "Trade route unblocked");
    let result = network.find_route(1, 5, 80, &vec![]);
    match result {
        Ok(RoutingResult::Single(route)) => {
            assert_eq!(route, vec![1, 4, 5]);
        }
        _ => panic!("Expected a single route after unblocking the route."),
    }
}