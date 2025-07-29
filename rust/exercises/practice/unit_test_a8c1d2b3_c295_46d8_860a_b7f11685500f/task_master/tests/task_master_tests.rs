use std::collections::HashSet;
use task_master::{Scheduler, TaskStatus};

#[test]
fn test_task_submission() {
    let mut scheduler = Scheduler::new();
    let task_a = scheduler.submit_task("Task A".to_string(), 5);
    let task_b = scheduler.submit_task("Task B".to_string(), 7);
    
    // Verify that newly submitted tasks are in Pending state.
    assert_eq!(scheduler.query_task_status(&task_a), Some(TaskStatus::Pending));
    assert_eq!(scheduler.query_task_status(&task_b), Some(TaskStatus::Pending));
}

#[test]
fn test_task_assignment_priority() {
    let mut scheduler = Scheduler::new();
    // Submit tasks with varying priorities.
    let task_low = scheduler.submit_task("Low priority".to_string(), 1);
    let task_high = scheduler.submit_task("High priority".to_string(), 10);
    let task_mid = scheduler.submit_task("Mid priority".to_string(), 5);

    // Register two workers with a single-task capacity.
    let worker1 = scheduler.register_worker(1);
    let worker2 = scheduler.register_worker(1);

    // Invoke assignment. Highest priority tasks should be scheduled first.
    let assignments = scheduler.assign_tasks();
    let assigned_tasks: HashSet<_> = assignments.iter().map(|(_, task_id)| task_id.clone()).collect();

    // Verify that the highest priority task gets assigned.
    assert!(assigned_tasks.contains(&task_high));
    // At least one of the remaining tasks should be assigned.
    assert!(assigned_tasks.contains(&task_mid) || assigned_tasks.contains(&task_low));
    
    // Check that assigned tasks are marked as Running.
    for (_, task_id) in assignments {
        assert_eq!(scheduler.query_task_status(&task_id), Some(TaskStatus::Running));
    }
}

#[test]
fn test_worker_failure_reassigns_tasks() {
    let mut scheduler = Scheduler::new();
    let task1 = scheduler.submit_task("Task for failure test".to_string(), 8);
    
    // Register a worker with capacity 1 and assign tasks.
    let worker = scheduler.register_worker(1);
    let assignments = scheduler.assign_tasks();
    let assigned = assignments.into_iter().find(|(_, tid)| *tid == task1);
    assert!(assigned.is_some(), "Task should have been assigned to a worker");
    
    // Simulate worker failure.
    scheduler.simulate_worker_failure(&worker);
    
    // After worker failure the task should be re-queued (i.e. set to Pending).
    assert_eq!(scheduler.query_task_status(&task1), Some(TaskStatus::Pending));
}

#[test]
fn test_task_completion_reporting() {
    let mut scheduler = Scheduler::new();
    let task_success = scheduler.submit_task("Successful Task".to_string(), 6);
    let task_failure = scheduler.submit_task("Failing Task".to_string(), 6);
    
    // Register a worker that can handle two concurrent tasks.
    let worker = scheduler.register_worker(2);
    let assignments = scheduler.assign_tasks();
    
    // Report completion of tasks based on simulated outcome.
    for (w, task) in assignments {
        if task == task_success {
            scheduler.report_task_completion(&w, &task, true);
            assert_eq!(scheduler.query_task_status(&task_success), Some(TaskStatus::Completed));
        } else if task == task_failure {
            scheduler.report_task_completion(&w, &task, false);
            assert_eq!(scheduler.query_task_status(&task_failure), Some(TaskStatus::Failed));
        }
    }
}

#[test]
fn test_dynamic_worker_registration_and_task_assignment() {
    let mut scheduler = Scheduler::new();
    // Submit tasks prior to any worker registration.
    let tasks: Vec<_> = (0..5)
        .map(|i| scheduler.submit_task(format!("Task {}", i), i))
        .collect();
    
    // With no registered workers, assignment should yield no tasks.
    let assignments = scheduler.assign_tasks();
    assert!(assignments.is_empty());

    // Register a worker with capacity 2.
    let _worker = scheduler.register_worker(2);
    let assignments = scheduler.assign_tasks();
    
    // Verify that no more than 2 tasks are assigned at once.
    assert!(assignments.len() <= 2);
    for (_, task_id) in assignments {
        assert_eq!(scheduler.query_task_status(&task_id), Some(TaskStatus::Running));
    }
}

#[test]
fn test_reassignment_after_multiple_worker_failure() {
    let mut scheduler = Scheduler::new();
    // Submit several tasks.
    let tasks: Vec<_> = (0..3)
        .map(|i| scheduler.submit_task(format!("Task {}", i), 5))
        .collect();
    
    // Register two workers with a capacity of 1 each.
    let worker1 = scheduler.register_worker(1);
    let worker2 = scheduler.register_worker(1);
    
    // Assign tasks.
    let assignments = scheduler.assign_tasks();
    assert_eq!(assignments.len(), 2);

    // Simulate failure of one worker and verify reassignment.
    scheduler.simulate_worker_failure(&worker1);
    for (w, task_id) in assignments.iter() {
        if *w == worker1 {
            assert_eq!(scheduler.query_task_status(task_id), Some(TaskStatus::Pending));
        } else {
            assert_eq!(scheduler.query_task_status(task_id), Some(TaskStatus::Running));
        }
    }
    
    // Register a new worker to handle re-queued tasks.
    let _worker3 = scheduler.register_worker(1);
    let new_assignments = scheduler.assign_tasks();
    let mut reassigned = false;
    for (_, task_id) in new_assignments {
        if tasks.contains(&task_id) && scheduler.query_task_status(&task_id) == Some(TaskStatus::Running) {
            reassigned = true;
        }
    }
    assert!(reassigned, "Requeued task was not reassigned after worker failure");
}