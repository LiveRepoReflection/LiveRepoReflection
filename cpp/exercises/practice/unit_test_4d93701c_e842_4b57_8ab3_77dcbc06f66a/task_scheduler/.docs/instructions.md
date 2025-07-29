## Project Name

```
Distributed Task Scheduler with Dependencies
```

## Question Description

You are tasked with designing and implementing a distributed task scheduler that can handle complex task dependencies. The scheduler must efficiently manage a large number of tasks, each potentially dependent on the completion of other tasks.

**Scenario:**

Imagine a scientific simulation workflow. The workflow consists of numerous individual computations (tasks), some of which can be executed in parallel, while others require the results of previous tasks. For instance, task 'B' might depend on the output of task 'A', meaning 'B' cannot start until 'A' is finished.  These tasks are to be distributed across a cluster of worker nodes.

**Requirements:**

1.  **Task Definition:** A task is defined by a unique ID (string), a processing time (integer, representing the number of seconds it takes to complete), and a list of dependencies (a list of task IDs that must be completed before this task can start).

2.  **Dependency Resolution:** The scheduler must correctly resolve task dependencies to ensure tasks are executed in the correct order. Circular dependencies should be detected and reported as an error.

3.  **Distributed Execution:** The scheduler should simulate the distribution of tasks to a fixed number of worker nodes. Each worker node can execute only one task at a time.

4.  **Resource Constraints:** Each worker node has a limited amount of memory. Tasks also require a certain amount of memory to run. The scheduler must ensure that a worker node doesn't exceed its memory capacity when assigning tasks. If no worker has sufficient capacity, the task will remain pending.

5.  **Task Prioritization:** Tasks can have priorities (integer, higher value means higher priority). When multiple tasks are ready to be executed, the scheduler should prioritize tasks with higher priority.

6.  **Fault Tolerance:** If a worker node fails during task execution, the scheduler should automatically re-schedule the failed task (and any tasks dependent on it) to another available worker node. Assume a task can be retried a maximum of 3 times.

7.  **Optimization:** The scheduler should aim to minimize the overall completion time of the entire workflow (makespan).

**Input:**

*   `num_workers`: The number of worker nodes in the cluster (integer).
*   `worker_memory`: The memory capacity of each worker node (integer).
*   `tasks`: A list of task definitions. Each task is a dictionary/object with the following keys:
    *   `task_id`: A unique identifier for the task (string).
    *   `processing_time`: The time required to execute the task (integer, seconds).
    *   `memory_required`: The amount of memory the task requires to run (integer).
    *   `dependencies`: A list of task IDs that must be completed before this task can start (list of strings).
    *   `priority`: The priority of the task (integer).

**Output:**

A dictionary/object containing the following information:

*   `schedule`: A list of events, sorted by time. Each event is a dictionary/object with the following keys:
    *   `time`: The time (integer, seconds) at which the event occurred.
    *   `worker_id`: The ID of the worker node involved (integer, starting from 0).
    *   `task_id`: The ID of the task involved (string).
    *   `event_type`: One of "START", "END", or "FAILED".

*   `makespan`: The total time (integer, seconds) taken to complete all tasks.

*   `circular_dependency`: `True` if a circular dependency was detected, `False` otherwise.

*   `unfulfillable_dependencies`: A list of task IDs that could not be executed due to unfulfillable dependencies (e.g., a dependency task never completes).

*   `tasks_not_executed`: A list of task IDs that could not be executed due to resource constraints (insufficient memory).

**Constraints:**

*   The number of tasks can be very large (up to 10,000).
*   The number of worker nodes is relatively small (up to 10).
*   Processing times can vary significantly (from 1 second to 1000 seconds).
*   Memory requirements can also vary significantly.
*   The scheduler must be efficient and avoid unnecessary delays in task execution.
*   The solution must be thread-safe.

**Example:**

```
num_workers = 2
worker_memory = 100
tasks = [
    {"task_id": "A", "processing_time": 10, "memory_required": 50, "dependencies": [], "priority": 1},
    {"task_id": "B", "processing_time": 5, "memory_required": 30, "dependencies": ["A"], "priority": 2},
    {"task_id": "C", "processing_time": 15, "memory_required": 70, "dependencies": ["A"], "priority": 1},
    {"task_id": "D", "processing_time": 8, "memory_required": 40, "dependencies": ["B", "C"], "priority": 3},
]
```

The output `schedule` would show which tasks are started and ended at what time and on which worker. The output `makespan` would be the total time when the last task is finished. The other outputs would be `False` or empty lists, as there are no circular dependencies, unfulfillable dependencies, or tasks that cannot be executed due to resource constraints in this example.

**Judging Criteria:**

*   Correctness: The scheduler must correctly resolve dependencies and produce a valid schedule.
*   Efficiency: The scheduler should minimize the makespan.
*   Scalability: The scheduler should be able to handle a large number of tasks.
*   Fault Tolerance: The scheduler should correctly handle worker node failures.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem is designed to test your understanding of distributed systems, task scheduling algorithms, data structures, and optimization techniques. Good luck!
