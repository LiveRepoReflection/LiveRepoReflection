use std::collections::{HashMap, HashSet, VecDeque};

pub struct Task {
    pub id: usize,
    pub processing_time: i32,
    pub deadline: i32,
    pub dependencies: Vec<usize>,
}

// Utility for detection of circular dependencies
fn has_circular_dependency(tasks: &[Task]) -> bool {
    let n = tasks.len();
    let mut graph: HashMap<usize, Vec<usize>> = HashMap::new();
    
    // Build adjacency list
    for task in tasks {
        for &dep in &task.dependencies {
            graph.entry(dep).or_default().push(task.id);
        }
        // Ensure all nodes exist in the graph, even if they have no outgoing edges
        graph.entry(task.id).or_default();
    }
    
    // Check for cycles with DFS
    let mut visited = vec![false; n];
    let mut rec_stack = vec![false; n];
    
    for i in 0..n {
        if !visited[i] && is_cyclic_util(i, &graph, &mut visited, &mut rec_stack) {
            return true;
        }
    }
    
    false
}

fn is_cyclic_util(
    v: usize,
    graph: &HashMap<usize, Vec<usize>>,
    visited: &mut [bool],
    rec_stack: &mut [bool],
) -> bool {
    // Mark the current node as visited and part of recursion stack
    visited[v] = true;
    rec_stack[v] = true;
    
    // Recur for all neighbors
    if let Some(neighbors) = graph.get(&v) {
        for &neighbor in neighbors {
            if !visited[neighbor] && is_cyclic_util(neighbor, graph, visited, rec_stack) {
                return true;
            } else if rec_stack[neighbor] {
                return true;
            }
        }
    }
    
    // Remove the vertex from recursion stack
    rec_stack[v] = false;
    false
}

// Calculate earliest start times for all tasks
fn calculate_earliest_start_times(tasks: &[Task]) -> Vec<i32> {
    let n = tasks.len();
    let mut earliest_start = vec![0; n];
    let mut in_degree = vec![0; n];
    let mut adj_list: Vec<Vec<usize>> = vec![Vec::new(); n];
    
    // Build the adjacency list and count in-degrees
    for task in tasks {
        for &dep in &task.dependencies {
            adj_list[dep].push(task.id);
            in_degree[task.id] += 1;
        }
    }
    
    // Initialize queue with all nodes having no dependencies
    let mut queue: VecDeque<usize> = VecDeque::new();
    for i in 0..n {
        if in_degree[i] == 0 {
            queue.push_back(i);
        }
    }
    
    // Topological sort to calculate earliest start times
    while let Some(current) = queue.pop_front() {
        for &next in &adj_list[current] {
            earliest_start[next] = earliest_start[next].max(
                earliest_start[current] + tasks[current].processing_time
            );
            in_degree[next] -= 1;
            if in_degree[next] == 0 {
                queue.push_back(next);
            }
        }
    }
    
    earliest_start
}

// Main solution function
pub fn solve_task_scheduling(tasks: Vec<Task>) -> i32 {
    if tasks.is_empty() {
        return 0;
    }
    
    // Check for circular dependencies
    if has_circular_dependency(&tasks) {
        return -1;
    }
    
    // Calculate earliest possible start times
    let earliest_start = calculate_earliest_start_times(&tasks);
    
    // Get eligible tasks (respecting dependencies)
    let n = tasks.len();
    let mut best_tardiness = i32::MAX;
    
    // Create a schedule state for branch and bound
    let mut schedule: Vec<usize> = Vec::with_capacity(n);
    let mut scheduled: HashSet<usize> = HashSet::new();
    
    // Branch and bound to find optimal schedule
    fn backtrack(
        tasks: &[Task],
        earliest_start: &[i32],
        schedule: &mut Vec<usize>,
        scheduled: &mut HashSet<usize>,
        current_time: i32,
        current_tardiness: i32,
        best_tardiness: &mut i32,
    ) {
        if schedule.len() == tasks.len() {
            // We have a complete schedule
            *best_tardiness = (*best_tardiness).min(current_tardiness);
            return;
        }
        
        // Pruning: If current tardiness already exceeds best found, stop exploring
        if current_tardiness >= *best_tardiness {
            return;
        }
        
        // Find eligible tasks (all dependencies scheduled)
        let mut eligible: Vec<usize> = Vec::new();
        for (i, task) in tasks.iter().enumerate() {
            // Skip already scheduled tasks
            if scheduled.contains(&i) {
                continue;
            }
            
            // Check if all dependencies are scheduled
            let all_deps_scheduled = task.dependencies.iter().all(|dep| scheduled.contains(dep));
            if all_deps_scheduled {
                eligible.push(i);
            }
        }
        
        // Try each eligible task next
        for &task_id in &eligible {
            let task = &tasks[task_id];
            let task_start_time = current_time.max(earliest_start[task_id]);
            let task_finish_time = task_start_time + task.processing_time;
            let task_tardiness = (task_finish_time - task.deadline).max(0);
            let additional_tardiness = task_tardiness * task.processing_time;
            
            // Add task to schedule
            schedule.push(task_id);
            scheduled.insert(task_id);
            
            // Recurse
            backtrack(
                tasks,
                earliest_start,
                schedule,
                scheduled,
                task_finish_time,
                current_tardiness + additional_tardiness,
                best_tardiness,
            );
            
            // Backtrack
            scheduled.remove(&task_id);
            schedule.pop();
        }
    }
    
    // Start the recursive backtracking
    backtrack(
        &tasks,
        &earliest_start,
        &mut schedule,
        &mut scheduled,
        0,
        0,
        &mut best_tardiness,
    );
    
    // Return the best schedule's tardiness
    if best_tardiness == i32::MAX {
        // This should not happen given the earlier circular dependency check
        -1
    } else {
        best_tardiness
    }
}