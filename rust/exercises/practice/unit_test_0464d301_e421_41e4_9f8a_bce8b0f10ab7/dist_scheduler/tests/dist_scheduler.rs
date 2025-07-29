use dist_scheduler::schedule_tasks;

fn validate_schedule(schedule: &Vec<usize>, num_tasks: usize, num_workers: usize) {
    // Ensure the schedule has exactly one assignment per task.
    assert_eq!(schedule.len(), num_tasks);
    // Each worker id must be within the valid range.
    for &worker in schedule.iter() {
        assert!(worker < num_workers, "Worker index {} out of range", worker);
    }
}

#[test]
fn test_single_worker() {
    let num_workers = 1;
    let worker_capacities = vec![100];
    let task_loads = vec![10, 20, 30, 40];
    let data_dependencies = vec![
        (0, 1, 5),
        (1, 2, 10),
        (2, 3, 15)
    ];
    let network_bandwidth = vec![
        vec![100]
    ];

    let schedule = schedule_tasks(&worker_capacities, &task_loads, &data_dependencies, &network_bandwidth);
    validate_schedule(&schedule, task_loads.len(), num_workers);

    // For a single worker system, every task must be assigned to worker 0.
    for &worker in schedule.iter() {
        assert_eq!(worker, 0);
    }
}

#[test]
fn test_no_dependencies() {
    let num_workers = 3;
    let worker_capacities = vec![50, 75, 100];
    let task_loads = vec![10, 20, 30, 40, 15, 25];
    let data_dependencies: Vec<(usize, usize, u32)> = vec![];
    let network_bandwidth = vec![
        vec![100, 80, 60],
        vec![80, 100, 70],
        vec![60, 70, 100]
    ];

    let schedule = schedule_tasks(&worker_capacities, &task_loads, &data_dependencies, &network_bandwidth);
    validate_schedule(&schedule, task_loads.len(), num_workers);
}

#[test]
fn test_with_dependencies() {
    let num_workers = 3;
    let worker_capacities = vec![70, 80, 90];
    let task_loads = vec![20, 20, 20, 20, 20];
    // Define a chain of dependencies: task 0 -> 1, 1 -> 2, 2 -> 3, and 3 -> 4.
    let data_dependencies = vec![
        (0, 1, 10),
        (1, 2, 15),
        (2, 3, 20),
        (3, 4, 25)
    ];
    let network_bandwidth = vec![
        vec![100, 50, 50],
        vec![50, 100, 75],
        vec![50, 75, 100]
    ];

    let schedule = schedule_tasks(&worker_capacities, &task_loads, &data_dependencies, &network_bandwidth);
    validate_schedule(&schedule, task_loads.len(), num_workers);
}

#[test]
fn test_heterogeneous_system() {
    let num_workers = 5;
    let worker_capacities = vec![30, 60, 90, 50, 80];
    let task_loads = vec![10, 15, 20, 25, 30, 35, 40, 45, 50];
    let data_dependencies = vec![
        (0, 3, 5),
        (1, 4, 10),
        (2, 5, 15),
        (3, 6, 20),
        (4, 7, 25),
        (5, 8, 30)
    ];
    let network_bandwidth = vec![
        vec![100, 80, 60, 70, 90],
        vec![80, 100, 65, 75, 85],
        vec![60, 65, 100, 55, 75],
        vec![70, 75, 55, 100, 80],
        vec![90, 85, 75, 80, 100]
    ];

    let schedule = schedule_tasks(&worker_capacities, &task_loads, &data_dependencies, &network_bandwidth);
    validate_schedule(&schedule, task_loads.len(), num_workers);
}

#[test]
fn test_large_scale() {
    let num_workers = 10;
    let worker_capacities = vec![50, 60, 70, 80, 90, 100, 110, 120, 130, 140];
    let num_tasks = 50;
    let mut task_loads = Vec::new();
    for i in 0..num_tasks {
        task_loads.push((i % 10) + 10);
    }
    let mut data_dependencies = Vec::new();
    // Each task depends on its immediate predecessor.
    for i in 1..num_tasks {
        data_dependencies.push((i - 1, i, (5 + (i % 5)) as u32));
    }
    let num_workers = worker_capacities.len();
    let mut network_bandwidth = vec![vec![100; num_workers]; num_workers];
    // Vary the bandwidth slightly.
    for i in 0..num_workers {
        for j in 0..num_workers {
            network_bandwidth[i][j] = 80 + ((i + j) % 21) as u32;
        }
    }

    let schedule = schedule_tasks(&worker_capacities, &task_loads, &data_dependencies, &network_bandwidth);
    validate_schedule(&schedule, task_loads.len(), num_workers);
}