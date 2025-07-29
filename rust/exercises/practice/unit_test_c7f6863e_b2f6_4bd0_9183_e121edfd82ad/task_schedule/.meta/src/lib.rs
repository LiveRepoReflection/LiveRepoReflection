pub fn minimize_lateness(tasks: &[(i32, i32, Vec<usize>)]) -> i32 {
    if tasks.is_empty() {
        return 0;
    }
    let n = tasks.len();

    // Build graph structures.
    // successors[i] holds all tasks that depend on task i.
    // predecessors[i] holds all tasks that task i depends on.
    let mut successors: Vec<Vec<usize>> = vec![Vec::new(); n];
    let mut predecessors: Vec<Vec<usize>> = vec![Vec::new(); n];

    for (i, &(_, _, ref deps)) in tasks.iter().enumerate() {
        for &dep in deps {
            // task i depends on dep: dep -> i.
            successors[dep].push(i);
            predecessors[i].push(dep);
        }
    }

    // outdegree[i] is the number of successors of task i.
    let mut outdegree: Vec<usize> = successors.iter().map(|v| v.len()).collect();

    // Use Lawler's algorithm (scheduling in reverse order).
    // We use a min-heap keyed on the task deadline.
    use std::collections::BinaryHeap;
    use std::cmp::Reverse;
    let mut heap = BinaryHeap::new();

    // Push all tasks with no successors (sink tasks) into the heap.
    for i in 0..n {
        if outdegree[i] == 0 {
            heap.push(Reverse((tasks[i].1, i)));
        }
    }

    // order_rev will store the tasks in reverse scheduled order.
    let mut order_rev = Vec::with_capacity(n);
    // Track unscheduled tasks.
    let mut unscheduled = vec![true; n];
    let mut remaining = n;

    while remaining > 0 {
        if heap.is_empty() {
            // Cycle detected or unsolvable dependency.
            return -1;
        }
        let Reverse((_, node)) = heap.pop().unwrap();
        if !unscheduled[node] {
            continue;
        }
        unscheduled[node] = false;
        order_rev.push(node);
        remaining -= 1;

        // For each predecessor, remove the edge from the predecessor to this node.
        for &pred in &predecessors[node] {
            if unscheduled[pred] {
                outdegree[pred] -= 1;
                if outdegree[pred] == 0 {
                    heap.push(Reverse((tasks[pred].1, pred)));
                }
            }
        }
    }

    // Reverse the order to get the actual schedule order (from start to finish).
    order_rev.reverse();

    // Simulate the schedule forward, and check if every task finishes by its deadline.
    let mut current_time = 0;
    for &task_idx in &order_rev {
        let exec = tasks[task_idx].0;
        let deadline = tasks[task_idx].1;
        current_time += exec;
        if current_time > deadline {
            return -1;
        }
    }
    0
}