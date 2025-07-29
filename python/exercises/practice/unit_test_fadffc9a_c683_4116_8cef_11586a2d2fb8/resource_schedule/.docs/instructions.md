## Project Name

**Optimal Resource Allocation with Dependencies and Deadlines**

## Question Description

You are tasked with optimizing the allocation of computational resources to a set of tasks with dependencies and deadlines. Each task requires a specific amount of a single resource (e.g., CPU cores, memory) and must be completed before its deadline. Tasks also have dependencies; a task cannot start until all its dependent tasks are finished.

Specifically, you are given:

*   `n`: The number of tasks, indexed from 0 to n-1.
*   `resources`: A single integer representing the total available resources.
*   `task_resources`: A list of integers of length `n`, where `task_resources[i]` represents the amount of resources required by task `i`.
*   `task_deadlines`: A list of integers of length `n`, where `task_deadlines[i]` represents the deadline for task `i`.  Deadlines are expressed as integer timestamps (e.g., the number of seconds since the start of the simulation).
*   `dependencies`: A list of lists of integers. `dependencies[i]` is a list of task indices that task `i` depends on.  In other words, all tasks in `dependencies[i]` must be completed before task `i` can start.

A schedule is a list of tuples, where each tuple `(start_time, task_index)` indicates that task `task_index` starts executing at time `start_time`. Each task executes for exactly one unit of time after it starts. A valid schedule must satisfy the following conditions:

1.  **Resource Constraint:** At any given time, the total resources allocated to running tasks must not exceed the total available resources.
2.  **Dependency Constraint:** A task can only start executing if all its dependencies have been completed (i.e., finished executing).
3.  **Deadline Constraint:** Each task must be completed before its deadline (start\_time + 1 <= task\_deadlines[i] where i is the task index).
4.  **Non-preemption:** Once a task starts, it runs to completion without interruption. A task executes for one unit of time.
5.  **No Overlap:** No task can start before the system is ready to execute it.

Your goal is to find a valid schedule that maximizes the number of tasks completed. If multiple schedules achieve the same maximum number of completed tasks, return the schedule that minimizes the makespan (the time when the last task finishes). If no valid schedule exists, return an empty list.

**Constraints:**

*   1 <= n <= 1000
*   1 <= resources <= 1000
*   1 <= task\_resources\[i] <= resources for all i
*   1 <= task\_deadlines\[i] <= 10000 for all i
*   0 <= len(dependencies\[i]) <= n for all i
*   The dependency graph is a Directed Acyclic Graph (DAG).
*   The evaluation of the answer will consider both the number of completed tasks and the makespan. A solution with a larger number of completed tasks is always better. If the number of completed tasks is the same, a solution with a smaller makespan is better.

**Optimization Requirements:**

*   The solution must be efficient enough to handle reasonably sized input within a time limit (e.g., 1-2 seconds).  Consider using appropriate data structures and algorithms for graph traversal, scheduling, and resource management.
*   The chosen data structures and algorithms should be robust to all possible valid input cases.

**Example:**

```python
n = 4
resources = 10
task_resources = [3, 6, 4, 2]
task_deadlines = [4, 6, 5, 7]
dependencies = [[], [0, 2], [0], []]

# One possible optimal schedule:
# [(0, 0), (1, 2), (2, 3), (3, 1)]
# This completes all 4 tasks with a makespan of 4.
# The task 0 starts at time 0, task 2 starts at time 1, task 3 starts at time 2, task 1 starts at time 3.

```
