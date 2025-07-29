use microservice_partition::partition;

#[test]
fn test_single_server_single_microservice() {
    let servers = vec![(10, 10, 10)];
    let edges = Vec::new();
    let microservices = vec![(5, 5, 5)];
    let dependencies = vec![];
    let k = 1;
    let result = partition(servers, edges, microservices, dependencies, k);
    assert!(result.is_some());
    let clusters = result.unwrap();
    assert_eq!(clusters.len(), k);
    let all_ms: Vec<usize> = clusters.into_iter().flatten().collect();
    assert_eq!(all_ms.len(), 1);
    assert_eq!(all_ms[0], 0);
}

#[test]
fn test_example_partition() {
    let servers = vec![(10, 10, 10), (12, 12, 12), (15, 15, 15)];
    let edges = vec![(0, 1, 5), (1, 2, 3)];
    let microservices = vec![(3, 3, 3), (2, 2, 2), (4, 4, 4)];
    let dependencies = vec![(0, 1), (2, 0)];
    let k = 2;
    let result = partition(servers, edges, microservices, dependencies, k);
    assert!(result.is_some());
    let clusters = result.unwrap();
    assert_eq!(clusters.len(), k);
    // Ensure that all microservices are assigned exactly once.
    let mut ms_ids: Vec<usize> = clusters.iter().flatten().cloned().collect();
    ms_ids.sort_unstable();
    assert_eq!(ms_ids, vec![0, 1, 2]);
}

#[test]
fn test_impossible_partition_due_to_capacity() {
    // In this case, a microservice requires more resources than available.
    let servers = vec![(2, 2, 2), (2, 2, 2)];
    let edges = vec![(0, 1, 1)];
    let microservices = vec![(3, 0, 0)];
    let dependencies = vec![];
    let k = 1;
    let result = partition(servers, edges, microservices, dependencies, k);
    assert!(result.is_none());
}

#[test]
fn test_dependency_constraint() {
    // Here we create a chain of dependencies in a fully connected graph.
    let servers = vec![(20, 20, 20), (20, 20, 20), (20, 20, 20), (20, 20, 20)];
    let edges = vec![
        (0, 1, 2), (1, 0, 2),
        (1, 2, 2), (2, 1, 2),
        (2, 3, 2), (3, 2, 2),
        (0, 3, 5), (3, 0, 5),
        (0, 2, 4), (2, 0, 4),
        (1, 3, 3), (3, 1, 3)
    ];
    let microservices = vec![
        (5, 5, 5),  // Microservice 0
        (5, 5, 5),  // Microservice 1
        (5, 5, 5),  // Microservice 2
        (5, 5, 5)   // Microservice 3
    ];
    let dependencies = vec![(0, 1), (1, 2), (2, 3)];
    let k = 2;
    let result = partition(servers, edges, microservices, dependencies, k);
    assert!(result.is_some());
    let clusters = result.unwrap();
    assert_eq!(clusters.len(), k);
    // Ensure that all microservices are assigned.
    let mut ms_ids: Vec<usize> = clusters.iter().flatten().cloned().collect();
    ms_ids.sort_unstable();
    assert_eq!(ms_ids, vec![0, 1, 2, 3]);
}

#[test]
fn test_multiple_clusters_increased_complexity() {
    // A more complex scenario with 5 servers, 6 microservices, and multiple dependencies.
    let servers = vec![
        (15, 15, 15), // Server 0
        (10, 10, 10), // Server 1
        (20, 20, 20), // Server 2
        (15, 15, 15), // Server 3
        (25, 25, 25)  // Server 4
    ];
    let edges = vec![
        (0, 1, 3), (1, 0, 3),
        (1, 2, 2), (2, 1, 2),
        (2, 3, 4), (3, 2, 4),
        (3, 4, 1), (4, 3, 1),
        (0, 4, 7), (4, 0, 7)
    ];
    let microservices = vec![
        (5, 5, 5),  // Microservice 0
        (3, 3, 3),  // Microservice 1
        (7, 7, 7),  // Microservice 2
        (4, 4, 4),  // Microservice 3
        (6, 6, 6),  // Microservice 4
        (2, 2, 2)   // Microservice 5
    ];
    let dependencies = vec![
        (0, 1), (1, 2), (2, 3), (4, 2), (5, 4)
    ];
    let k = 3;
    let result = partition(servers, edges, microservices, dependencies, k);
    assert!(result.is_some());
    let clusters = result.unwrap();
    assert_eq!(clusters.len(), k);
    // Ensure that all microservices are assigned exactly once.
    let mut assigned: Vec<usize> = clusters.iter().flatten().cloned().collect();
    assigned.sort_unstable();
    assert_eq!(assigned, vec![0, 1, 2, 3, 4, 5]);
}