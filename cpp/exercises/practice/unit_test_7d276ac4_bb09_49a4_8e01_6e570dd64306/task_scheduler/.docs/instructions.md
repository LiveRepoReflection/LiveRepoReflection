## Question: Optimal Task Scheduling with Deadlines and Dependencies

**Problem Description:**

You are given a set of `N` tasks. Each task `i` has the following attributes:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= N).
*   `duration_i`: An integer representing the time required to complete the task.
*   `deadline_i`: An integer representing the deadline by which the task must be completed.
*   `dependencies_i`: A list of integer task IDs that must be completed before task `i` can start.

Your goal is to determine a schedule for executing these tasks that maximizes the number of tasks completed by their deadlines. A schedule is a permutation of the tasks, representing the order in which they are executed.

**Constraints:**

1.  **Dependencies:** A task can only be started after all its dependencies have been completed.
2.  **Non-preemption:** Once a task is started, it must be completed without interruption.
3.  **Single Processor:** All tasks are executed on a single processor. Only one task can be executed at a time.
4.  **Optimization:** Maximize the number of tasks completed by their deadlines. If multiple schedules achieve the same maximum number of on-time tasks, minimize the total tardiness (sum of `max(0, completion_time - deadline_i)` for all tasks).

**Input:**

The input will be provided as follows:

*   `N`: The number of tasks (1 <= `N` <= 300).
*   A list of `N` tuples, where each tuple represents a task with the format: `(id_i, duration_i, deadline_i, dependencies_i)`. The `dependencies_i` is a list of `id_i` referring to the tasks that must be completed before the task i.

*   All `id_i` are unique and in the range \[1, N].
*   `duration_i` and `deadline_i` are positive integers (1 <= `duration_i`, `deadline_i` <= 1000).
*   The dependencies are guaranteed to be acyclic (no circular dependencies).

**Output:**

Return a list of integers representing the optimal task schedule (i.e., the order in which the tasks should be executed). The list should contain the `id_i` of the tasks in the execution order.

**Example:**

```
N = 4
tasks = [
    (1, 5, 10, []),
    (2, 3, 8, [1]),
    (3, 6, 15, [1, 2]),
    (4, 4, 12, [])
]

Possible Optimal Schedule: [1, 2, 4, 3]
```

**Scoring:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** The generated schedule must respect task dependencies.
2.  **Optimality:** The schedule must maximize the number of tasks completed by their deadlines.
3.  **Tardiness Tiebreaker:** If multiple schedules achieve the same maximum number of on-time tasks, the schedule with the minimum total tardiness will be preferred.
4.  **Efficiency:** Your solution must be efficient enough to handle the given constraints within a reasonable time limit (e.g., a few seconds).

**Notes:**

*   This is a challenging optimization problem that may require a combination of graph algorithms, dynamic programming, and/or heuristic search techniques.
*   Consider the edge cases carefully, such as when it's impossible to complete all tasks by their deadlines.
*   The input data may be large; ensure your solution is efficient in terms of both time and memory usage.
*   A brute-force approach of trying all possible task permutations will likely be too slow for larger input sizes.
*   Clear and well-documented code is essential for understanding and evaluating your solution.
