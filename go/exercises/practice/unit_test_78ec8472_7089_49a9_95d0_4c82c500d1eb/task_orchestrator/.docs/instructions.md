## Problem: Distributed Task Orchestration with Fault Tolerance

**Description:**

You are building a distributed task orchestration system. This system comprises multiple worker nodes that execute tasks submitted by a central orchestrator. Each task has dependencies on other tasks, forming a directed acyclic graph (DAG). The orchestrator is responsible for scheduling tasks onto available worker nodes, ensuring dependencies are met, and handling worker failures.

**Specifics:**

1.  **Task Representation:** A task is represented by a unique string identifier. Each task has a list of task identifiers that represent its dependencies (parent tasks). A task can only be started when all of its dependencies have been successfully completed.

2.  **Worker Nodes:** Worker nodes are identified by unique string identifiers. Each worker node can execute one task at a time. Worker nodes can fail at any point during task execution.

3.  **Orchestrator Responsibilities:**
    *   Receives a DAG of tasks with dependencies.
    *   Maintains a pool of available worker nodes.
    *   Schedules tasks onto available workers, ensuring dependencies are met.
    *   Monitors the status of tasks (pending, running, completed, failed).
    *   Handles worker failures:
        *   If a worker fails during task execution, the task is marked as failed.
        *   Failed tasks (due to worker failure) must be automatically re-scheduled onto a different available worker node, respecting task dependencies.
        *   Retries should be limited to a maximum number.
    *   Provides a mechanism to query the status of a task (e.g., "completed", "failed", "pending", "running").
    *   The Orchestrator should complete and return an error if it detects a circular dependency.
    *   The Orchestrator should complete and return an error if a task fails after exhausting the number of retries.

4.  **Task Execution:** You don't need to implement the actual task execution. Instead, simulate it with a function that takes a task identifier as input and returns either success or failure (randomly or based on a predefined probability). The worker node will call this simulation function.

5.  **Constraints:**
    *   The system must be fault-tolerant, able to recover from worker node failures.
    *   Task scheduling should be efficient, minimizing idle time for worker nodes.
    *   The orchestrator must prevent tasks from running concurrently if they depend on each other.
    *   The solution must use Go concurrency primitives (goroutines, channels, mutexes) effectively.

6.  **Input:**
    *   A DAG of tasks represented as a `map[string][]string`, where the key is the task identifier and the value is a list of its dependencies (parent task identifiers).
    *   A list of worker node identifiers.
    *   A task simulation function (as described above).
    *   Maximum number of retries for a task.

7.  **Output:**
    *   A `map[string]string` representing the final status of each task (e.g., "completed", "failed").
    *   An error, if any circular dependencies are found or if a task fails after maximum retries.

**Bonus Challenges:**

*   Implement dynamic scaling of worker nodes (adding/removing workers during execution).
*   Prioritize tasks based on urgency or importance.
*   Implement a graphical user interface (GUI) to visualize the DAG and task execution status.
*   Add logging and monitoring capabilities to the system.
*   Implement a cancellation mechanism to stop the execution of a task.

This problem requires a solid understanding of concurrency, data structures (graphs), and error handling in Go. It also tests the ability to design a fault-tolerant distributed system. The multiple edge cases and the need for efficient scheduling make it a challenging and sophisticated problem.
