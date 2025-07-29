## Question: Asynchronous Task Orchestration with Dependency Resolution

### Question Description

You are tasked with designing and implementing an asynchronous task orchestration system.  This system manages a set of independent tasks with inter-dependencies. Each task performs a specific operation and may depend on the successful completion of other tasks before it can begin execution. The system must efficiently schedule and execute these tasks, considering the dependencies and resource constraints.

Specifically, you will be given:

1.  **A list of tasks**: Each task is represented by a unique ID (string), an estimated execution time (integer, representing arbitrary time units), and a list of task IDs it depends on (list of strings).
2.  **A limited number of worker threads**: The system can only execute a certain number of tasks concurrently.
3.  **Resource constraints**: Each task requires a specific amount of resources (e.g., memory, CPU, network bandwidth) to execute. The system has a total resource capacity.

Your system should:

*   **Parse the task definitions and build a dependency graph.** The graph should accurately represent the dependencies between tasks.
*   **Schedule tasks for execution based on dependency resolution and resource availability.**  A task can only be scheduled when all its dependencies are met, and sufficient resources are available.
*   **Simulate task execution using threads.** Each worker thread represents a resource that can execute one task at a time.  Simulate the execution time of each task using `time.sleep()` or similar mechanism (representing CPU time).
*   **Handle task failures gracefully.** If a task fails (simulated by randomly raising an exception during task execution), all tasks that depend on it should be cancelled, and the system should report the failure.
*   **Optimize task execution time.** The system should aim to minimize the overall time required to complete all tasks while respecting dependencies and resource constraints.  This might involve prioritizing tasks on the critical path.
*   **Provide a mechanism to track the progress of tasks.** The system should provide a clear indication of which tasks are pending, running, completed successfully, or failed.
*   **Avoid deadlocks.** The system must ensure that tasks do not enter a deadlock situation where they are indefinitely waiting for each other.

**Input:**

*   `tasks`: A list of dictionaries. Each dictionary represents a task and has the following keys:
    *   `id`: A string representing the unique task ID.
    *   `execution_time`: An integer representing the estimated execution time of the task.
    *   `dependencies`: A list of strings representing the task IDs that this task depends on.
    *   `resources_required`: An integer representing the resources required by the task.
*   `num_workers`: An integer representing the number of worker threads available.
*   `total_resources`: An integer representing the total resource capacity of the system.
*   `failure_rate`: A float between 0 and 1 representing the probability of a task failing during execution (simulate failure randomly).

**Output:**

*   A dictionary containing the following keys:
    *   `status`: "success" if all tasks completed successfully, "failure" if any task failed.
    *   `completion_time`: The total time taken to complete all tasks.
    *   `task_states`: A dictionary mapping task IDs to their final state ("pending", "running", "completed", "failed", "cancelled").

**Constraints:**

*   The number of tasks can be large (e.g., up to 1000).
*   The dependencies can form a complex directed acyclic graph (DAG). You are guaranteed it will be a DAG.
*   The execution time of tasks can vary significantly.
*   The resource requirements of tasks can vary.
*   The system must be robust and handle errors gracefully.
*   The solution must be efficient and avoid unnecessary delays.

**Hints:**

*   Use appropriate data structures to represent the dependency graph (e.g., adjacency list).
*   Use threading or asyncio to implement asynchronous task execution.
*   Implement a task scheduler that prioritizes tasks based on dependency resolution and resource availability.
*   Use locks or semaphores to manage access to shared resources (e.g., worker threads, resource capacity).
*   Implement a mechanism to detect and handle task failures.
*   Consider using topological sorting to optimize task scheduling.
*   Consider using a priority queue to prioritize tasks on the critical path.

This problem requires a solid understanding of data structures, algorithms, concurrency, and system design principles. A well-designed and implemented solution will be able to efficiently manage and execute a large number of tasks with complex dependencies and resource constraints. Good luck!
