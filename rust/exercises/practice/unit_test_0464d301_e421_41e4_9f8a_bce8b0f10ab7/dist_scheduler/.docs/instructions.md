## Question: Optimized Task Scheduling on a Distributed System

**Project Name:** `distributed-scheduler`

**Question Description:**

You are designing a task scheduler for a distributed system with a large number of independent tasks that need to be executed across a cluster of machines.  The system comprises `N` worker nodes, each with varying computational capabilities and network bandwidth. Your goal is to design an efficient scheduler that minimizes the overall completion time (makespan) of all tasks, while considering both computational load and data transfer overhead.

**Input:**

*   `N`: The number of worker nodes (1 <= N <= 1000). Each worker node is represented by an index from `0` to `N-1`.
*   `worker_capacities`: A vector of `N` integers, where `worker_capacities[i]` represents the computational capacity of worker node `i`. Higher values indicate greater capacity. The capacities are in arbitrary units, but their relative values are meaningful. (1 <= `worker_capacities[i]` <= 1000)
*   `task_loads`: A vector of `M` integers, where `task_loads[j]` represents the computational load of task `j`. These loads are in the same arbitrary units as the worker capacities. (1 <= `M` <= 10000, 1 <= `task_loads[j]` <= 100)
*   `data_dependencies`: A vector of tuples `(task_a, task_b, data_size)`. This vector specifies data dependencies between tasks. The tuple `(task_a, task_b, data_size)` means that task `task_b` requires `data_size` units of data from task `task_a` upon completion.  Task indices are 0-indexed. (0 <= `task_a`, `task_b` < M, 1 <= `data_size` <= 100, no cyclic dependencies)
*   `network_bandwidth`: A matrix of `N x N` integers representing the network bandwidth between worker nodes. `network_bandwidth[i][j]` represents the bandwidth between worker node `i` and worker node `j`.  Assume bandwidth is symmetric: `network_bandwidth[i][j] == network_bandwidth[j][i]`. Higher values indicate greater bandwidth. (1 <= `network_bandwidth[i][j]` <= 1000)

**Constraints and Edge Cases:**

*   Tasks are independent unless a data dependency is explicitly defined in `data_dependencies`.
*   A task can only be executed on one worker node.
*   Data transfer between worker nodes occurs only when a data dependency exists and the dependent tasks are assigned to different worker nodes. Data transfer can occur concurrently with task execution.
*   The scheduler must be non-preemptive; once a task is assigned to a worker node, it cannot be moved to another node mid-execution.
*   The goal is to minimize the makespan - the time when all tasks are completed.
*   Consider the case where some worker nodes might be significantly slower or have limited network bandwidth.  The scheduler should adapt to these heterogeneities.
*   Handle the case where the number of tasks significantly exceeds the number of worker nodes.
*   The number of tasks may be less than or equal to number of worker nodes.
*   The input data dependencies graph must be a directed acyclic graph (DAG).

**Output:**

A vector of `M` integers, where the `i`-th integer represents the worker node (index from 0 to `N-1`) to which task `i` is assigned.

**Optimization Requirements:**

The solution must be computationally efficient. A naive solution will likely time out. Consider using heuristics, approximation algorithms, or intelligent search techniques to find a near-optimal solution within a reasonable time frame.

**Grading:**

The solution will be graded based on the makespan achieved for a set of hidden test cases. Test cases will vary in size (N, M), worker capacities, task loads, data dependencies, and network bandwidth characteristics.  Solutions will be compared against an optimal solution to determine a score.  Solutions which do not complete within a reasonable time limit or crash will receive a zero score.

Good luck!
