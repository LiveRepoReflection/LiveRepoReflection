use network_scheduler::max_weighted_throughput;

#[test]
fn test_empty_data_flows() {
    let n = 3;
    let processing_capacities = vec![100, 200, 150];
    let data_flows: Vec<(usize, usize, usize, usize)> = vec![];
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 0);
}

#[test]
fn test_basic_example() {
    let n = 2;
    let processing_capacities = vec![100, 100];
    let data_flows = vec![
        (0, 1, 50, 2), // weighted throughput = 100
        (1, 0, 60, 3), // weighted throughput = 180
        (0, 1, 70, 1), // weighted throughput = 70; cannot combine with first since 50+70 > 100 on server 0
    ];
    // Best selection: choose flows (0,1,50,2) and (1,0,60,3) for total = 280.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 280);
}

#[test]
fn test_all_flows_fit() {
    let n = 2;
    let processing_capacities = vec![200, 200];
    let data_flows = vec![
        (0, 1, 100, 10), // weighted = 1000, uses server 0 capacity = 100
        (1, 0, 100, 20), // weighted = 2000, uses server 1 capacity = 100
    ];
    // Both flows can be scheduled, total = 3000.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 3000);
}

#[test]
fn test_conflict_flows() {
    let n = 3;
    let processing_capacities = vec![100, 100, 100];
    let data_flows = vec![
        (0, 1, 70, 5),  // weighted = 350, uses 70 from server 0
        (0, 2, 50, 4),  // weighted = 200, uses 50 from server 0 (cannot combine with above since 70+50 > 100)
        (1, 2, 60, 10), // weighted = 600, uses 60 from server 1
        (2, 1, 80, 1),  // weighted = 80, uses 80 from server 2
    ];
    // Optimal selection is to choose flows (0,1,70,5), (1,2,60,10) and (2,1,80,1)
    // Total weighted throughput = 350 + 600 + 80 = 1030.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 1030);
}

#[test]
fn test_capacity_exceeded() {
    let n = 2;
    let processing_capacities = vec![50, 100];
    let data_flows = vec![
        (0, 1, 60, 10), // cannot be scheduled because volume 60 exceeds capacity of server 0 (50)
        (1, 0, 30, 5),  // can be scheduled, uses 30 from server 1, weighted = 150
    ];
    // Only the second flow can be scheduled.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 150);
}

#[test]
fn test_non_greedy_selection() {
    let n = 1;
    let processing_capacities = vec![100];
    let data_flows = vec![
        (0, 1, 60, 5), // weighted = 300
        (0, 1, 50, 4), // weighted = 200, cannot combine with first due to capacity overrun (60+50 > 100)
        (0, 1, 40, 3), // weighted = 120
    ];
    // Optimal selection is to choose flows (0,1,60,5) and (0,1,40,3) using full capacity (60+40=100)
    // Total weighted throughput = 300 + 120 = 420.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 420);
}

#[test]
fn test_multiple_servers_independent() {
    let n = 3;
    let processing_capacities = vec![100, 200, 150];
    let data_flows = vec![
        // Flows from server 0
        (0, 1, 60, 2), // weighted = 120
        (0, 2, 40, 3), // weighted = 120, total server0 usage = 100, sum = 240
        // Flows from server 1
        (1, 0, 150, 5), // weighted = 750, uses 150 from server 1 which is <= 200
        (1, 2, 60, 2),  // weighted = 120, but cannot add with previous as 150+60 = 210 > 200, so best is to only choose higher one
        // Flow from server 2
        (2, 1, 150, 4), // weighted = 600, exactly fits server2's capacity
    ];
    // Optimal selection:
    // From server 0: (0,1,60,2) and (0,2,40,3) -> 240
    // From server 1: (1,0,150,5) -> 750
    // From server 2: (2,1,150,4) -> 600
    // Total = 240 + 750 + 600 = 1590.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 1590);
}

#[test]
fn test_duplicate_flows() {
    let n = 2;
    let processing_capacities = vec![100, 100];
    let data_flows = vec![
        (0, 1, 50, 2),
        (0, 1, 50, 2),
    ];
    // Both flows can be scheduled since server 0 capacity is exactly 100.
    // Total weighted throughput = (50*2) + (50*2) = 100 + 100 = 200.
    let result = max_weighted_throughput(n, processing_capacities, data_flows);
    assert_eq!(result, 200);
}