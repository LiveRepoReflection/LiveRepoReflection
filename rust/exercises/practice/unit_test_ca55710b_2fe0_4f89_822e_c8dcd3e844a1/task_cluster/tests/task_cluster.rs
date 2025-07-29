use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use task_cluster::{Scheduler, TaskStatus};

#[test]
fn test_task_submission_and_completion() {
    let mut scheduler = Scheduler::new();
    scheduler.register_worker(1);
    scheduler.submit_task(1001, "task1_cmd".to_string()).unwrap();
    // Simulate scheduler run, which assigns the task to registered worker(s)
    scheduler.run();
    let status = scheduler.get_task_status(1001).unwrap();
    assert_eq!(status, TaskStatus::Completed);
}

#[test]
fn test_worker_registration_and_deregistration() {
    let mut scheduler = Scheduler::new();
    scheduler.register_worker(1);
    scheduler.register_worker(2);
    // Assuming get_worker_count returns the current number of registered workers.
    assert_eq!(scheduler.get_worker_count(), 2);
    scheduler.deregister_worker(1);
    assert_eq!(scheduler.get_worker_count(), 1);
}

#[test]
fn test_fault_tolerance_and_task_retry() {
    let mut scheduler = Scheduler::new();
    scheduler.register_worker(1);
    scheduler.register_worker(2);
    // Submit a task that will experience a simulated failure before succeeding.
    scheduler.submit_task(2001, "task_fail_then_retry".to_string()).unwrap();

    // First attempt: assign to worker 1 and simulate failure.
    scheduler.assign_task_to_worker(2001, 1);
    scheduler.simulate_worker_failure(1).unwrap();

    // Scheduler should retry and assign to worker 2.
    scheduler.assign_task_to_worker(2001, 2);
    scheduler.run();
    let status = scheduler.get_task_status(2001).unwrap();
    // If the retry succeeds, the task should be marked as Completed.
    assert_eq!(status, TaskStatus::Completed);
}

#[test]
fn test_retry_limit_exceeded() {
    let mut scheduler = Scheduler::new();
    scheduler.register_worker(1);
    // Submit a task that is expected to fail repeatedly.
    scheduler.submit_task(3001, "task_always_fail".to_string()).unwrap();
    // Simulate three consecutive failures.
    for _ in 0..3 {
        scheduler.assign_task_to_worker(3001, 1);
        scheduler.simulate_worker_failure(1).unwrap();
    }
    // After exceeding retry limit, the task should be marked as Failed.
    scheduler.assign_task_to_worker(3001, 1);
    scheduler.run();
    let status = scheduler.get_task_status(3001).unwrap();
    assert_eq!(status, TaskStatus::Failed);
}

#[test]
fn test_concurrent_task_submissions() {
    let scheduler = Arc::new(Mutex::new(Scheduler::new()));
    {
        let mut sched = scheduler.lock().unwrap();
        // Register multiple workers.
        for worker_id in 1..=5 {
            sched.register_worker(worker_id);
        }
    }

    let handles: Vec<_> = (0..10)
        .map(|i| {
            let scheduler_clone = Arc::clone(&scheduler);
            thread::spawn(move || {
                let mut sched = scheduler_clone.lock().unwrap();
                sched.submit_task(4000 + i, format!("cmd_{}", i)).unwrap();
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    // Simulate scheduler run to process concurrently submitted tasks.
    scheduler.lock().unwrap().run();

    for i in 0..10 {
        let status = scheduler.lock().unwrap().get_task_status(4000 + i).unwrap();
        assert_eq!(status, TaskStatus::Completed);
    }
}

#[test]
fn test_worker_registration_during_runtime() {
    let mut scheduler = Scheduler::new();
    scheduler.register_worker(1);
    scheduler.submit_task(5001, "initial_task".to_string()).unwrap();
    scheduler.run();
    let status_initial = scheduler.get_task_status(5001).unwrap();
    assert_eq!(status_initial, TaskStatus::Completed);

    // Dynamically register a new worker while tasks are pending.
    scheduler.register_worker(2);
    scheduler.submit_task(5002, "new_task".to_string()).unwrap();
    scheduler.run();
    let status_new = scheduler.get_task_status(5002).unwrap();
    assert_eq!(status_new, TaskStatus::Completed);
}