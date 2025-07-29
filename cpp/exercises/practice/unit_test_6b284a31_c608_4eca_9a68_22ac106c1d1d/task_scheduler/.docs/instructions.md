## Project Name

```
Distributed Task Scheduler
```

## Question Description

You are tasked with designing and implementing a distributed task scheduler. This scheduler is responsible for receiving task submissions from various clients, managing their dependencies, distributing them across a cluster of worker nodes, and ensuring their execution in the correct order, handling failures gracefully.

**System Architecture:**

The system comprises the following components:

*   **Clients:** Submit tasks to the scheduler. Each task is represented by a unique ID, a command to execute, and a list of task IDs that must be completed before it can start (dependencies).
*   **Scheduler:** The central component responsible for receiving tasks, managing dependencies, assigning tasks to workers, and tracking their execution status.  It should be highly available, possibly by having redundant instances, though you only need to implement the logic for a single scheduler instance for this problem.
*   **Workers:** Execute the tasks assigned to them by the scheduler. Each worker has limited resources (e.g., CPU, memory). The scheduler must consider worker resource limitations when assigning tasks. Workers report back to the scheduler upon completion (success or failure) of a task.
*   **Task Representation:** The Task class must have the following info:
    *   `task_id`: Unique identifier (string).
    *   `command`: Command to execute (string).
    *   `dependencies`: A set of `task_id` strings representing dependencies.
    *   `status`: Task status (enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).
*   **Resource Management:**
    *   Each Worker has a limited number of CPU cores and memory (in MB).
    *   Each Task requires a certain number of CPU cores and memory to run.
    *   The Scheduler must only assign Tasks to Workers that have sufficient resources.

**Requirements:**

1.  **Task Submission:** Clients can submit tasks to the scheduler. The scheduler should validate the task (e.g., check for circular dependencies, non-existent dependencies, resource requirements).

2.  **Dependency Management:** The scheduler must ensure that tasks are executed only after all their dependencies have been successfully completed.

3.  **Task Assignment:** The scheduler must assign tasks to available workers, considering their resource limitations (CPU and memory). If no suitable worker is available, the task should remain in a pending state until a worker becomes available. Assume workers regularly send heartbeats to the scheduler to indicate availability.

4.  **Task Execution:** Workers execute the tasks assigned to them and report the execution status (success or failure) to the scheduler.

5.  **Failure Handling:** If a task fails, the scheduler must:
    *   Retry the task a limited number of times (configurable, e.g., 3 retries).  The worker may have failed, so consider reassigning to a different worker.
    *   If the task fails after all retries, mark the task as failed.
    *   Notify clients about task failures. Tasks dependent on the failed task should also be marked as failed.

6.  **Concurrency:** The scheduler and workers must be designed to handle multiple tasks concurrently.

7.  **Efficiency:** The scheduler should efficiently manage task dependencies and resource allocation to minimize task completion time.  Consider optimizing task assignment for faster completion, preferring workers with more available resources that meet requirements.

8.  **Scalability:** While you don't need to implement a distributed scheduler for this problem, your design should consider how the system could be scaled to handle a large number of tasks and workers. Consider the data structures used and their impact on performance as the task and worker counts grow.

**Constraints:**

*   The number of workers can be up to 100.
*   The number of tasks can be up to 10,000.
*   Task IDs are unique strings.
*   CPU cores for workers: 1-32
*   Memory for workers: 1GB - 64GB
*   CPU cores for tasks: 1-8
*   Memory for tasks: 128MB - 8GB
*   The time limit for execution is strict (similar to LeetCode hard problems).  Inefficient solutions will time out.

**Input:**

*   A list of task definitions. Each task definition includes:
    *   `task_id` (string)
    *   `command` (string)
    *   `dependencies` (a set of task_id strings)
    *   `cpu_cores_required` (int)
    *   `memory_required_mb` (int)
*   A list of worker definitions. Each worker definition includes:
    *   `worker_id` (string, you can assume the scheduler assigns these)
    *   `cpu_cores_available` (int)
    *   `memory_available_mb` (int)

**Output:**

*   A dictionary where the key is the `task_id` and the value is the final `status` of the task (`COMPLETED` or `FAILED`).
*   The scheduler should strive to complete as many tasks as possible, even if some tasks fail.

**Bonus Challenges:**

*   Implement a simple priority mechanism for tasks.
*   Implement a mechanism for workers to dynamically join and leave the cluster.
*   Implement a simple client API to submit tasks and monitor their status.
*   Add a logging mechanism to track task execution and system events.

This problem requires a strong understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
