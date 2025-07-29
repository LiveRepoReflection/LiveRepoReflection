use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum TaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
}

#[derive(Debug, Clone)]
struct Task {
    id: String,
    description: String,
    priority: i32,
    status: TaskStatus,
    assigned_worker: Option<u32>,
}

#[derive(Debug, Clone)]
struct Worker {
    id: u32,
    capacity: usize,
    running_tasks: usize,
    active: bool,
}

pub struct Scheduler {
    tasks: HashMap<String, Task>,
    workers: HashMap<u32, Worker>,
    task_counter: u64,
    worker_counter: u32,
}

impl Scheduler {
    pub fn new() -> Self {
        Scheduler {
            tasks: HashMap::new(),
            workers: HashMap::new(),
            task_counter: 0,
            worker_counter: 0,
        }
    }

    // Submit a new task with the given description and priority.
    // Returns the task id.
    pub fn submit_task(&mut self, description: String, priority: i32) -> String {
        let task_id = self.task_counter.to_string();
        self.task_counter += 1;
        let task = Task {
            id: task_id.clone(),
            description,
            priority,
            status: TaskStatus::Pending,
            assigned_worker: None,
        };
        self.tasks.insert(task_id.clone(), task);
        task_id
    }

    // Returns the status of a task if it exists.
    pub fn query_task_status(&self, task_id: &String) -> Option<TaskStatus> {
        self.tasks.get(task_id).map(|t| t.status.clone())
    }

    // Registers a new worker with a given capacity.
    // Returns the worker id.
    pub fn register_worker(&mut self, capacity: usize) -> u32 {
        let worker_id = self.worker_counter;
        self.worker_counter += 1;
        let worker = Worker {
            id: worker_id,
            capacity,
            running_tasks: 0,
            active: true,
        };
        self.workers.insert(worker_id, worker);
        worker_id
    }

    // Attempts to assign pending tasks to available workers.
    // Returns a vector of (worker_id, task_id) pairs, representing the tasks assigned.
    pub fn assign_tasks(&mut self) -> Vec<(u32, String)> {
        // Collect pending tasks.
        let mut pending_tasks: Vec<&mut Task> = self.tasks
            .values_mut()
            .filter(|task| task.status == TaskStatus::Pending)
            .collect();
        // Sort tasks by descending priority, and if equal, by task id.
        pending_tasks.sort_by(|a, b| {
            b.priority.cmp(&a.priority).then(a.id.cmp(&b.id))
        });

        let mut assignments = Vec::new();

        // Keep trying to assign tasks until we either run out of pending tasks or workers.
        for task in pending_tasks.iter_mut() {
            // Find an active worker with available capacity.
            // Choose the one with the smallest running_tasks (for fairness) and then by id.
            let mut available_worker: Option<&mut Worker> = self.workers
                .values_mut()
                .filter(|worker| worker.active && worker.running_tasks < worker.capacity)
                .min_by(|a, b| {
                    a.running_tasks.cmp(&b.running_tasks).then(a.id.cmp(&b.id))
                });
            if let Some(worker) = available_worker.as_mut() {
                // Assign the task.
                task.status = TaskStatus::Running;
                task.assigned_worker = Some(worker.id);
                worker.running_tasks += 1;
                assignments.push((worker.id, task.id.clone()));
            } else {
                // No available worker for the remaining tasks.
                break;
            }
        }
        assignments
    }

    // Simulates a worker failure and requeues its running tasks.
    pub fn simulate_worker_failure(&mut self, worker_id: &u32) {
        if let Some(worker) = self.workers.get_mut(worker_id) {
            // Mark the worker as inactive.
            worker.active = false;
            worker.running_tasks = 0;
        }
        // Requeue tasks assigned to this worker.
        for task in self.tasks.values_mut() {
            if task.assigned_worker == Some(*worker_id) && task.status == TaskStatus::Running {
                task.status = TaskStatus::Pending;
                task.assigned_worker = None;
            }
        }
    }

    // Reports task completion. If success is true, task becomes Completed; otherwise, Failed.
    // Decrements the worker's running task count.
    pub fn report_task_completion(&mut self, worker_id: &u32, task_id: &String, success: bool) {
        if let Some(task) = self.tasks.get_mut(task_id) {
            if task.assigned_worker == Some(*worker_id) && task.status == TaskStatus::Running {
                task.status = if success { TaskStatus::Completed } else { TaskStatus::Failed };
                task.assigned_worker = None;
                if let Some(worker) = self.workers.get_mut(worker_id) {
                    if worker.running_tasks > 0 {
                        worker.running_tasks -= 1;
                    }
                }
            }
        }
    }
}