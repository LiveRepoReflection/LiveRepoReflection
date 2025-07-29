use network_allocator::{Operation, process_operations};

#[test]
fn test_no_connection_path() {
    let capacities = vec![10, 5, 8];
    let operations = vec![
        Operation::Event(0, 1, true),  // Connect node 0 and node 1
        Operation::Request(0, 2, 7),    // Attempt transfer from node 0 to node 2 (no path)
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![0];
    assert_eq!(results, expected);
}

#[test]
fn test_basic_transfer_partial() {
    let capacities = vec![10, 5, 8];
    let operations = vec![
        Operation::Event(0, 1, true),  // Connect node 0 and node 1
        Operation::Request(0, 2, 7),    // No valid path, should return 0
        Operation::Event(1, 2, true),  // Connect node 1 and node 2, forming a path 0->1->2
        Operation::Request(0, 2, 7),    // Transfer via node 1, limited by its capacity (5)
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![0, 5];
    assert_eq!(results, expected);
}

#[test]
fn test_disconnect_effect() {
    let capacities = vec![15, 10, 20, 25];
    let operations = vec![
        Operation::Event(0, 1, true),   // Connect node 0 and node 1
        Operation::Event(1, 2, true),   // Connect node 1 and node 2
        Operation::Event(2, 3, true),   // Connect node 2 and node 3, forming path 0->1->2->3
        // The bottleneck on the path is node 1 with capacity 10 (node 2 has capacity 20)
        Operation::Request(0, 3, 12),    // Request 12; should transfer only 10
        Operation::Event(1, 2, false),  // Disconnect node 1 and node 2, breaking the path
        Operation::Request(0, 3, 12),    // Now, transfer should fail resulting in 0
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![10, 0];
    assert_eq!(results, expected);
}

#[test]
fn test_multiple_paths() {
    let capacities = vec![100, 50, 60, 40, 70];
    let operations = vec![
        Operation::Event(0, 1, true),  // First potential path: 0 -> 1
        Operation::Event(1, 4, true),  // Complete first path: 0 -> 1 -> 4 with bottleneck 50
        Operation::Event(0, 2, true),  // Second potential path: 0 -> 2
        Operation::Event(2, 3, true),  // Continue second path: 2 -> 3
        Operation::Event(3, 4, true),  // Complete second path: 0 -> 2 -> 3 -> 4 with bottleneck 40 (min(60,40))
        Operation::Request(0, 4, 80),   // Request 80; system should choose the optimal path yielding 50 transferred
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![50];
    assert_eq!(results, expected);
}

#[test]
fn test_repeated_requests_no_capacity_consumption() {
    let capacities = vec![30, 20, 25];
    let operations = vec![
        Operation::Event(0, 1, true),  // Connect node 0 and node 1
        Operation::Event(1, 2, true),  // Connect node 1 and node 2 forming path 0->1->2
        Operation::Request(0, 2, 15),   // First request: 15, which is within node 1's capacity (20)
        Operation::Request(0, 2, 25),   // Second request: 25, but limited by node 1 capacity to deliver 20
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![15, 20];
    assert_eq!(results, expected);
}

#[test]
fn test_invalid_node_handling() {
    let capacities = vec![10, 10];
    let operations = vec![
        // Invalid event: attempting to connect a non-existent node index 2 should be handled gracefully.
        Operation::Event(0, 2, true),
        Operation::Request(0, 1, 5),  // With no valid connection, request should return 0.
    ];
    let results = process_operations(capacities, operations);
    let expected = vec![0];
    assert_eq!(results, expected);
}