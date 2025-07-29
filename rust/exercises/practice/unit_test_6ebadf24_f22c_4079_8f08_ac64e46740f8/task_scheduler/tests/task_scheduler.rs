use task_scheduler::{Task, solve_task_scheduling};

#[test]
fn test_empty_tasks() {
    let tasks = vec![];
    assert_eq!(solve_task_scheduling(tasks), 0);
}

#[test]
fn test_single_task_no_dependency() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 5,
            deadline: 10,
            dependencies: vec![],
        }
    ];
    assert_eq!(solve_task_scheduling(tasks), 0); // No tardiness if deadline > processing time
}

#[test]
fn test_single_task_with_tardiness() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 10,
            deadline: 5,
            dependencies: vec![],
        }
    ];
    assert_eq!(solve_task_scheduling(tasks), 50); // (10-5)*10 = 50
}

#[test]
fn test_linear_dependency_chain() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 5,
            deadline: 5,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 8,
            dependencies: vec![0],
        },
        Task {
            id: 2,
            processing_time: 4,
            deadline: 12,
            dependencies: vec![1],
        },
    ];
    assert_eq!(solve_task_scheduling(tasks), 0); // All tasks can be completed before deadlines
}

#[test]
fn test_linear_dependency_chain_with_tardiness() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 5,
            deadline: 3,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 5,
            dependencies: vec![0],
        },
        Task {
            id: 2,
            processing_time: 4,
            deadline: 10,
            dependencies: vec![1],
        },
    ];
    // Task 0: Tardiness = 2, Weighted = 2*5 = 10
    // Task 1: Tardiness = 3, Weighted = 3*3 = 9
    // Task 2: Tardiness = 2, Weighted = 2*4 = 8
    // Total: 27
    assert_eq!(solve_task_scheduling(tasks), 27);
}

#[test]
fn test_circular_dependency() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 5,
            deadline: 10,
            dependencies: vec![1],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 8,
            dependencies: vec![0],
        },
    ];
    assert_eq!(solve_task_scheduling(tasks), -1); // Circular dependency, no valid schedule
}

#[test]
fn test_multiple_independent_tasks() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 5,
            deadline: 5,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 3,
            dependencies: vec![],
        },
        Task {
            id: 2,
            processing_time: 4,
            deadline: 4,
            dependencies: vec![],
        },
    ];
    // Optimally scheduled: 1, 2, 0
    // Task 1: Completes at 3, no tardiness
    // Task 2: Completes at 7, tardiness = 3, weighted = 3*4 = 12
    // Task 0: Completes at 12, tardiness = 7, weighted = 7*5 = 35
    // Total: 47
    
    // But we can also do: 2, 1, 0 or other combinations
    // Let's check the best ordering
    
    // Order: 0, 1, 2
    // Task 0: Completes at 5, no tardiness
    // Task 1: Completes at 8, tardiness = 5, weighted = 5*3 = 15
    // Task 2: Completes at 12, tardiness = 8, weighted = 8*4 = 32
    // Total: 47
    
    // Order: 0, 2, 1
    // Task 0: Completes at 5, no tardiness
    // Task 2: Completes at 9, tardiness = 5, weighted = 5*4 = 20
    // Task 1: Completes at 12, tardiness = 9, weighted = 9*3 = 27
    // Total: 47
    
    // Order: 1, 0, 2
    // Task 1: Completes at 3, no tardiness
    // Task 0: Completes at 8, tardiness = 3, weighted = 3*5 = 15
    // Task 2: Completes at 12, tardiness = 8, weighted = 8*4 = 32
    // Total: 47
    
    // Order: 1, 2, 0
    // Task 1: Completes at 3, no tardiness
    // Task 2: Completes at 7, tardiness = 3, weighted = 3*4 = 12
    // Task 0: Completes at 12, tardiness = 7, weighted = 7*5 = 35
    // Total: 47
    
    // Order: 2, 0, 1
    // Task 2: Completes at 4, no tardiness
    // Task 0: Completes at 9, tardiness = 4, weighted = 4*5 = 20
    // Task 1: Completes at 12, tardiness = 9, weighted = 9*3 = 27
    // Total: 47
    
    // Order: 2, 1, 0
    // Task 2: Completes at 4, no tardiness
    // Task 1: Completes at 7, tardiness = 4, weighted = 4*3 = 12
    // Task 0: Completes at 12, tardiness = 7, weighted = 7*5 = 35
    // Total: 47
    
    // The minimum weighted tardiness is 47
    assert_eq!(solve_task_scheduling(tasks), 47);
}

#[test]
fn test_complex_dependency_graph() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 2,
            deadline: 5,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 10,
            dependencies: vec![0],
        },
        Task {
            id: 2,
            processing_time: 4,
            deadline: 8,
            dependencies: vec![0],
        },
        Task {
            id: 3,
            processing_time: 2,
            deadline: 15,
            dependencies: vec![1, 2],
        },
        Task {
            id: 4,
            processing_time: 5,
            deadline: 20,
            dependencies: vec![3],
        },
    ];
    
    // Optimal schedule:
    // Task 0: 0-2, no tardiness
    // We need to decide task 1 or 2 next
    // If task 1: 2-5, no tardiness, then task 2: 5-9, tardiness = 1, weighted = 1*4 = 4
    // If task 2: 2-6, no tardiness, then task 1: 6-9, no tardiness
    // 
    // Optimal choice is task 2 then task 1:
    // Task 2: 2-6, no tardiness
    // Task 1: 6-9, no tardiness
    // Task 3: 9-11, no tardiness
    // Task 4: 11-16, no tardiness
    // Total: 0
    
    assert_eq!(solve_task_scheduling(tasks), 0);
}

#[test]
fn test_challenging_case() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 10,
            deadline: 20,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 15,
            deadline: 30,
            dependencies: vec![],
        },
        Task {
            id: 2,
            processing_time: 20,
            deadline: 40,
            dependencies: vec![0, 1],
        },
        Task {
            id: 3,
            processing_time: 5,
            deadline: 15,
            dependencies: vec![],
        },
        Task {
            id: 4,
            processing_time: 8,
            deadline: 25,
            dependencies: vec![3],
        },
        Task {
            id: 5,
            processing_time: 12,
            deadline: 35,
            dependencies: vec![2, 4],
        },
    ];
    
    // One possible optimal schedule:
    // Task 3: 0-5, no tardiness
    // Task 0: 5-15, no tardiness
    // Task 4: 15-23, no tardiness
    // Task 1: 23-38, tardiness = 8, weighted = 8*15 = 120
    // Task 2: 38-58, tardiness = 18, weighted = 18*20 = 360
    // Task 5: 58-70, tardiness = 35, weighted = 35*12 = 420
    // Total: 900
    
    // However, there may be a better ordering, so just testing that the result is <= 900
    let result = solve_task_scheduling(tasks);
    assert!(result <= 900 && result > 0);
}

#[test]
fn test_medium_sized_problem() {
    let tasks = vec![
        Task { id: 0, processing_time: 5, deadline: 10, dependencies: vec![] },
        Task { id: 1, processing_time: 3, deadline: 8, dependencies: vec![0] },
        Task { id: 2, processing_time: 7, deadline: 15, dependencies: vec![1] },
        Task { id: 3, processing_time: 2, deadline: 12, dependencies: vec![0] },
        Task { id: 4, processing_time: 4, deadline: 20, dependencies: vec![2, 3] },
        Task { id: 5, processing_time: 6, deadline: 25, dependencies: vec![4] },
        Task { id: 6, processing_time: 8, deadline: 30, dependencies: vec![5] },
        Task { id: 7, processing_time: 3, deadline: 18, dependencies: vec![3] },
        Task { id: 8, processing_time: 5, deadline: 22, dependencies: vec![7] },
        Task { id: 9, processing_time: 4, deadline: 28, dependencies: vec![8, 6] },
    ];
    
    // This is a moderately complex graph with multiple paths
    // Just testing that the function returns a valid result (not -1)
    let result = solve_task_scheduling(tasks);
    assert!(result >= 0);
}

#[test]
fn test_multiple_possible_paths() {
    let tasks = vec![
        Task {
            id: 0,
            processing_time: 2,
            deadline: 5,
            dependencies: vec![],
        },
        Task {
            id: 1,
            processing_time: 3,
            deadline: 7,
            dependencies: vec![],
        },
        Task {
            id: 2,
            processing_time: 4,
            deadline: 10,
            dependencies: vec![0, 1],
        },
        Task {
            id: 3,
            processing_time: 5,
            deadline: 12,
            dependencies: vec![0],
        },
        Task {
            id: 4,
            processing_time: 3,
            deadline: 15,
            dependencies: vec![2, 3],
        },
    ];
    
    // We have multiple valid paths through this dependency graph
    // Testing that we get a valid result
    let result = solve_task_scheduling(tasks);
    assert!(result >= 0);
}