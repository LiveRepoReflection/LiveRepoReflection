## Project Name

**NetworkFlowScheduler**

## Question Description

You are tasked with designing a highly efficient task scheduler for a distributed computing network. This network consists of `N` compute nodes, each having limited processing capacity. There are `M` independent tasks that need to be scheduled across these nodes. Each task has a specific processing requirement (CPU cycles, memory, etc.) and a deadline.

The network administrator wants to minimize the overall completion time (makespan) of all tasks, ensuring that no task misses its deadline and that no node exceeds its processing capacity at any point in time.

**Formal Definition:**

*   **Nodes:** The network has `N` nodes, numbered from 1 to `N`. Each node `i` has a processing capacity `C[i]`, representing the maximum amount of processing it can handle at any given moment.
*   **Tasks:** There are `M` tasks, numbered from 1 to `M`. Each task `j` has:
    *   `P[j]`: Processing requirement - the amount of processing units needed to complete the task.
    *   `D[j]`: Deadline - the time by which the task must be completed.
*   **Schedule:** A schedule is an assignment of tasks to nodes and a start time for each task.
*   **Constraints:**
    1.  **Node Capacity:** At any time `t`, the sum of processing requirements `P[j]` of all tasks `j` running on node `i` at time `t` must not exceed `C[i]`.
    2.  **Task Deadline:** Each task `j` must be completed by its deadline `D[j]`.  That is, if task `j` is scheduled to start at time `S[j]`, then `S[j] + P[j] <= D[j]`.
    3.  **Non-preemption:** Once a task starts on a node, it must run to completion without interruption (no task splitting or migration).
    4.  **Single Assignment:** Each task can only be assigned to exactly one node.
*   **Objective:** Find a valid schedule that minimizes the makespan (the maximum completion time of any task). The makespan is defined as `max(S[j] + P[j])` for all tasks `j`, where `S[j]` is the start time of task `j`.

**Input:**

Your function will receive the following inputs:

*   `N`: An integer representing the number of nodes.
*   `M`: An integer representing the number of tasks.
*   `C`: A slice of integers of length `N`, where `C[i]` is the processing capacity of node `i`.
*   `P`: A slice of integers of length `M`, where `P[j]` is the processing requirement of task `j`.
*   `D`: A slice of integers of length `M`, where `D[j]` is the deadline of task `j`.

**Output:**

Your function must return a slice of integers of length `M`. Each element `result[j]` represents the node number (1-indexed) that task `j` is assigned to. If no valid schedule exists, return an empty slice (`[]`). You do **not** need to provide the start times for each task, only the node assignments.

**Constraints:**

*   1 <= N <= 20
*   1 <= M <= 100
*   1 <= C\[i] <= 1000 for all i
*   1 <= P\[j] <= 500 for all j
*   1 <= D\[j] <= 1000 for all j

**Efficiency Requirements:**

*   Your solution must be able to handle the maximum input sizes within a reasonable time limit (e.g., a few seconds). Solutions with exponential time complexity are unlikely to pass all test cases.

**Example:**

```go
N = 2 // 2 nodes
M = 3 // 3 tasks
C = []int{6, 8} // Node capacities
P = []int{3, 4, 2} // Task processing requirements
D = []int{7, 8, 6} // Task deadlines

// Possible valid output:
// []int{1, 2, 1} // Assign task 1 to node 1, task 2 to node 2, task 3 to node 1
// Other valid schedules might exist as well.

```

**Judging Criteria:**

*   **Correctness:** Your solution must produce a valid schedule that satisfies all constraints.
*   **Makespan Minimization:** Among all valid schedules, your solution should aim to minimize the makespan. Solutions with smaller makespans will be preferred.
*   **Time Efficiency:** Your solution must complete within the time limit.
*   **Code Quality:** Your code should be well-structured, readable, and maintainable.

This problem requires a strong understanding of combinatorial optimization techniques, graph algorithms (potentially network flow), and possibly heuristics or approximation algorithms.  There might be multiple valid solutions with different makespans. The goal is to find a *good* solution, not necessarily the absolute optimal one, within the time constraints. Good luck!
