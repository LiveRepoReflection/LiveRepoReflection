use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

#[derive(Eq, PartialEq)]
struct ReadyTask {
    priority: usize,
    cost: usize,
    task_id: usize,
}

impl Ord for ReadyTask {
    fn cmp(&self, other: &Self) -> Ordering {
        // Higher priority comes first. If same priority, lower cost comes first.
        match self.priority.cmp(&other.priority) {
            Ordering::Equal => other.cost.cmp(&self.cost),
            other_order => other_order,
        }
    }
}

impl PartialOrd for ReadyTask {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

struct Worker {
    id: usize,
    remaining: usize,
    busy: bool,
}

impl Worker {
    fn new(id: usize, capacity: usize) -> Self {
        Worker {
            id,
            remaining: capacity,
            busy: false,
        }
    }
}

/// Execute the given workflow according to the task orchestration scheduling.
///
/// n: number of worker nodes.
/// capacity: capacity for each worker.
/// tasks: Vec of (task_id, cost, priority)
/// dependencies: Vec of (parent_task_id, child_task_id)
/// initial_tasks: Vec of task_ids that are ready to run initially.
///
/// Returns a Vec of (worker_id, task_id) in the order tasks started execution.
pub fn execute_workflow(
    n: usize,
    capacity: usize,
    tasks: Vec<(usize, usize, usize)>,
    dependencies: Vec<(usize, usize)>,
    initial_tasks: Vec<usize>,
) -> Vec<(usize, usize)> {
    // Build task info map: task_id -> (cost, priority)
    let mut task_info: HashMap<usize, (usize, usize)> = HashMap::new();
    for (task_id, cost, priority) in tasks.iter() {
        task_info.insert(*task_id, (*cost, *priority));
    }
    
    // Build dependency count and children mapping.
    let mut dep_count: HashMap<usize, usize> = HashMap::new();
    let mut children: HashMap<usize, Vec<usize>> = HashMap::new();
    
    // Initialize dependency count to zero for all tasks.
    for (&task_id, _) in task_info.iter() {
        dep_count.insert(task_id, 0);
    }
    
    for &(parent, child) in dependencies.iter() {
        let counter = dep_count.entry(child).or_insert(0);
        *counter += 1;
        children.entry(parent).or_insert_with(Vec::new).push(child);
    }
    
    // Override dependency count for tasks in initial_tasks to 0.
    for &tid in initial_tasks.iter() {
        dep_count.insert(tid, 0);
    }
    
    // Build initial ready queue: tasks with dependency count == 0.
    let mut ready_queue = BinaryHeap::new();
    for (&task_id, &count) in dep_count.iter() {
        if count == 0 {
            if let Some(&(cost, priority)) = task_info.get(&task_id) {
                ready_queue.push(ReadyTask { priority, cost, task_id });
            }
        }
    }
    
    // Initialize workers.
    let mut workers: Vec<Worker> = (0..n).map(|id| Worker::new(id, capacity)).collect();
    
    // Channel for completions.
    let (tx, rx) = mpsc::channel();
    
    // For joining worker threads.
    let mut join_handles = Vec::new();
    
    // Schedule result vector.
    let mut schedule: Vec<(usize, usize)> = Vec::new();
    
    // Set of completed tasks.
    let mut completed_tasks: HashSet<usize> = HashSet::new();
    
    // Total number of tasks.
    let total_tasks = task_info.len();
    
    // In-flight tasks count.
    let mut in_progress = 0;
    
    // Scheduler loop.
    while completed_tasks.len() < total_tasks {
        let mut temp_tasks = Vec::new();
        let mut assignment_made = false;
        
        // Try to assign tasks from the ready queue.
        while let Some(task) = ready_queue.pop() {
            // Find first idle worker with enough capacity.
            let mut assigned = false;
            for worker in workers.iter_mut() {
                if !worker.busy && worker.remaining >= task.cost {
                    // Assign task to this worker.
                    worker.busy = true;
                    worker.remaining -= task.cost;
                    schedule.push((worker.id, task.task_id));
                    
                    // Spawn a thread to simulate execution.
                    let tx_clone = tx.clone();
                    let worker_id = worker.id;
                    let task_id = task.task_id;
                    let handle = thread::spawn(move || {
                        // Simulate task execution.
                        thread::sleep(Duration::from_millis(10));
                        tx_clone.send((worker_id, task_id)).unwrap();
                    });
                    join_handles.push(handle);
                    
                    in_progress += 1;
                    assigned = true;
                    assignment_made = true;
                    break;
                }
            }
            if !assigned {
                // Cannot assign this task now; save it for later.
                temp_tasks.push(task);
            }
        }
        
        // Push back tasks that were not assigned.
        for task in temp_tasks.into_iter() {
            ready_queue.push(task);
        }
        
        // If no assignment was made but there are tasks in progress, wait for a task to complete.
        if !assignment_made && in_progress > 0 {
            let (worker_id, finished_task) = rx.recv().unwrap();
            in_progress -= 1;
            completed_tasks.insert(finished_task);
            // Mark worker as idle.
            if let Some(worker) = workers.iter_mut().find(|w| w.id == worker_id) {
                worker.busy = false;
            }
            // Update dependency counts for children of the finished task.
            if let Some(child_list) = children.get(&finished_task) {
                for &child in child_list.iter() {
                    let count = dep_count.get_mut(&child).unwrap();
                    if *count > 0 {
                        *count -= 1;
                    }
                    if *count == 0 {
                        if let Some(&(cost, priority)) = task_info.get(&child) {
                            ready_queue.push(ReadyTask { priority, cost, task_id: child });
                        }
                    }
                }
            }
        }
        // If ready_queue is empty and no tasks are in progress but not all tasks completed,
        // then break (should not happen if the input is a valid DAG and capacities are sufficient).
        if ready_queue.is_empty() && in_progress == 0 && completed_tasks.len() < total_tasks {
            break;
        }
        
        // Also, if assignments were made, try to drain completions without blocking.
        while let Ok((worker_id, finished_task)) = rx.try_recv() {
            in_progress -= 1;
            completed_tasks.insert(finished_task);
            if let Some(worker) = workers.iter_mut().find(|w| w.id == worker_id) {
                worker.busy = false;
            }
            if let Some(child_list) = children.get(&finished_task) {
                for &child in child_list.iter() {
                    let count = dep_count.get_mut(&child).unwrap();
                    if *count > 0 {
                        *count -= 1;
                    }
                    if *count == 0 {
                        if let Some(&(cost, priority)) = task_info.get(&child) {
                            ready_queue.push(ReadyTask { priority, cost, task_id: child });
                        }
                    }
                }
            }
        }
    }
    
    // Ensure all spawned threads are joined.
    for handle in join_handles {
        let _ = handle.join();
    }
    
    schedule
}