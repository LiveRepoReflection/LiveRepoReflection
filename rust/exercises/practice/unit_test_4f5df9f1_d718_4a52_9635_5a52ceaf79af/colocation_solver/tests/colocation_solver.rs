use colocation_solver::{solve_colocation, ServerCapacity};
use std::collections::HashMap;

#[test]
fn test_simple_placement() {
    // Simple case with no existing placements or restrictions
    let server_capacity = ServerCapacity {
        cpu: 8,
        memory: 16 * 1024 * 1024 * 1024, // 16GB
        network: 1000,
    };

    let vm_requests = vec![
        (1, 101, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 101
        (1, 102, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 102
        (2, 201, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 2, VM 201
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect all VMs to fit on a single server
    assert!(result.is_some());
    let placement = result.unwrap();
    assert_eq!(placement.len(), 1); // Only one server should be used
}

#[test]
fn test_with_restrictions() {
    // Case with colocation restrictions
    let server_capacity = ServerCapacity {
        cpu: 8,
        memory: 16 * 1024 * 1024 * 1024, // 16GB
        network: 1000,
    };

    let vm_requests = vec![
        (1, 101, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 101
        (1, 102, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 102
        (2, 201, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 2, VM 201
        (3, 301, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 3, VM 301
    ];

    // Customer 1 and 2 cannot be collocated
    let colocation_restrictions: Vec<(u32, u32)> = vec![(1, 2)];
    let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution with 2 servers
    assert!(result.is_some());
    let placement = result.unwrap();
    assert_eq!(placement.len(), 2); // Two servers should be used

    // Check that Customer 1 and 2 are not on the same server
    for (_server_id, vms) in placement.iter() {
        let has_customer_1 = vms.iter().any(|(customer_id, _)| *customer_id == 1);
        let has_customer_2 = vms.iter().any(|(customer_id, _)| *customer_id == 2);
        assert!(!(has_customer_1 && has_customer_2));
    }
}

#[test]
fn test_with_existing_placements() {
    // Case with existing placements
    let server_capacity = ServerCapacity {
        cpu: 8,
        memory: 16 * 1024 * 1024 * 1024, // 16GB
        network: 1000,
    };

    let vm_requests = vec![
        (1, 101, 2, 4 * 1024 * 1024 * 1024, 200), // Customer 1, VM 101
        (2, 201, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 2, VM 201
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    
    // VM 101 already placed on server 1
    let mut existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();
    existing_placements.insert(1, vec![(1, 101)]);

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution
    assert!(result.is_some());
    let placement = result.unwrap();
    
    // Check that existing placement is respected
    assert!(placement.contains_key(&1));
    assert!(placement[&1].contains(&(1, 101)));
}

#[test]
fn test_resource_limits() {
    // Test resource limits
    let server_capacity = ServerCapacity {
        cpu: 4,
        memory: 8 * 1024 * 1024 * 1024, // 8GB
        network: 500,
    };

    let vm_requests = vec![
        (1, 101, 3, 6 * 1024 * 1024 * 1024, 300), // Customer 1, VM 101
        (2, 201, 3, 6 * 1024 * 1024 * 1024, 300), // Customer 2, VM 201
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution with 2 servers since each VM uses most of a server's resources
    assert!(result.is_some());
    let placement = result.unwrap();
    assert_eq!(placement.len(), 2); // Two servers should be used
}

#[test]
fn test_complex_scenario() {
    // A more complex scenario with multiple constraints
    let server_capacity = ServerCapacity {
        cpu: 16,
        memory: 32 * 1024 * 1024 * 1024, // 32GB
        network: 2000,
    };

    let vm_requests = vec![
        (1, 101, 4, 8 * 1024 * 1024 * 1024, 500),  // Customer 1, VM 101
        (1, 102, 4, 8 * 1024 * 1024 * 1024, 500),  // Customer 1, VM 102
        (2, 201, 6, 12 * 1024 * 1024 * 1024, 800), // Customer 2, VM 201
        (2, 202, 6, 12 * 1024 * 1024 * 1024, 800), // Customer 2, VM 202
        (3, 301, 8, 16 * 1024 * 1024 * 1024, 1000), // Customer 3, VM 301
        (4, 401, 8, 16 * 1024 * 1024 * 1024, 1000), // Customer 4, VM 401
    ];

    // Customer 1 cannot be with 2, and 3 cannot be with 4
    let colocation_restrictions: Vec<(u32, u32)> = vec![(1, 2), (3, 4)];
    
    // VM 101 already placed on server 1
    // VM 301 already placed on server 2
    let mut existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();
    existing_placements.insert(1, vec![(1, 101)]);
    existing_placements.insert(2, vec![(3, 301)]);

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution
    assert!(result.is_some());
    let placement = result.unwrap();
    
    // Check that existing placements are respected
    assert!(placement.contains_key(&1));
    assert!(placement[&1].contains(&(1, 101)));
    assert!(placement.contains_key(&2));
    assert!(placement[&2].contains(&(3, 301)));
    
    // Check that colocation restrictions are respected
    for (_server_id, vms) in placement.iter() {
        let has_customer_1 = vms.iter().any(|(customer_id, _)| *customer_id == 1);
        let has_customer_2 = vms.iter().any(|(customer_id, _)| *customer_id == 2);
        let has_customer_3 = vms.iter().any(|(customer_id, _)| *customer_id == 3);
        let has_customer_4 = vms.iter().any(|(customer_id, _)| *customer_id == 4);
        
        assert!(!(has_customer_1 && has_customer_2));
        assert!(!(has_customer_3 && has_customer_4));
    }
    
    // Check that all VMs are placed
    let mut placed_vms = vec![];
    for (_server_id, vms) in placement.iter() {
        for &vm in vms {
            placed_vms.push(vm);
        }
    }
    assert_eq!(placed_vms.len(), vm_requests.len());
}

#[test]
fn test_impossible_placement() {
    // A scenario where placement is impossible
    let server_capacity = ServerCapacity {
        cpu: 4,
        memory: 8 * 1024 * 1024 * 1024, // 8GB
        network: 500,
    };

    let vm_requests = vec![
        (1, 101, 5, 4 * 1024 * 1024 * 1024, 300), // CPU requirement exceeds server capacity
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect no valid solution
    assert!(result.is_none());
}

#[test]
fn test_server_utilization_optimization() {
    // Test that the solution optimizes server utilization
    let server_capacity = ServerCapacity {
        cpu: 8,
        memory: 16 * 1024 * 1024 * 1024, // 16GB
        network: 1000,
    };

    // These VMs could fit on 2 servers if optimally placed
    let vm_requests = vec![
        (1, 101, 3, 6 * 1024 * 1024 * 1024, 300), // Customer 1, VM 101
        (2, 201, 3, 6 * 1024 * 1024 * 1024, 300), // Customer 2, VM 201
        (3, 301, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 3, VM 301
        (4, 401, 4, 8 * 1024 * 1024 * 1024, 400), // Customer 4, VM 401
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    let existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution with 2 servers (optimal packing)
    assert!(result.is_some());
    let placement = result.unwrap();
    assert_eq!(placement.len(), 2); // Two servers should be used
}

#[test]
fn test_contiguous_server_ids() {
    // Test that server IDs are contiguous
    let server_capacity = ServerCapacity {
        cpu: 4,
        memory: 8 * 1024 * 1024 * 1024, // 8GB
        network: 500,
    };

    let vm_requests = vec![
        (1, 101, 2, 4 * 1024 * 1024 * 1024, 250), // Customer 1, VM 101
        (2, 201, 2, 4 * 1024 * 1024 * 1024, 250), // Customer 2, VM 201
        (3, 301, 2, 4 * 1024 * 1024 * 1024, 250), // Customer 3, VM 301
    ];

    let colocation_restrictions: Vec<(u32, u32)> = vec![];
    
    // Place VM 101 on server 3 (this should not create gaps in the final solution)
    let mut existing_placements: HashMap<u32, Vec<(u32, u32)>> = HashMap::new();
    existing_placements.insert(3, vec![(1, 101)]);

    let result = solve_colocation(
        &server_capacity,
        &vm_requests,
        &colocation_restrictions,
        &existing_placements,
    );

    // We expect a valid solution
    assert!(result.is_some());
    let placement = result.unwrap();
    
    // Check that server IDs start from 1 and are contiguous
    let max_server_id = *placement.keys().max().unwrap();
    for server_id in 1..=max_server_id {
        assert!(placement.contains_key(&server_id));
    }
}