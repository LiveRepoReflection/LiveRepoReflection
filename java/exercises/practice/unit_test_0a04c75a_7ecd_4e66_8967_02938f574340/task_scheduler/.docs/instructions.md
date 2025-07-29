## Question: Distributed Task Scheduler with Dependency Resolution

### Problem Description

You are tasked with designing and implementing a distributed task scheduler for a system where tasks have dependencies on each other.  The system consists of multiple worker nodes that can execute tasks in parallel.  Your scheduler must efficiently assign tasks to available workers, respecting task dependencies and minimizing overall execution time.

Each task is represented by a unique integer ID and has the following properties:

*   **Dependencies:** A list of task IDs that must be completed before this task can start.
*   **Estimated Execution Time:** An estimate of how long the task will take to execute (in milliseconds). This is *just* an estimate. Actual execution time may vary, and may even be zero.
*   **Resource Requirements:** A set of resources (e.g., memory, CPU cores, specific software licenses) that the task requires to execute.  Resources are represented as strings.
*   **Priority:** An integer representing the task's priority. Higher values indicate higher priority.

The system has a pool of worker nodes. Each worker node has the following properties:

*   **Available Resources:** A set of resources that the worker node can provide.
*   **Current Task:** The task ID of the task currently being executed (or -1 if idle).

Your scheduler must implement the following functionalities:

1.  **Add Task:** Add a new task to the scheduler with its properties.
2.  **Remove Task:** Removes a task from the scheduler with its ID. If the task is running, the behaviour is undefined.
3.  **Add Worker:** Add a new worker node to the system with its available resources.
4.  **Remove Worker:** Removes a worker node from the system with its ID. If the worker is running a task, the behaviour is undefined.
5.  **Assign Tasks:**  The core functionality. The scheduler should iterate through available tasks and assign them to suitable worker nodes. A task can only be assigned if:
    *   All its dependencies are completed.
    *   A worker node is available (idle) and has all the required resources.
    *   No other tasks of *equal or higher* priority can be assigned to the available node.
    *   If multiple workers can execute a task, assign it to the worker with the *least* available resources (to maximize resource utilization).
6.  **Mark Task Completed:** Marks a task as completed. This will potentially unblock other tasks that depend on it.
7.  **Get Worker Task Assignments:** Returns a map of worker ID to task ID representing the current task assignments.
8. **Get Task Status:** Returns the task status, which can be 'Ready', 'Running', 'Completed', or 'Blocked'. 'Ready' signifies the task is ready to be assigned. 'Running' signifies the task is currently assigned to a worker. 'Completed' signifies the task has been completed. 'Blocked' signifies the task is blocked by dependencies.

### Constraints and Requirements

*   **Scalability:** The system should be able to handle a large number of tasks and worker nodes (e.g., thousands).
*   **Efficiency:** The `Assign Tasks` operation should be as efficient as possible. Consider using appropriate data structures and algorithms to minimize the time complexity.
*   **Dependency Resolution:** The scheduler must correctly resolve task dependencies and ensure that tasks are executed in the correct order.
*   **Resource Management:** The scheduler must correctly manage resources and ensure that tasks are only assigned to worker nodes that have the required resources.
*   **Priority:** The scheduler should prioritize tasks based on their priority value.
*   **Concurrency:** The scheduler may be accessed concurrently by multiple threads. Ensure thread safety.
*   **Error Handling:** Handle edge cases and potential errors gracefully (e.g., invalid task IDs, missing resources).

### Input and Output

The input will be a series of operations on the scheduler, as described above. The output will be the results of the `Get Worker Task Assignments` and `Get Task Status` operations.  The specific format of the input and output is left to the solver to define.

### Example

Imagine a system with three tasks (1, 2, 3) and two workers (A, B).

*   Task 1: No dependencies, Estimated Execution Time: 100ms, Resources: {"CPU"}, Priority: 1
*   Task 2: Dependency: [1], Estimated Execution Time: 200ms, Resources: {"Memory"}, Priority: 2
*   Task 3: Dependency: [1, 2], Estimated Execution Time: 150ms, Resources: {"CPU", "Memory"}, Priority: 1
*   Worker A: Available Resources: {"CPU"}
*   Worker B: Available Resources: {"Memory"}

The scheduler might initially assign Task 1 to Worker A and Task 2 to Worker B. Once Task 1 completes, Task 3 could be assigned to either worker if they both have the resources and are idle.

### Optimization Considerations

*   **Task Scheduling Algorithm:** Explore different task scheduling algorithms (e.g., First-Come, First-Served, Priority Scheduling, Shortest Job First) and choose the one that best suits the requirements.
*   **Data Structures:** Use appropriate data structures (e.g., priority queues, hash maps, sets) to efficiently store and retrieve task and worker information.
*   **Concurrency Control:** Implement appropriate concurrency control mechanisms (e.g., locks, semaphores) to ensure thread safety without introducing excessive overhead.

### Judging Criteria

The solution will be judged based on the following criteria:

*   **Correctness:** Does the solution correctly resolve task dependencies and assign tasks to worker nodes according to the problem requirements?
*   **Efficiency:** Is the solution efficient in terms of time and space complexity? Does it scale well to a large number of tasks and worker nodes?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Concurrency:** Is the solution thread-safe and does it handle concurrent access correctly?
*   **Error Handling:** Does the solution handle edge cases and potential errors gracefully?
