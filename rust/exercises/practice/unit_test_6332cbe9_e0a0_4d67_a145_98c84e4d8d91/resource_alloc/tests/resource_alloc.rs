use std::collections::HashMap;
use resource_alloc::allocate;

#[test]
fn test_empty_request() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 4);
            map.insert("memory".to_string(), 16);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 8);
            map.insert("memory".to_string(), 32);
            map
        },
    ];
    let request: HashMap<String, u64> = HashMap::new();

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_ok());
    let allocation = result.unwrap();
    // An empty request should result in an empty allocation.
    assert!(allocation.is_empty());
}

#[test]
fn test_insufficient_resources() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 2);
            map.insert("memory".to_string(), 4);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 1);
            map.insert("memory".to_string(), 2);
            map
        },
    ];

    let mut request = HashMap::new();
    request.insert("cpu".to_string(), 5);
    request.insert("memory".to_string(), 8);

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_err());
    assert_eq!(result.err().unwrap(), "Insufficient resources");
}

#[test]
fn test_single_rm_exact_match() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 4);
            map.insert("memory".to_string(), 16);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 8);
            map.insert("memory".to_string(), 32);
            map
        },
    ];

    let mut request = HashMap::new();
    request.insert("cpu".to_string(), 8);
    request.insert("memory".to_string(), 32);

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_ok());
    let allocation = result.unwrap();
    // Allocation should only use a single resource manager.
    assert_eq!(allocation.len(), 1);
    let (_rm_index, alloc_map) = allocation.into_iter().next().unwrap();
    assert!(*alloc_map.get("cpu").unwrap() >= 8);
    assert!(*alloc_map.get("memory").unwrap() >= 32);
}

#[test]
fn test_multiple_rms_allocation() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 2);
            map.insert("memory".to_string(), 4);
            map.insert("disk".to_string(), 100);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 4);
            map.insert("memory".to_string(), 8);
            map.insert("disk".to_string(), 50);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 4);
            map.insert("memory".to_string(), 8);
            map.insert("disk".to_string(), 200);
            map
        },
    ];

    let mut request = HashMap::new();
    request.insert("cpu".to_string(), 6);
    request.insert("memory".to_string(), 10);
    request.insert("disk".to_string(), 120);

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_ok());
    let allocation = result.unwrap();

    // Verify the aggregate allocation meets the request.
    let mut total_alloc: HashMap<String, u64> = HashMap::new();
    for (_rm_index, res_map) in allocation.iter() {
        for (res, amount) in res_map.iter() {
            *total_alloc.entry(res.clone()).or_insert(0) += *amount;
        }
    }

    assert!(*total_alloc.get("cpu").unwrap_or(&0) >= 6);
    assert!(*total_alloc.get("memory").unwrap_or(&0) >= 10);
    assert!(*total_alloc.get("disk").unwrap_or(&0) >= 120);
}

#[test]
fn test_zero_capacity_rm() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            // This RM has zero capacity for "cpu" and "memory".
            map.insert("cpu".to_string(), 0);
            map.insert("memory".to_string(), 0);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 4);
            map.insert("memory".to_string(), 16);
            map
        },
    ];

    let mut request = HashMap::new();
    request.insert("cpu".to_string(), 2);
    request.insert("memory".to_string(), 8);

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_ok());
    let allocation = result.unwrap();
    // Ensure the allocation skips any RM with zero capacity.
    assert_eq!(allocation.len(), 1);
    assert!(allocation.contains_key(&1));
    let alloc_map = allocation.get(&1).unwrap();
    assert!(*alloc_map.get("cpu").unwrap() >= 2);
    assert!(*alloc_map.get("memory").unwrap() >= 8);
}

#[test]
fn test_exact_split_allocation() {
    let rm_capacities = vec![
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 3);
            map.insert("memory".to_string(), 8);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 3);
            map.insert("memory".to_string(), 8);
            map
        },
        {
            let mut map = HashMap::new();
            map.insert("cpu".to_string(), 3);
            map.insert("memory".to_string(), 8);
            map
        },
    ];

    let mut request = HashMap::new();
    request.insert("cpu".to_string(), 5);
    request.insert("memory".to_string(), 12);

    let result = allocate(&rm_capacities, &request);
    assert!(result.is_ok());
    let allocation = result.unwrap();

    // Check that the number of RMs used is minimized.
    assert!(allocation.len() <= 2);

    // Validate that the total allocation meets the request.
    let mut total_alloc: HashMap<String, u64> = HashMap::new();
    for (_rm_index, alloc_map) in allocation.iter() {
        for (resource, amount) in alloc_map.iter() {
            *total_alloc.entry(resource.clone()).or_insert(0) += *amount;
        }
    }
    assert!(*total_alloc.get("cpu").unwrap() >= 5);
    assert!(*total_alloc.get("memory").unwrap() >= 12);
}