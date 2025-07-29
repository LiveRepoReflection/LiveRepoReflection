use resource_allocator::{Allocation, Machine, Task};
use std::collections::HashMap;

#[test]
fn test_basic_allocation() {
    let machines = vec![
        Machine { id: 1, cpu: 4, memory: 8, network: 10 },
        Machine { id: 2, cpu: 2, memory: 4, network: 5 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 1, memory: 2, network: 3 },
        Task { id: 2, cpu: 2, memory: 4, network: 4 },
    ];
    let dependencies = HashMap::new();

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    assert_eq!(result.len(), 2);
}

#[test]
fn test_insufficient_resources() {
    let machines = vec![
        Machine { id: 1, cpu: 1, memory: 1, network: 1 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 2, memory: 2, network: 2 },
    ];
    let dependencies = HashMap::new();

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    assert!(result.is_empty());
}

#[test]
fn test_with_dependencies() {
    let machines = vec![
        Machine { id: 1, cpu: 4, memory: 8, network: 10 },
        Machine { id: 2, cpu: 4, memory: 8, network: 10 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 2, memory: 4, network: 5 },
        Task { id: 2, cpu: 2, memory: 4, network: 5 },
        Task { id: 3, cpu: 2, memory: 4, network: 5 },
    ];
    let mut dependencies = HashMap::new();
    dependencies.insert(1, vec![2, 3]); // Task 1 must be scheduled before tasks 2 and 3

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    
    // Verify that if task 2 or 3 is allocated, task 1 must also be allocated
    if result.iter().any(|a| a.task_id == 2 || a.task_id == 3) {
        assert!(result.iter().any(|a| a.task_id == 1));
    }
}

#[test]
fn test_large_allocation() {
    let mut machines = Vec::new();
    let mut tasks = Vec::new();
    
    // Create 10 machines with varying capacities
    for i in 1..=10 {
        machines.push(Machine {
            id: i,
            cpu: i * 2,
            memory: i * 4,
            network: i * 3,
        });
    }

    // Create 20 tasks with varying requirements
    for i in 1..=20 {
        tasks.push(Task {
            id: i,
            cpu: 1,
            memory: 2,
            network: 1,
        });
    }

    let mut dependencies = HashMap::new();
    dependencies.insert(1, vec![2, 3]);
    dependencies.insert(4, vec![5, 6]);

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    assert!(result.len() > 0);
}

#[test]
fn test_resource_constraints() {
    let machines = vec![
        Machine { id: 1, cpu: 4, memory: 8, network: 10 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 2, memory: 4, network: 5 },
        Task { id: 2, cpu: 3, memory: 5, network: 6 },
    ];
    let dependencies = HashMap::new();

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);

    // Verify that allocated resources don't exceed machine capacity
    let mut used_cpu = 0;
    let mut used_memory = 0;
    let mut used_network = 0;

    for allocation in &result {
        let task = tasks.iter().find(|t| t.id == allocation.task_id).unwrap();
        used_cpu += task.cpu;
        used_memory += task.memory;
        used_network += task.network;
    }

    assert!(used_cpu <= machines[0].cpu);
    assert!(used_memory <= machines[0].memory);
    assert!(used_network <= machines[0].network);
}

#[test]
fn test_cyclic_dependencies() {
    let machines = vec![
        Machine { id: 1, cpu: 4, memory: 8, network: 10 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 1, memory: 2, network: 3 },
        Task { id: 2, cpu: 1, memory: 2, network: 3 },
    ];
    let mut dependencies = HashMap::new();
    dependencies.insert(1, vec![2]);
    dependencies.insert(2, vec![1]); // Circular dependency

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    assert!(result.is_empty()); // Should fail due to circular dependency
}

#[test]
fn test_single_allocation_constraint() {
    let machines = vec![
        Machine { id: 1, cpu: 4, memory: 8, network: 10 },
        Machine { id: 2, cpu: 4, memory: 8, network: 10 },
    ];
    let tasks = vec![
        Task { id: 1, cpu: 1, memory: 2, network: 3 },
    ];
    let dependencies = HashMap::new();

    let result = resource_allocator::allocate_resources(&machines, &tasks, &dependencies);
    
    // Count occurrences of task 1
    let task1_count = result.iter()
        .filter(|a| a.task_id == 1)
        .count();
    
    assert_eq!(task1_count, 1); // Task should be allocated exactly once
}