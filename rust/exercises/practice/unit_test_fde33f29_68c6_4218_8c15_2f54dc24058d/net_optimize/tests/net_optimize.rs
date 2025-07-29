use net_optimize::optimize_network;

#[test]
fn test_two_nodes_feasible() {
    let n = 2;
    let capacity = vec![20, 20];
    let traffic = vec![
        vec![0, 10],
        vec![10, 0],
    ];
    let cost = vec![
        vec![0, 5],
        vec![5, 0],
    ];
    let latency = vec![
        vec![0, 3],
        vec![3, 0],
    ];
    // Expected:
    // Direct connections: edges 0->1 and 1->0.
    // Total cost = 5 + 5 = 10.
    // Total latency = (10*3) + (10*3) = 60.
    // Sum = 10 + 60 = 70.
    let result = optimize_network(n, capacity, traffic, cost, latency);
    assert_eq!(result, 70);
}

#[test]
fn test_three_nodes_feasible() {
    let n = 3;
    // Capacities high enough so that direct connections are feasible.
    let capacity = vec![100, 100, 100];
    let traffic = vec![
        vec![0, 5, 5],
        vec![5, 0, 10],
        vec![5, 10, 0],
    ];
    let cost = vec![
        vec![0, 4, 10],
        vec![8, 0, 3],
        vec![9, 2, 0],
    ];
    let latency = vec![
        vec![0, 2, 8],
        vec![6, 0, 1],
        vec![7, 1, 0],
    ];
    // All direct connections included:
    // Total cost = 4 + 10 + 8 + 3 + 9 + 2 = 36.
    // Latency:
    //  0->1: 5*2 = 10, 0->2: 5*8 = 40,
    //  1->0: 5*6 = 30, 1->2: 10*1 = 10,
    //  2->0: 5*7 = 35, 2->1: 10*1 = 10.
    // Total latency = 10 + 40 + 30 + 10 + 35 + 10 = 135.
    // Sum total = 36 + 135 = 171.
    let result = optimize_network(n, capacity, traffic, cost, latency);
    assert_eq!(result, 171);
}

#[test]
fn test_three_nodes_infeasible() {
    let n = 3;
    let capacity = vec![10, 10, 10];
    let traffic = vec![
        vec![0, 6, 6],
        vec![6, 0, 6],
        vec![6, 6, 0],
    ];
    let cost = vec![
        vec![0, 5, 5],
        vec![5, 0, 5],
        vec![5, 5, 0],
    ];
    let latency = vec![
        vec![0, 3, 3],
        vec![3, 0, 3],
        vec![3, 3, 0],
    ];
    // In this case, even using all direct connections,
    // the total load on each node exceeds its capacity.
    // Thus, the expected outcome is -1.
    let result = optimize_network(n, capacity, traffic, cost, latency);
    assert_eq!(result, -1);
}

#[test]
fn test_four_nodes_complex() {
    let n = 4;
    let capacity = vec![50, 50, 50, 50];
    let traffic = vec![
        vec![0, 3, 4, 5],
        vec![3, 0, 6, 2],
        vec![4, 6, 0, 1],
        vec![5, 2, 1, 0],
    ];
    let cost = vec![
        vec![0, 3, 8, 5],
        vec![7, 0, 4, 6],
        vec![9, 2, 0, 3],
        vec![4, 8, 7, 0],
    ];
    let latency = vec![
        vec![0, 2, 9, 4],
        vec![5, 0, 3, 8],
        vec![6, 1, 0, 2],
        vec![3, 7, 4, 0],
    ];
    // Taking all direct connections:
    // Total cost = 3+8+5+7+4+6+9+2+3+4+8+7 = 66.
    // Total latency:
    // 0->1: 3*2 = 6,   0->2: 4*9 = 36,  0->3: 5*4 = 20,
    // 1->0: 3*5 = 15,  1->2: 6*3 = 18,  1->3: 2*8 = 16,
    // 2->0: 4*6 = 24,  2->1: 6*1 = 6,   2->3: 1*2 = 2,
    // 3->0: 5*3 = 15,  3->1: 2*7 = 14,  3->2: 1*4 = 4.
    // Total latency = 6+36+20+15+18+16+24+6+2+15+14+4 = 176.
    // Sum total = 66 + 176 = 242.
    let result = optimize_network(n, capacity, traffic, cost, latency);
    assert_eq!(result, 242);
}