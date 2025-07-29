## Problem: Distributed Task Scheduler with Prioritization and Dependencies

### Question Description

You are tasked with designing a distributed task scheduler for a system that processes a large number of tasks with varying priorities and dependencies. The system consists of multiple worker nodes that can execute tasks in parallel. Your scheduler must efficiently allocate tasks to workers while respecting task priorities and dependencies, and handling worker failures gracefully.

**Tasks:**

Each task is represented by a unique ID (integer), a priority (integer, where lower values indicate higher priority), a list of dependencies (IDs of other tasks that must be completed before this task can start), and an estimated execution time (integer, in seconds).

**Workers:**

The system has a cluster of worker nodes. Each worker node can execute one task at a time.  Workers can fail unpredictably, causing the currently executing task to be lost and requiring rescheduling.

**Scheduler Requirements:**

1.  **Prioritization:** The scheduler should prioritize tasks with higher priority (lower priority value). If multiple tasks are ready to be executed, the one with the highest priority should be scheduled first.

2.  **Dependency Management:** A task can only be scheduled for execution after all its dependencies have been successfully completed.

3.  **Fault Tolerance:** If a worker node fails during the execution of a task, the scheduler should detect the failure and reschedule the task for execution on another available worker node.

4.  **Scalability:** The scheduler should be designed to handle a large number of tasks and worker nodes efficiently.

5.  **Minimization of Makespan:** The scheduler should attempt to minimize the makespan, which is the total time it takes to complete all tasks.

6.  **Fairness:** The scheduler should ensure that no task is indefinitely delayed (starvation) if there is sufficient resources available.

**Input:**

The input will be provided in the following format:

*   A list of tasks, where each task is represented as a tuple: `(task_id, priority, dependencies, estimated_execution_time)`. The `dependencies` field is a list of integer `task_id` values.
*   The number of worker nodes available in the system.

**Output:**

Your program should output a schedule of tasks, represented as a list of events. Each event is a tuple: `(timestamp, worker_id, event_type, task_id)`.

*   `timestamp`: The time (in seconds) when the event occurred.
*   `worker_id`: The ID of the worker node involved in the event (0-indexed).
*   `event_type`: A string representing the type of event. It can be one of the following:
    *   `"SCHEDULED"`: A task is scheduled to start execution on a worker.
    *   `"COMPLETED"`: A task has completed execution successfully.
    *   `"FAILED"`: A worker node has failed during the execution of a task.
    *   `"RESCHEDULED"`: A task is being rescheduled due to a worker failure.

*   `task_id`: The ID of the task involved in the event.

The events in the output should be sorted by timestamp.

**Constraints:**

*   The number of tasks can be up to 10,000.
*   The number of worker nodes can be up to 100.
*   Task IDs are unique integers.
*   Priorities are non-negative integers.
*   Estimated execution times are positive integers.
*   Dependencies must refer to valid task IDs.
*   Worker failures can occur at any time during task execution. Model the worker failures by having a failure probability for each second of execution. The failure probability is a constant `FAILURE_PROBABILITY` defined in your code.
*   The simulation time should be discrete, incrementing in seconds.

**Scoring:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The schedule must be valid, respecting task dependencies and priorities.
*   **Makespan:** Lower makespan values will result in higher scores.
*   **Efficiency:** The scheduler should efficiently utilize worker nodes.
*   **Fault Tolerance:** The scheduler should handle worker failures gracefully and minimize the impact on the overall execution time.

**Example:**

```python
tasks = [
    (1, 1, [], 5),  # Task 1, priority 1, no dependencies, execution time 5 seconds
    (2, 2, [1], 3), # Task 2, priority 2, depends on Task 1, execution time 3 seconds
    (3, 1, [], 4),  # Task 3, priority 1, no dependencies, execution time 4 seconds
    (4, 3, [2, 3], 2) # Task 4, priority 3, depends on Tasks 2 and 3, execution time 2 seconds
]
num_workers = 2

schedule = your_scheduler_function(tasks, num_workers)

# Example Output (may vary depending on your implementation):
# [
#     (0, 0, "SCHEDULED", 1),
#     (0, 1, "SCHEDULED", 3),
#     (4, 1, "COMPLETED", 3),
#     (5, 0, "COMPLETED", 1),
#     (5, 0, "SCHEDULED", 2),
#     (8, 0, "COMPLETED", 2),
#     (8, 1, "SCHEDULED", 4),
#     (10, 1, "COMPLETED", 4)
# ]
```

**Bonus:**

*   Implement a visualization of the task schedule, showing task execution on worker nodes over time.
*   Allow tasks to have resource requirements (e.g., memory, CPU cores) and incorporate resource allocation into the scheduler.

This problem requires you to design a sophisticated task scheduler that balances prioritization, dependency management, fault tolerance, and efficiency. It challenges your understanding of data structures, algorithms, and system design principles. Good luck!
