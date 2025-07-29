use network_routing::network_routing;

#[test]
fn basic_routing() {
    let n = 5;
    let updates = vec![
        (0, 1, 2),
        (1, 2, 3),
        (0, 2, 6),
        (2, 3, 4),
        (3, 4, 5),
    ];
    let queries = vec![
        (0, 3, 3),
        (0, 4, 5),
        (1, 4, 2),
    ];
    let result = network_routing(n, updates, queries);
    assert_eq!(result, vec![9, 14, -1]);
}

#[test]
fn removal_updates() {
    let n = 4;
    let updates = vec![
        (0, 1, 5),
        (1, 2, 10),
        (2, 3, 3),
        (1, 2, -1)
    ];
    let queries = vec![
        // After removal, no path exists from 0 to 3.
        (0, 3, 3),
        // Query direct edge for verification.
        (0, 1, 1)
    ];
    let result = network_routing(n, updates, queries);
    assert_eq!(result, vec![-1, 5]);
}

#[test]
fn weight_update() {
    let n = 3;
    let updates = vec![
        (0, 1, 4),
        (0, 1, 2),
        (1, 2, 3),
    ];
    let queries = vec![
        (0, 2, 2)
    ];
    let result = network_routing(n, updates, queries);
    assert_eq!(result, vec![5]);
}

#[test]
fn max_hops_constraint() {
    let n = 6;
    let updates = vec![
        (0, 1, 2),
        (1, 2, 2),
        (2, 3, 2),
        (3, 4, 2),
        (4, 5, 2),
        (0, 5, 15),
    ];
    let queries = vec![
        // Chain path: 0->1->2->3->4->5 (5 hops, weight 10) is optimal.
        (0, 5, 5),
        // With max_hops 3, only the direct edge qualifies.
        (0, 5, 3),
    ];
    let result = network_routing(n, updates, queries);
    assert_eq!(result, vec![10, 15]);
}

#[test]
fn disconnected_nodes() {
    let n = 3;
    let updates = vec![
        (0, 1, 3),
    ];
    let queries = vec![
        (1, 2, 2),
        (0, 2, 3),
    ];
    let result = network_routing(n, updates, queries);
    assert_eq!(result, vec![-1, -1]);
}

#[test]
fn update_after_removal() {
    let n = 4;
    let updates = vec![
        (0, 1, 7),
        (1, 2, 8),
        (2, 3, 9),
        (1, 2, -1),
        (1, 2, 5)
    ];
    let queries = vec![
        (0, 3, 3)
    ];
    let result = network_routing(n, updates, queries);
    // The re-added edge now gives the optimal path 0 -> 1 -> 2 -> 3 with weight 7+5+9 = 21.
    assert_eq!(result, vec![21]);
}