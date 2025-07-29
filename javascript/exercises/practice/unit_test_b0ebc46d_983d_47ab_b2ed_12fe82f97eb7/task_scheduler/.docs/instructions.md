Okay, here's a challenging Javascript problem description designed to be akin to a LeetCode Hard difficulty question.

## Project Title

**Distributed Task Scheduler with Resource Constraints**

## Question Description

You are tasked with designing and implementing a distributed task scheduler. This scheduler is responsible for accepting tasks, assigning them to available worker nodes in a cluster, and ensuring that tasks are executed subject to resource constraints and dependencies.

The system operates under the following constraints:

*   **Tasks:** Each task is defined as a JavaScript object with the following properties:
    *   `id`: A unique string identifier for the task.
    *   `dependencies`: An array of task IDs that must be completed before this task can start.  A task with an empty `dependencies` array can start immediately if resources are available.
    *   `cpu`: An integer representing the number of CPU cores required by the task.
    *   `memory`: An integer representing the amount of memory (in MB) required by the task.
    *   `duration`: An integer representing the estimated execution time of the task in seconds.

*   **Workers:** The cluster consists of multiple worker nodes. Each worker is represented as a JavaScript object with the following properties:
    *   `id`: A unique string identifier for the worker.
    *   `cpu`: An integer representing the total number of CPU cores available on the worker.
    *   `memory`: An integer representing the total amount of memory (in MB) available on the worker.
    *   `available`: a boolean representing whether the worker is available or not. Worker node becomes unavailable when it is running a task. Worker becomes available when its running task is completed.

*   **Scheduler API:** You need to implement the following functions:
    *   `addTask(task)`: Adds a task to the scheduler's queue.  The task should be validated (e.g., checking if `id` is unique, resource requests are non-negative, etc.).  If validation fails, throw an error.
    *   `addWorker(worker)`: Adds a worker to the cluster.  The worker should be validated (e.g., checking if `id` is unique, resource capacity are non-negative, etc.). If validation fails, throw an error.
    *   `removeWorker(workerId)`: Removes a worker from the cluster.  Any tasks assigned to the removed worker should be requeued and made available for scheduling on other workers.
    *   `getAvailableWorkers()`: Returns an array of worker node IDs that are currently available.
    *   `schedule()`: Attempts to schedule tasks from the queue onto available workers.  The scheduler should follow these rules:
        *   Prioritize tasks based on the number of dependencies they have, scheduling tasks with fewer dependencies first.
        *   A task can only be assigned to a worker if the worker has sufficient CPU cores and memory to satisfy the task's requirements.
        *   A worker can only run one task at a time.
        *   If multiple workers can run a task, choose the worker with the most available resources (CPU + Memory).
        *   If a task cannot be scheduled due to resource constraints, it remains in the queue.
        *   Schedule function should return the number of tasks scheduled in the current schedule() execution.
    *   `getTaskStatus(taskId)`: Returns the current status of a task. Possible status values are: "pending", "running", "completed", "failed".
    *   `runTasks()`: Simulates the execution of the tasks that are currently running on the workers. For simplicity, assume the `duration` of each task is accurate. After the `duration` time is passed, the worker becomes available and the task status will be updated to "completed". The runTasks() function should automatically handle any exceptions during task execution and set the task status to "failed" in such cases. The `runTasks()` should automatically call schedule() method to schedule more tasks if there are available workers.

*   **Optimization Requirements:**
    *   The `schedule()` function should be optimized for performance.  Consider using appropriate data structures to efficiently find suitable workers for tasks. The scheduler should avoid unnecessary iterations and comparisons.
    *   The `addTask()`, `addWorker()`, and `removeWorker()` functions should also maintain reasonable performance.
    *   Implementations should try to maximize cluster utilization.

*   **Edge Cases:**
    *   Handle circular dependencies between tasks (detect and throw an error).
    *   Handle tasks that request more resources than any worker can provide (mark as "failed").
    *   Handle worker failures during task execution (requeue the task).
    *   Handle situations where a task is dependent on a task that has failed (mark as "failed").
    *   Handle scenarios where there are no available workers.
    *   Handle scenarios where all workers are busy, and no tasks can be scheduled.

*   **Real-World Considerations:**
    *   The scheduler should be designed to be resilient to worker failures.
    *   The scheduler should be able to handle a large number of tasks and workers.

*   **System Design Aspects:**
    *   Consider how the scheduler could be extended to support different task types (e.g., CPU-intensive, memory-intensive, I/O-intensive).
    *   Consider how the scheduler could be integrated with a monitoring system to track resource utilization and task progress.
    *   Consider how the scheduler can be extended to support task priorities.

## Input

The input consists of a series of calls to the scheduler API methods (`addTask`, `addWorker`, `removeWorker`, `schedule`, `getTaskStatus`, `runTasks`).

## Output

The output consists of the return values of the scheduler API methods (e.g., the number of scheduled tasks returned by `schedule`, the task status returned by `getTaskStatus`, the array of available workers returned by `getAvailableWorkers`).

This problem requires a solid understanding of data structures, algorithms, and system design principles.  It challenges the solver to consider various edge cases, optimization strategies, and real-world considerations to build a robust and efficient distributed task scheduler.  Good luck!
