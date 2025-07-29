use optimal_scheduler::schedule;

#[test]
fn test_example() {
    let n = 3;
    let time = vec![2, 3, 2];
    let deadline = vec![4, 6, 5];
    let penalty = vec![5, 8, 3];
    let dependencies = vec![vec![], vec![0], vec![0, 1]];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 3);
}

#[test]
fn test_all_on_time() {
    let n = 4;
    let time = vec![1, 2, 3, 4];
    let deadline = vec![2, 4, 6, 10];
    let penalty = vec![5, 5, 5, 5];
    let dependencies = vec![vec![], vec![], vec![], vec![]];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 0);
}

#[test]
fn test_dependency_ordering() {
    let n = 3;
    let time = vec![1, 3, 2];
    let deadline = vec![2, 5, 4];
    let penalty = vec![10, 1, 5];
    // task1 depends on task0, task2 is independent
    let dependencies = vec![vec![], vec![0], vec![]];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 1);
}

#[test]
fn test_chain_dependency() {
    let n = 4;
    let time = vec![5, 4, 3, 2];
    let deadline = vec![4, 8, 10, 12];
    let penalty = vec![3, 5, 7, 9];
    let dependencies = vec![vec![], vec![0], vec![1], vec![2]];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 24);
}

#[test]
fn test_branching_dependencies() {
    let n = 5;
    let time = vec![2, 3, 1, 4, 2];
    let deadline = vec![3, 6, 5, 10, 8];
    let penalty = vec![10, 5, 2, 8, 1];
    let dependencies = vec![
        vec![],      // Task 0 has no dependencies
        vec![0],     // Task 1 depends on Task 0
        vec![0],     // Task 2 depends on Task 0
        vec![1, 2],  // Task 3 depends on Tasks 1 and 2
        vec![2],     // Task 4 depends on Task 2
    ];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 1);
}

#[test]
fn test_empty_tasks() {
    let n = 0;
    let time: Vec<u64> = vec![];
    let deadline: Vec<u64> = vec![];
    let penalty: Vec<u64> = vec![];
    let dependencies: Vec<Vec<usize>> = vec![];
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 0);
}

#[test]
fn test_no_dependencies_penalty() {
    // Tasks with no dependencies; optimal ordering is required to minimize penalty.
    let n = 3;
    let time = vec![4, 2, 3];
    let deadline = vec![3, 6, 8];
    let penalty = vec![7, 4, 10];
    let dependencies = vec![vec![], vec![], vec![]];
    // One optimal ordering: task1, task2, task0 gives cumulative times 2, 5, 9.
    // Task1 finishes by 2 (deadline 6), task2 by 5 (deadline 8), task0 by 9 (deadline 3, incurring penalty 7).
    // Expected total penalty is 7.
    let result = schedule(n, &time, &deadline, &penalty, &dependencies);
    assert_eq!(result, 7);
}