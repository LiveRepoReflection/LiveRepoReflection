use task_schedule::minimize_lateness;

#[test]
fn test_empty_tasks() {
    let tasks: Vec<(i32, i32, Vec<usize>)> = vec![];
    // With no tasks, the schedule is trivially feasible.
    assert_eq!(minimize_lateness(&tasks), 0);
}

#[test]
fn test_single_task_feasible() {
    let tasks = vec![(5, 10, vec![])]; // finishes at 5 <= 10
    assert_eq!(minimize_lateness(&tasks), 0);
}

#[test]
fn test_single_task_infeasible() {
    let tasks = vec![(10, 5, vec![])]; // finishes at 10 > 5, no way to schedule earlier.
    assert_eq!(minimize_lateness(&tasks), -1);
}

#[test]
fn test_independent_tasks_infeasible() {
    // Two independent tasks: any schedule will finish one at 3 and the other at 6.
    // For a deadline of 5 on both, at least one will miss its deadline.
    let tasks = vec![(3, 5, vec![]), (3, 5, vec![])];
    assert_eq!(minimize_lateness(&tasks), -1);
}

#[test]
fn test_chain_dependencies_feasible() {
    // Chain of tasks where each task depends on the previous.
    // Schedule: Task 0 -> Task 1 -> Task 2
    // Completion times: 5, 8, 10 respectively.
    let tasks = vec![
        (5, 10, vec![]),    // Task 0, finishes at 5
        (3, 12, vec![0]),   // Task 1, starts after 5, finishes at 8
        (2, 15, vec![1]),   // Task 2, starts after 8, finishes at 10
    ];
    assert_eq!(minimize_lateness(&tasks), 0);
}

#[test]
fn test_complex_dependency_tree_feasible() {
    // Tasks with multiple dependencies.
    // Graph:
    //   Task 0: no dependencies.
    //   Task 1: depends on Task 0.
    //   Task 2: depends on Task 0.
    //   Task 3: depends on Tasks 1 and 2.
    // Optimal ordering: Task 0 (duration 4, deadline 8), then Task 2 (duration 3, deadline 10),
    // then Task 1 (duration 2, deadline 12), then Task 3 (duration 2, deadline 15).
    // Completion times: 4, 7, 9, 11 => All <= deadlines.
    let tasks = vec![
        (4, 8, vec![]),         // Task 0: finishes at 4
        (2, 12, vec![0]),       // Task 1: finishes at 6 or 9 depending on ordering
        (3, 10, vec![0]),       // Task 2: finishes at 7 or 9 depending on ordering
        (2, 15, vec![1, 2]),    // Task 3: after Tasks 1 and 2, finishes by 11 or later
    ];
    assert_eq!(minimize_lateness(&tasks), 0);
}

#[test]
fn test_circular_dependency() {
    // Introduce a cycle: Task 0 depends on Task 1 and Task 1 depends on Task 0.
    let tasks = vec![
        (3, 10, vec![1]), // Task 0 depends on Task 1
        (4, 12, vec![0]), // Task 1 depends on Task 0, forming a cycle.
    ];
    // The cycle makes scheduling impossible.
    assert_eq!(minimize_lateness(&tasks), -1);
}

#[test]
fn test_complex_infeasible_due_to_dependencies() {
    // A scenario where dependencies force a long delay that makes one task miss its deadline.
    // Task 0: no dependency, (3, 5)
    // Task 1: depends on Task 0, (4, 8) --> earliest finish is 7, feasible.
    // Task 2: depends on Task 1, (5, 10) --> earliest finish is 12, deadline 10 missed.
    let tasks = vec![
        (3, 5, vec![]),    // Task 0: finishes at 3
        (4, 8, vec![0]),   // Task 1: finishes at 7
        (5, 10, vec![1]),  // Task 2: finishes at 12 > 10
    ];
    assert_eq!(minimize_lateness(&tasks), -1);
}