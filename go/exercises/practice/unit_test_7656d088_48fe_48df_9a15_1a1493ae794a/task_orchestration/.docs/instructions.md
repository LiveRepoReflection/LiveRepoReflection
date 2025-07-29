## Problem Title: Optimal Task Orchestration in a Distributed System

**Problem Description:**

You are tasked with designing an efficient task orchestration system for a large-scale distributed environment. The system consists of `n` worker nodes and a central orchestrator. A set of `m` independent tasks needs to be executed across these worker nodes. Each task `i` has a specific resource requirement `r_i` (e.g., CPU cores, memory) and a completion time `t_i` that depends on the worker node it is assigned to. The completion time of task `i` on worker node `j` is given by `t_ij`. Each worker node `j` has a limited resource capacity `c_j`. The orchestrator needs to assign tasks to worker nodes such that the following objectives are met:

1.  **Resource Constraint:** The total resource requirement of tasks assigned to any worker node `j` does not exceed its capacity `c_j`.
2.  **Minimize Makespan:** The makespan, defined as the maximum completion time across all worker nodes, should be minimized. In other words, the time when the last worker node finishes its assigned tasks must be as early as possible.
3.  **Fault Tolerance:** The system should be resilient to worker node failures. If a worker node fails during task execution, all tasks assigned to that node must be re-assigned to other available nodes without violating resource constraints and while still attempting to minimize the overall makespan.

**Input:**

*   `n`: Number of worker nodes (integer).
*   `m`: Number of tasks (integer).
*   `c`: An array of length `n` representing the resource capacity `c_j` of each worker node `j`.
*   `r`: An array of length `m` representing the resource requirement `r_i` of each task `i`.
*   `t`: A 2D array of dimensions `m x n` representing the completion time `t_ij` of task `i` on worker node `j`.
*   `failed_node`: An integer representing the index of a worker node that has failed (or -1 if no node has failed initially).

**Output:**

A data structure (e.g., a map/dictionary) representing the optimal task assignment.  The keys of the structure should be worker node indices (0 to n-1), and the values should be lists of task indices (0 to m-1) assigned to that worker node.  If no feasible assignment exists (either initially or after a node failure), return an empty data structure.

**Constraints:**

*   1 <= `n` <= 100
*   1 <= `m` <= 1000
*   1 <= `c_j` <= 1000 for all `j`
*   1 <= `r_i` <= 100 for all `i`
*   1 <= `t_ij` <= 1000 for all `i` and `j`
*   -1 <= `failed_node` < `n`

**Optimization Requirements:**

*   The solution should strive to minimize the makespan.
*   The solution should be efficient in terms of time complexity, especially when re-assigning tasks after a node failure.
*   Consider various task scheduling algorithms (e.g., greedy, simulated annealing, genetic algorithms) and their trade-offs in terms of solution quality and computational cost.

**Edge Cases:**

*   Infeasible initial assignment (tasks requiring more resources than available).
*   Node failure leading to infeasible re-assignment.
*   Large number of tasks and worker nodes.
*   Tasks with vastly different resource requirements and completion times.

**Example:**

```
n = 3
m = 5
c = [10, 12, 8]
r = [3, 4, 2, 5, 1]
t = [
    [5, 7, 9],
    [8, 6, 4],
    [2, 3, 5],
    [6, 8, 7],
    [1, 2, 3]
]
failed_node = -1

// Possible optimal output (this is just an example; other assignments might be equally optimal):
{
    0: [2, 4],  // Tasks 2 and 4 assigned to worker node 0
    1: [1],    // Task 1 assigned to worker node 1
    2: [0, 3]   // Tasks 0 and 3 assigned to worker node 2
}

// In this example, the makespan would be max(2+1, 6, 5+6) = 11
```
```
n = 3
m = 5
c = [10, 12, 8]
r = [3, 4, 2, 5, 1]
t = [
    [5, 7, 9],
    [8, 6, 4],
    [2, 3, 5],
    [6, 8, 7],
    [1, 2, 3]
]
failed_node = 1

//If node 1 fails, task 1 must be re-assigned without exceeding resource limits.
//A possible (but not necessarily only) optimal solution would be
{
    0: [2, 4, 1],  // Tasks 2, 4 and 1 assigned to worker node 0
    1: [],    // Worker node 1 has failed, so no tasks assigned
    2: [0, 3]   // Tasks 0 and 3 assigned to worker node 2
}
```

**Clarifications:**

*   Tasks are indivisible; you cannot split a task across multiple worker nodes.
*   The goal is to minimize the makespan, but within that constraint, any valid assignment is acceptable. There may be multiple valid assignments with the same minimal makespan.
*   Assume that the input is valid and that `failed_node` is within the valid range.
* The failed node is considered completely unavailable for reassignment

This problem challenges you to combine resource allocation, task scheduling, and fault tolerance considerations in a distributed system. The need to minimize the makespan while adhering to resource constraints and adapting to node failures demands a sophisticated algorithmic approach. Good luck!
