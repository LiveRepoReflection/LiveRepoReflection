use train_network::min_cost_train_network;

#[test]
fn test_single_city() {
    let n = 1;
    let routes: Vec<(usize, usize, u64, u64)> = vec![];
    // When there is a single city, there are no pairs to satisfy,
    // so the cost should be 0.
    let k = 5;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, Some(0));
}

#[test]
fn test_simple_network() {
    let n = 4;
    let routes = vec![
        (0, 1, 10, 5),
        (1, 2, 20, 7),
        (2, 3, 30, 9),
    ];
    // Spanning tree: (0,1), (1,2), (2,3) with total cost 10+20+30 = 60.
    // Minimum capacity on this network is min(5,7,9)=5, which satisfies K=4.
    let k = 4;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, Some(60));
}

#[test]
fn test_redundant_routes() {
    let n = 4;
    let routes = vec![
        (0, 1, 10, 5),
        (0, 2, 15, 3),
        (1, 2, 20, 7),
        (1, 3, 25, 2),
        (2, 3, 30, 9),
    ];
    // Although there are extra routes, the optimal network can be obtained by choosing
    // the spanning tree: (0,1) [10,5], (1,2) [20,7], (2,3) [30,9] for a total cost of 60,
    // which satisfies the minimum capacity K=4.
    let k = 4;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, Some(60));
}

#[test]
fn test_disconnected_network() {
    let n = 3;
    let routes = vec![
        (0, 1, 10, 5),
        (1, 2, 20, 7),
    ];
    // The spanning tree here would yield a path 0-1-2.
    // However, the minimum capacity on this path is min(5,7)=5, which is below the requirement of K=6.
    // Thus, no valid network can be constructed.
    let k = 6;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, None);
}

#[test]
fn test_multiple_routes_same_cities() {
    let n = 3;
    let routes = vec![
        (0, 1, 10, 5),
        (0, 1, 15, 8),
        (1, 2, 20, 5),
        (1, 2, 10, 6),
    ];
    // The optimal solution would choose the cheaper edge among duplicates:
    // For example: (0, 1) with cost 10 and capacity 5, (1, 2) with cost 10 and capacity 6.
    // Total cost = 10 + 10 = 20, meeting the minimum capacity K=5.
    let k = 5;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, Some(20));
}

#[test]
fn test_cycle_network() {
    let n = 5;
    let routes = vec![
        (0, 1, 10, 10),
        (1, 2, 10, 3),
        (2, 3, 10, 10),
        (3, 4, 10, 10),
        (4, 0, 50, 10),
        (1, 3, 30, 4),
    ];
    // A simple spanning tree (by choosing the optimal combination of routes) that satisfies the
    // minimum capacity requirement (K=4) might be:
    // (0, 1) [10,10], (1, 3) [30,4], (3, 2) [10,10] (from edge (2,3)), and (3, 4) [10,10].
    // Total cost = 10 + 30 + 10 + 10 = 60.
    let k = 4;
    let res = min_cost_train_network(n, &routes, k);
    assert_eq!(res, Some(60));
}