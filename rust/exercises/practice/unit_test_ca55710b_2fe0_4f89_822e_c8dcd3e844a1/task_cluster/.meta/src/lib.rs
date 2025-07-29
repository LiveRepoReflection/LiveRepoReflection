use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TaskStatus {
    Pending,
    InProgress,
    Completed,
    Failed,
}

#[derive(Debug, Clone)]
struct Task {
    id: u32,
    command: String,
    status: TaskStatus,
    attempts: u32,
    assigned_worker: Option<u32>,
}

pub struct Scheduler {
    tasks: HashMap<u32, Task>,
    workers: HashSet<u32>,
}

impl Scheduler {
    pub fn new() -> Self {
        Scheduler {
            tasks: HashMap::new(),
            workers: HashSet::new(),
        }
    }

    pub fn register_worker(&mut self, worker_id: u32) {
        self.workers.insert(worker_id);
    }

    pub fn deregister_worker(&mut self, worker_id: u32) {
        self.workers.remove(&worker_id);
    }

    pub fn get_worker_count(&self) -> usize {
        self.workers.len()
    }

    pub fn submit_task(&mut self, task_id: u32, command: String) -> Result<(), String> {
        if self.tasks.contains_key(&task_id) {
            return Err(format!("Task {} already exists", task_id));
        }
        let task = Task {
            id: task_id,
            command,
            status: TaskStatus::Pending,
            attempts: 0,
            assigned_worker: None,
        };
        self.tasks.insert(task_id, task);
        Ok(())
    }

    pub fn get_task_status(&self, task_id: u32) -> Option<TaskStatus> {
        self.tasks.get(&task_id).map(|t| t.status.clone())
    }

    pub fn assign_task_to_worker(&mut self, task_id: u32, worker_id: u32) {
        if !self.workers.contains(&worker_id) {
            return;
        }
        if let Some(task) = self.tasks.get_mut(&task_id) {
            // Only assign if task is pending or was previously in progress.
            if task.status == TaskStatus::Pending || task.status == TaskStatus::InProgress {
                task.assigned_worker = Some(worker_id);
                task.status = TaskStatus::InProgress;
            }
        }
    }

    // Simulate a worker failure: any task in progress on the failed worker 
    // is marked as pending for a retry (if retry limit not exceeded) or failed.
    pub fn simulate_worker_failure(&mut self, worker_id: u32) -> Result<(), String> {
        let mut found = false;
        for task in self.tasks.values_mut() {
            if task.assigned_worker == Some(worker_id) && task.status == TaskStatus::InProgress {
                found = true;
                task.assigned_worker = None;
                task.attempts += 1;
                if task.attempts >= 3 {
                    task.status = TaskStatus::Failed;
                } else {
                    task.status = TaskStatus::Pending;
                }
            }
        }
        if found {
            Ok(())
        } else {
            Err(format!("No task found assigned to worker {}", worker_id))
        }
    }

    // The run function simulates executing tasks.
    // For each task that is pending or in progress, if it has an assigned worker,
    // then simulate its execution and mark it as completed.
    // For pending tasks without an assigned worker, try to assign an arbitrary available worker.
    pub fn run(&mut self) {
        // Iterate over tasks and assign workers if not assigned.
        for task in self.tasks.values_mut() {
            if (task.status == TaskStatus::Pending) && (task.assigned_worker.is_none()) {
                if let Some(&worker) = self.workers.iter().next() {
                    task.assigned_worker = Some(worker);
                    task.status = TaskStatus::InProgress;
                }
            }
        }
        // Simulate execution: complete in-progress tasks.
        for task in self.tasks.values_mut() {
            if task.status == TaskStatus::InProgress {
                // Here we simulate the execution (e.g., delay, compute, etc.)
                // For simplicity we mark it as completed.
                task.status = TaskStatus::Completed;
                task.assigned_worker = None;
            }
        }
    }
}