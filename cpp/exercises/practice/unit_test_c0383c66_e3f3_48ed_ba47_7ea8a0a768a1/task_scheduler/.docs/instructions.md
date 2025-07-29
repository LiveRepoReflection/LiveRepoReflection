## Problem: Optimal Task Assignment with Dependencies and Deadlines

**Description:**

You are tasked with optimizing the execution of a set of tasks in a complex project. Each task has a specific duration, a deadline, a potential profit associated with completing it on time, and dependencies on other tasks. The project has a limited number of worker threads available for parallel execution. Your goal is to determine the optimal schedule to maximize the total profit while respecting dependencies, deadlines, and thread limitations.

**Formal Definition:**

Given:

*   `N`: The number of tasks in the project.
*   `M`: The number of available worker threads.
*   `tasks`: A list of `N` tasks, where each task `i` has the following attributes:
    *   `id_i`: A unique identifier for the task (0 to N-1).
    *   `duration_i`: The time (in arbitrary units) required to complete the task.
    *   `deadline_i`: The time (in arbitrary units) by which the task must be completed to earn its profit.
    *   `profit_i`: The profit earned if the task is completed by its deadline. If a task is not completed by its deadline, no profit is earned (profit = 0).
    *   `dependencies_i`: A list of `id`s representing the tasks that must be completed before task `i` can start.  Dependencies are guaranteed to be acyclic.

Your function must return the maximum total profit that can be obtained by scheduling the tasks, respecting the following constraints:

1.  **Dependencies:** A task can only start executing after all its dependencies have been completed.
2.  **Deadlines:** A task must be completed before its deadline to earn its profit.
3.  **Thread Limit:** At any given time, the number of tasks executing concurrently cannot exceed `M`.
4.  **Non-preemption:** Once a task starts executing, it must run to completion without interruption.

**Input:**

Your function will receive the following inputs:

*   `N`: An integer representing the number of tasks.
*   `M`: An integer representing the number of worker threads.
*   `tasks`: A vector of structs/objects, each representing a task.  The structure for a task should contain the `id`, `duration`, `deadline`, `profit`, and `dependencies` as described above.

**Output:**

Your function should return a single integer: the maximum total profit achievable by scheduling the tasks optimally.

**Constraints:**

*   1 <= N <= 1000
*   1 <= M <= 100
*   1 <= duration\_i <= 100
*   1 <= deadline\_i <= 1000
*   0 <= profit\_i <= 1000
*   Dependencies are acyclic.
*   All task `id`s will be valid (0 to N-1).

**Example:**

```
N = 3
M = 2
tasks = [
  {id: 0, duration: 5, deadline: 10, profit: 100, dependencies: []},
  {id: 1, duration: 3, deadline: 8, profit: 50, dependencies: [0]},
  {id: 2, duration: 2, deadline: 12, profit: 75, dependencies: [0, 1]}
]

Optimal Schedule (one possible):
1. Task 0 starts at time 0, finishes at time 5 (profit = 100).
2. Task 1 starts at time 5, finishes at time 8 (profit = 50).
3. Task 2 starts at time 8, finishes at time 10 (profit = 75).

Maximum Profit = 100 + 50 + 75 = 225

```

**Challenge:**

The key challenge lies in efficiently exploring the vast search space of possible task schedules.  A naive brute-force approach will quickly become infeasible as `N` increases.  Consider using dynamic programming, branch and bound, or other optimization techniques to prune the search space and find the optimal solution within the given constraints.  Furthermore, efficient data structures for managing task dependencies and available threads will be crucial for achieving a good time complexity. Carefully handle edge cases where tasks are impossible to complete within their deadlines due to dependencies or thread limitations.  The aim is to design an algorithm that can handle a large number of tasks and dependencies within a reasonable time frame.
