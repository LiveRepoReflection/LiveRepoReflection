use resource_scheduler::{schedule_jobs, ResourceType};

#[test]
fn test_basic_scheduling() {
    // Resources: 4 CPU, 8 Memory
    let resources = vec![(ResourceType::CPU, 4), (ResourceType::Memory, 8)];
    // Jobs:
    // Job 1: 1 CPU, 2 Memory, deadline 2 => accepted, remaining: CPU:3, Memory:6
    // Job 2: 2 CPU, 3 Memory, deadline 3 => accepted, remaining: CPU:1, Memory:3
    // Job 3: 2 CPU, 4 Memory, deadline 4 => rejected (not enough CPU)
    let jobs = vec![
        (1, vec![(ResourceType::CPU, 1), (ResourceType::Memory, 2)], 2),
        (2, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 3)], 3),
        (3, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 4)], 4),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![1, 2]);
}

#[test]
fn test_invalid_deadline() {
    // Resources: 10 CPU, 10 Memory.
    let resources = vec![(ResourceType::CPU, 10), (ResourceType::Memory, 10)];
    // Job 1: deadline 0 -> should be rejected.
    // Job 2: deadline 1 -> accepted if resources available.
    let jobs = vec![
        (1, vec![(ResourceType::CPU, 5), (ResourceType::Memory, 5)], 0),
        (2, vec![(ResourceType::CPU, 5), (ResourceType::Memory, 5)], 1),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![2]);
}

#[test]
fn test_insufficient_capacity() {
    // Resources: 4 CPU, 4 Memory.
    let resources = vec![(ResourceType::CPU, 4), (ResourceType::Memory, 4)];
    // Job 1: 3 CPU, 2 Memory, deadline 2 -> accepted (remaining: CPU:1, Memory:2)
    // Job 2: 2 CPU, 2 Memory, deadline 3 -> rejected (only 1 CPU left)
    let jobs = vec![
        (1, vec![(ResourceType::CPU, 3), (ResourceType::Memory, 2)], 2),
        (2, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 2)], 3),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![1]);
}

#[test]
fn test_multiple_resources() {
    // Resources: CPU:4, Memory:16, GPU:2.
    let resources = vec![
        (ResourceType::CPU, 4),
        (ResourceType::Memory, 16),
        (ResourceType::GPU, 2),
    ];
    // Job 1: 2 CPU, 8 Memory, 1 GPU, deadline=2 -> accepted (remaining: CPU:2, Memory:8, GPU:1)
    // Job 2: 2 CPU, 8 Memory, 1 GPU, deadline=2 -> accepted (remaining: CPU:0, Memory:0, GPU:0)
    // Job 3: 1 CPU, 1 Memory, 1 GPU, deadline=3 -> rejected (not enough resources)
    let jobs = vec![
        (1, vec![
            (ResourceType::CPU, 2),
            (ResourceType::Memory, 8),
            (ResourceType::GPU, 1)
        ], 2),
        (2, vec![
            (ResourceType::CPU, 2),
            (ResourceType::Memory, 8),
            (ResourceType::GPU, 1)
        ], 2),
        (3, vec![
            (ResourceType::CPU, 1),
            (ResourceType::Memory, 1),
            (ResourceType::GPU, 1)
        ], 3),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![1, 2]);
}

#[test]
fn test_exact_resource_utilization() {
    // Resources: CPU:5, Memory:10.
    let resources = vec![(ResourceType::CPU, 5), (ResourceType::Memory, 10)];
    // Job 1: 2 CPU, 4 Memory, deadline 3 -> accepted (remaining: CPU:3, Memory:6)
    // Job 2: 3 CPU, 6 Memory, deadline 4 -> accepted (resources exactly match)
    // Job 3: 1 CPU, 1 Memory, deadline 5 -> rejected (no resources available)
    let jobs = vec![
        (1, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 4)], 3),
        (2, vec![(ResourceType::CPU, 3), (ResourceType::Memory, 6)], 4),
        (3, vec![(ResourceType::CPU, 1), (ResourceType::Memory, 1)], 5),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![1, 2]);
}

#[test]
fn test_resource_missing_in_capacities() {
    // Resources: Only CPU and Memory are available.
    let resources = vec![(ResourceType::CPU, 10), (ResourceType::Memory, 10)];
    // Job 1: requires GPU as well, but no GPU is provided so this job must be rejected.
    // Job 2: requires only CPU and Memory, so it will be accepted.
    let jobs = vec![
        (1, vec![
            (ResourceType::CPU, 2), 
            (ResourceType::Memory, 2), 
            (ResourceType::GPU, 1)
        ], 3),
        (2, vec![
            (ResourceType::CPU, 5),
            (ResourceType::Memory, 5)
        ], 4),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![2]);
}

#[test]
fn test_order_impact_on_scheduling() {
    // Resources: CPU: 6, Memory: 12.
    let resources = vec![(ResourceType::CPU, 6), (ResourceType::Memory, 12)];
    // Job order affects scheduling:
    // Job 1: 4 CPU, 8 Memory, deadline 3 -> accepted (remaining: CPU:2, Memory:4)
    // Job 2: 2 CPU, 4 Memory, deadline 2 -> accepted (remaining: CPU:0, Memory:0)
    // Job 3: 2 CPU, 2 Memory, deadline 4 -> rejected (insufficient resources)
    let jobs = vec![
        (1, vec![(ResourceType::CPU, 4), (ResourceType::Memory, 8)], 3),
        (2, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 4)], 2),
        (3, vec![(ResourceType::CPU, 2), (ResourceType::Memory, 2)], 4),
    ];
    let scheduled = schedule_jobs(resources, jobs);
    assert_eq!(scheduled, vec![1, 2]);
}