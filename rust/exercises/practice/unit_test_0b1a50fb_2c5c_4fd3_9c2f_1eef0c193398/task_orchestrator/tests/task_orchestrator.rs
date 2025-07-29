use std::collections::{HashMap, HashSet};

/// Helper function to validate that the schedule respects task dependencies.
/// `schedule` is a Vec of (worker_id, task_id) representing the order in which tasks are executed.
/// `dependencies` is a list of (parent, child) that must be enforced: parent must appear before child.
fn validate_dependencies(schedule: &[(usize, usize)], dependencies: &[(usize, usize)]) {
    // Map each task_id to its execution index.
    let mut order = HashMap::new();
    for (index, &(_, task_id)) in schedule.iter().enumerate() {
        order.insert(task_id, index);
    }
    for &(parent, child) in dependencies {
        let parent_index = order.get(&parent)
            .expect("Parent task not found in schedule");
        let child_index = order.get(&child)
            .expect("Child task not found in schedule");
        assert!(parent_index < child_index, "Task {} should execute before {}", parent, child);
    }
}

/// Helper function to validate that each task is executed exactly once.
fn validate_all_tasks_executed(schedule: &[(usize, usize)], expected_tasks: &HashSet<usize>) {
    let mut executed_tasks = HashSet::new();
    for &(_, task_id) in schedule {
        assert!(expected_tasks.contains(&task_id), "Task {} is not expected", task_id);
        let inserted = executed_tasks.insert(task_id);
        assert!(inserted, "Task {} executed more than once", task_id);
    }
    assert_eq!(executed_tasks, *expected_tasks, "Not all tasks were executed");
}

/// Test case using a simple single task with no dependencies.
#[test]
fn test_single_task() {
    let n: usize = 1;
    let capacity: usize = 10;
    let tasks = vec![(1, 5, 2)]; // (task_id, cost, priority)
    let dependencies: Vec<(usize, usize)> = vec![];
    let initial_tasks = vec![1];

    let schedule = task_orchestrator::execute_workflow(n, capacity, tasks, dependencies.clone(), initial_tasks);
    
    // Check that exactly one task is executed.
    assert_eq!(schedule.len(), 1);
    // Validate that task 1 is executed.
    let expected_tasks: HashSet<usize> = vec![1].into_iter().collect();
    validate_all_tasks_executed(&schedule, &expected_tasks);
}

/// Test case using linear dependencies: 1 -> 2 -> 3.
#[test]
fn test_linear_dependencies() {
    let n: usize = 2;
    let capacity: usize = 10;
    let tasks = vec![
        (1, 3, 2),  // Task 1: cost 3, priority 2
        (2, 4, 3),  // Task 2: cost 4, priority 3
        (3, 2, 1),  // Task 3: cost 2, priority 1
    ];
    let dependencies = vec![(1, 2), (2, 3)];
    let initial_tasks = vec![1];

    let schedule = task_orchestrator::execute_workflow(n, capacity, tasks, dependencies.clone(), initial_tasks);
    
    // Check that all tasks are executed.
    let expected_tasks: HashSet<usize> = vec![1, 2, 3].into_iter().collect();
    validate_all_tasks_executed(&schedule, &expected_tasks);
    // Validate dependency order.
    validate_dependencies(&schedule, &dependencies);
}

/// Test case using diamond dependencies:
///        1
///       / \
///      2   3
///       \ /
///        4
#[test]
fn test_diamond_dependencies() {
    let n: usize = 3;
    let capacity: usize = 15;
    let tasks = vec![
        (1, 5, 3),
        (2, 4, 2),
        (3, 3, 2),
        (4, 6, 5),
    ];
    let dependencies = vec![(1, 2), (1, 3), (2, 4), (3, 4)];
    let initial_tasks = vec![1];

    let schedule = task_orchestrator::execute_workflow(n, capacity, tasks, dependencies.clone(), initial_tasks);
    
    let expected_tasks: HashSet<usize> = vec![1, 2, 3, 4].into_iter().collect();
    validate_all_tasks_executed(&schedule, &expected_tasks);
    validate_dependencies(&schedule, &dependencies);
}

/// Test case using a more complex workflow with multiple initial tasks and non-trivial resource constraints.
/// The tasks and dependencies are constructed to force the scheduler to respect both capacity and priority constraints.
#[test]
fn test_complex_workflow() {
    let n: usize = 4;
    let capacity: usize = 20;
    // Define tasks: (task_id, cost, priority)
    // Task 1, 2 are initial tasks.
    // Task 3 depends on 1 and 2.
    // Task 4 depends on 2.
    // Task 5 depends on 3 and 4.
    // Task 6 depends on 5.
    let tasks = vec![
        (1, 7, 3),
        (2, 5, 4),
        (3, 6, 5),
        (4, 4, 3),
        (5, 8, 6),
        (6, 3, 2),
    ];
    let dependencies = vec![(1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)];
    let initial_tasks = vec![1, 2];

    let schedule = task_orchestrator::execute_workflow(n, capacity, tasks, dependencies.clone(), initial_tasks);
    
    let expected_tasks: HashSet<usize> = vec![1, 2, 3, 4, 5, 6].into_iter().collect();
    validate_all_tasks_executed(&schedule, &expected_tasks);
    validate_dependencies(&schedule, &dependencies);

    // Additionally, ensure that tasks with higher priority and lower cost are scheduled first when available.
    // Since task 2 (priority 4, cost 5) and task 1 (priority 3, cost 7) are both initial,
    // task 2 should be scheduled before task 1.
    let pos_task1 = schedule.iter().position(|&(_, task_id)| task_id == 1)
        .expect("Task 1 not executed");
    let pos_task2 = schedule.iter().position(|&(_, task_id)| task_id == 2)
        .expect("Task 2 not executed");
    assert!(pos_task2 < pos_task1, "Task 2 should execute before Task 1 due to higher priority");
}