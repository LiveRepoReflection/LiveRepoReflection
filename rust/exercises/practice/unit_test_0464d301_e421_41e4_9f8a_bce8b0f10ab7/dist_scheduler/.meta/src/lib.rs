pub fn schedule_tasks(
    worker_capacities: &Vec<usize>,
    task_loads: &Vec<usize>,
    data_dependencies: &Vec<(usize, usize, u32)>,
    network_bandwidth: &Vec<Vec<u32>>,
) -> Vec<usize> {
    let num_workers = worker_capacities.len();
    let num_tasks = task_loads.len();

    // Build dependency graph and in-degree count for topological sort.
    let mut graph: Vec<Vec<(usize, u32)>> = vec![vec![]; num_tasks];
    let mut in_degree: Vec<usize> = vec![0; num_tasks];
    for &(u, v, data_size) in data_dependencies.iter() {
        graph[u].push((v, data_size));
        in_degree[v] += 1;
    }

    // Kahn's algorithm for topological sort.
    let mut queue = std::collections::VecDeque::new();
    for i in 0..num_tasks {
        if in_degree[i] == 0 {
            queue.push_back(i);
        }
    }
    let mut topo_order = Vec::with_capacity(num_tasks);
    while let Some(task) = queue.pop_front() {
        topo_order.push(task);
        for &(neighbor, _) in &graph[task] {
            in_degree[neighbor] -= 1;
            if in_degree[neighbor] == 0 {
                queue.push_back(neighbor);
            }
        }
    }
    if topo_order.len() != num_tasks {
        panic!("Cycle detected in task dependencies");
    }

    // Prepare dependency list for each task.
    let mut dependencies: Vec<Vec<(usize, u32)>> = vec![vec![]; num_tasks];
    for &(u, v, data_size) in data_dependencies.iter() {
        dependencies[v].push((u, data_size));
    }

    // Initialize scheduling state.
    let mut assignment = vec![0; num_tasks];
    let mut worker_finish_times = vec![0.0f64; num_workers];
    let mut task_finish_times = vec![0.0f64; num_tasks];

    // Process tasks in topological order.
    for &task in topo_order.iter() {
        let task_load = task_loads[task] as f64;
        let mut best_worker = 0;
        let mut best_finish_time = std::f64::INFINITY;
        // Evaluate each worker for task assignment.
        for worker in 0..num_workers {
            // Earliest start is the worker's available time.
            let mut earliest_start = worker_finish_times[worker];
            // Consider dependency communications.
            for &(dep, data_size) in &dependencies[task] {
                let dep_finish = task_finish_times[dep];
                let comm_delay = if assignment[dep] == worker {
                    0.0
                } else {
                    let bw = network_bandwidth[assignment[dep]][worker] as f64;
                    (data_size as f64) / bw
                };
                let arrival = dep_finish + comm_delay;
                if arrival > earliest_start {
                    earliest_start = arrival;
                }
            }
            // Compute processing time on this worker.
            let proc_time = task_load / (worker_capacities[worker] as f64);
            let finish_time = earliest_start + proc_time;
            if finish_time < best_finish_time {
                best_finish_time = finish_time;
                best_worker = worker;
            }
        }
        // Assign task and update times.
        assignment[task] = best_worker;
        worker_finish_times[best_worker] = best_finish_time;
        task_finish_times[task] = best_finish_time;
    }
    assignment
}