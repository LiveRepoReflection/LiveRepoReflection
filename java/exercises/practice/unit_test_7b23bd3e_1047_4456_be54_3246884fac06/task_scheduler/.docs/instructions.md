## Question: Optimal Task Scheduling with Dependencies and Deadlines

### Question Description

You are given a set of `n` tasks to be scheduled on a single processor. Each task `i` has the following properties:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= n).
*   `duration_i`: The amount of time (in milliseconds) required to complete the task.
*   `deadline_i`: The time (in milliseconds from the start of the scheduling) by which the task must be completed to avoid a penalty.
*   `dependencies_i`: A list of task IDs that must be completed before task `i` can start.

Your goal is to design an optimal schedule for these tasks that minimizes the total penalty incurred due to missed deadlines. A task that is completed after its deadline incurs a penalty equal to the amount of time (in milliseconds) by which it exceeds the deadline. Tasks completed before or at the deadline incur no penalty.

**Constraints:**

1.  **Dependencies:** All dependencies of a task must be completed before the task can start. If a schedule violates dependency constraints, it is considered invalid and incurs an infinite penalty.
2.  **Single Processor:** Only one task can be executed at any given time.
3.  **Non-preemption:** Once a task starts, it must be completed without interruption.
4.  **Valid Task IDs:** Task IDs in the `dependencies_i` list are guaranteed to be valid and within the range [1, n].
5.  **No Circular Dependencies:** The task dependency graph will never contain cycles.
6.  **Task Count:** The number of tasks `n` can be up to 1000.

**Input:**

A list of tasks, where each task is represented as a tuple: `(id_i, duration_i, deadline_i, dependencies_i)`.

**Output:**

The minimum total penalty incurred by any valid schedule. If no valid schedule can be found (i.e., dependencies cannot be satisfied), return `Integer.MAX_VALUE`.

**Optimization Requirements:**

Your solution must be efficient enough to handle the maximum task count (`n = 1000`) within a reasonable time limit (e.g., a few seconds).  Brute-force approaches exploring all possible permutations of tasks are unlikely to be efficient enough.

**Edge Cases:**

*   Empty task list.
*   Tasks with no dependencies.
*   Tasks with a large number of dependencies.
*   Tasks with very short or very long durations.
*   Deadlines that are very close to or far from the task durations.
*   Cases where all tasks cannot be completed before their deadlines.
*   Cases where the optimal schedule still results in a non-zero penalty.
*   Tasks with zero duration (should still respect dependencies).

**Example:**

```
Tasks:
(1, 10, 20, [])
(2, 15, 30, [1])
(3, 5, 40, [2])

Optimal Schedule: 1 -> 2 -> 3

Penalty for Task 1: 0 (Completion Time: 10, Deadline: 20)
Penalty for Task 2: 0 (Completion Time: 25, Deadline: 30)
Penalty for Task 3: 0 (Completion Time: 30, Deadline: 40)

Total Penalty: 0
```

This problem challenges you to combine graph traversal, topological sorting, and optimization techniques to find the best possible task schedule. Consider exploring algorithms like dynamic programming or branch and bound to efficiently navigate the solution space.
