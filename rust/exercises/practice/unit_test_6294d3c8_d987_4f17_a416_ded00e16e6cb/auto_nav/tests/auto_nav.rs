use auto_nav::{Event, NavigationSystem};

#[test]
fn test_no_available_path() {
    let mut nav = NavigationSystem::new(3);
    let mut req = Event::NavigationRequest {
        start: 0,
        destination: 1,
        start_time: 0,
        end_time: 10,
        result: None,
    };
    nav.handle_event(&mut req);
    if let Event::NavigationRequest { result, .. } = req {
        assert!(result.is_none(), "Expected no valid path, but got {:?}", result);
    } else {
        panic!("Event type mismatch");
    }
}

#[test]
fn test_simple_navigation() {
    let mut nav = NavigationSystem::new(2);
    // Add a direct path from 0 to 1 with cost 5
    let add_event = Event::AddPath {
        src: 0,
        dst: 1,
        cost: 5,
    };
    nav.handle_event(&mut add_event.clone());
    
    let mut req = Event::NavigationRequest {
        start: 0,
        destination: 1,
        start_time: 0,
        end_time: 10,
        result: None,
    };
    nav.handle_event(&mut req);
    if let Event::NavigationRequest { result, .. } = req {
        assert_eq!(result, Some(5), "Expected path cost 5, but got {:?}", result);
    } else {
        panic!("Event type mismatch");
    }
}

#[test]
fn test_alternative_route_after_block() {
    let mut nav = NavigationSystem::new(3);
    // Setup paths:
    // Path 0->1 cost 2, Path 1->2 cost 2, Direct path 0->2 cost 10.
    let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 2 };
    let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 2 };
    let mut add_e3 = Event::AddPath { src: 0, dst: 2, cost: 10 };
    nav.handle_event(&mut add_e1);
    nav.handle_event(&mut add_e2);
    nav.handle_event(&mut add_e3);

    // Block the cheaper route edge: block 0->1 for duration 10.
    let mut block_event = Event::BlockPath {
        src: 0,
        dst: 1,
        duration: 10,
    };
    nav.handle_event(&mut block_event);

    // Navigation request from 0 to 2 with time window [0, 12]:
    let mut req = Event::NavigationRequest {
        start: 0,
        destination: 2,
        start_time: 0,
        end_time: 12,
        result: None,
    };
    nav.handle_event(&mut req);
    // Expect the system to use the direct edge 0->2 with cost 10 as the blocked route cannot be used.
    if let Event::NavigationRequest { result, .. } = req {
        assert_eq!(result, Some(10), "Expected path cost 10 using direct route, but got {:?}", result);
    } else {
        panic!("Event type mismatch");
    }
}

#[test]
fn test_navigation_after_unblock() {
    let mut nav = NavigationSystem::new(3);
    // Setup paths:
    // Path 0->1 cost 2, Path 1->2 cost 2, Direct path 0->2 cost 10.
    let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 2 };
    let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 2 };
    let mut add_e3 = Event::AddPath { src: 0, dst: 2, cost: 10 };
    nav.handle_event(&mut add_e1);
    nav.handle_event(&mut add_e2);
    nav.handle_event(&mut add_e3);

    // Block the edge 0->1 for duration 10, then immediately unblock it.
    let mut block_event = Event::BlockPath {
        src: 0,
        dst: 1,
        duration: 10,
    };
    nav.handle_event(&mut block_event);
    let mut unblock_event = Event::UnblockPath { src: 0, dst: 1 };
    nav.handle_event(&mut unblock_event);

    // Navigation request from 0 to 2 with time window [0, 10]:
    let mut req = Event::NavigationRequest {
        start: 0,
        destination: 2,
        start_time: 0,
        end_time: 10,
        result: None,
    };
    nav.handle_event(&mut req);
    // After unblocking, the cheaper route via node 1 (cost 2+2 = 4) should be usable.
    if let Event::NavigationRequest { result, .. } = req {
        assert_eq!(result, Some(4), "Expected path cost 4 using unblocked route, but got {:?}", result);
    } else {
        panic!("Event type mismatch");
    }
}

#[test]
fn test_remove_path() {
    let mut nav = NavigationSystem::new(3);
    // Setup paths:
    // Path 0->1 cost 3, Path 1->2 cost 3.
    let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 3 };
    let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 3 };
    nav.handle_event(&mut add_e1);
    nav.handle_event(&mut add_e2);

    // Remove the path 0->1
    let mut remove_event = Event::RemovePath { src: 0, dst: 1 };
    nav.handle_event(&mut remove_event);

    // Navigation request from 0 to 2 with time window [0, 10]:
    let mut req = Event::NavigationRequest {
        start: 0,
        destination: 2,
        start_time: 0,
        end_time: 10,
        result: None,
    };
    nav.handle_event(&mut req);
    // With the removed path, no valid route should exist.
    if let Event::NavigationRequest { result, .. } = req {
        assert!(result.is_none(), "Expected no valid path after removal, but got {:?}", result);
    } else {
        panic!("Event type mismatch");
    }
}