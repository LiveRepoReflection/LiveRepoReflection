Okay, here's a challenging Rust programming problem designed to be at the LeetCode "Hard" difficulty level.

**Question: Distributed Task Orchestration**

**Problem Description:**

You are tasked with designing and implementing a simplified distributed task orchestration system. This system will manage and execute tasks across a cluster of worker nodes, optimizing for throughput and fault tolerance.

The system receives a directed acyclic graph (DAG) representing a workflow. Each node in the graph represents a task, and the edges represent dependencies between tasks. A task can only be executed once all its dependencies are complete.

Your system must efficiently schedule and execute these tasks across `N` worker nodes. Each worker node has a limited processing capacity, represented by an integer `C`. Each task has a "cost" representing its resource consumption, also an integer. A worker can only execute a task if its remaining capacity is greater than or equal to the task's cost.

Furthermore, tasks have priorities represented by an integer. Higher integer values signify higher priority. When multiple tasks are ready to execute and workers are available, the system should prioritize executing the tasks with the highest priority first.  If tasks have same priority then pick the task with the smallest cost.

**Input:**

*   `N`: The number of worker nodes (1 <= N <= 100).
*   `C`: The capacity of each worker node (1 <= C <= 1000). All worker nodes have the same capacity.
*   `tasks`: A `Vec<(task_id: usize, cost: usize, priority: usize)>` representing the tasks. `task_id` is a unique identifier for each task, `cost` is the resource consumption of the task, and `priority` is the priority of the task. (1 <= cost <= C, 1 <= priority <= 1000).
*   `dependencies`: A `Vec<(parent_task_id: usize, child_task_id: usize)>` representing the dependencies between tasks. This defines the DAG.
*   `initial_tasks`: A `Vec<usize>` containing the `task_id` of tasks that are ready to run from the start.  Tasks not in this vector must wait for their dependencies to complete before they can become ready to run.

**Output:**

A `Vec<(worker_id: usize, task_id: usize)>` representing the execution schedule. Each tuple indicates that `task_id` was executed on `worker_id`. The `worker_id` ranges from 0 to `N-1`. The schedule should be ordered chronologically based on when the task started execution.

**Constraints and Requirements:**

*   **Correctness:** The output must be a valid execution schedule that respects the task dependencies and worker capacities.  A task cannot start until all its dependencies are complete. A worker cannot execute a task if it doesn't have enough capacity.
*   **Efficiency:** The solution should aim to minimize the overall execution time (makespan) of the workflow.  While an optimal solution is not required, the solution should be reasonably efficient. Consider different scheduling strategies.
*   **Fault Tolerance:** If a worker node fails during execution (hypothetically), the system should be able to reschedule the incomplete task on another available worker node (although you don't need to simulate the failure, your design should consider this).
*   **Scalability:** Your solution should be able to handle workflows with a large number of tasks (up to 10,000) and a reasonable number of dependencies.
*   **Concurrency:** Utilize Rust's concurrency features (e.g., threads, channels, mutexes) to allow workers to execute tasks concurrently.
*   **Deterministic:** The result should be deterministic for a given input.  Avoid relying on random number generators for task scheduling.
*   **Handling Cycles:** You can assume that the input graph will always be a DAG (Directed Acyclic Graph).  You do not need to handle cases where there are cycles.

**Example:**

Let's say:

*   `N = 2` (2 worker nodes)
*   `C = 10` (Capacity of each worker is 10)
*   `tasks = [(1, 5, 2), (2, 3, 1), (3, 4, 3)]` (task_id, cost, priority)
*   `dependencies = [(1, 3), (2, 3)]` (task 3 depends on task 1 and task 2)
*   `initial_tasks = [1, 2]` (Tasks 1 and 2 are initially ready)

A possible output could be:

`[(0, 1), (1, 2), (0, 3)]`

This means:

1.  Worker 0 executes task 1.
2.  Worker 1 executes task 2.
3.  Worker 0 executes task 3 (after task 1 and task 2 are completed).

**Judging Criteria:**

Solutions will be judged based on:

*   **Correctness:** Does the solution produce a valid execution schedule?
*   **Efficiency:** How quickly does the solution complete the workflow?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Concurrency Usage:** Does the solution effectively utilize Rust's concurrency features?
*   **Scalability:** Can the solution handle large workflows?

This problem requires a good understanding of graph algorithms, concurrent programming, and resource management. Good luck!
