## Question: Optimal Task Assignment with Dependencies and Deadlines

**Question Description:**

You are managing a complex project consisting of `N` tasks. Each task `i` has the following properties:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= N).
*   `duration_i`: The time (in arbitrary units) required to complete the task.
*   `deadline_i`: The latest time by which the task must be completed.
*   `dependencies_i`: A list of `id`s of tasks that must be completed *before* task `i` can begin.

Your goal is to determine the optimal order in which to execute these tasks to *minimize the maximum lateness* of any task. The *lateness* of a task is defined as `completion_time - deadline` if the completion time is later than the deadline, and 0 otherwise.  Formally, `lateness_i = max(0, completion_time_i - deadline_i)`.

The maximum lateness of the schedule is the maximum lateness of any single task in that schedule.

You have a single processor, so only one task can be executed at any given time. You can start a task only if all its dependencies have been completed.

**Input:**

A list of `N` tasks, where each task is represented as a tuple: `(id, duration, deadline, dependencies)`.

**Constraints:**

*   `1 <= N <= 1000`
*   `1 <= duration_i <= 100`
*   `1 <= deadline_i <= 10000`
*   The dependencies form a Directed Acyclic Graph (DAG).  There will be no circular dependencies.
*   All task IDs will be unique and in the range `[1, N]`.
*   A valid schedule *always* exists (meaning all tasks can be completed respecting dependencies).
*   The input list of tasks is not guaranteed to be sorted by `id`.

**Output:**

An ordered list of task IDs representing the optimal execution schedule that minimizes the maximum lateness. If multiple schedules achieve the same minimum maximum lateness, return any one of them.

**Example:**

```
Input:
tasks = [
    (1, 5, 10, []),
    (2, 3, 15, [1]),
    (3, 8, 20, [1]),
    (4, 2, 12, [2, 3])
]

Possible Output (one optimal solution):
[1, 2, 3, 4]

Explanation:

Schedule: 1 -> 2 -> 3 -> 4
- Task 1: Completion time = 5, Lateness = max(0, 5-10) = 0
- Task 2: Completion time = 5 + 3 = 8, Lateness = max(0, 8-15) = 0
- Task 3: Completion time = 8 + 8 = 16, Lateness = max(0, 16-20) = 0
- Task 4: Completion time = 16 + 2 = 18, Lateness = max(0, 18-12) = 6
Maximum Lateness = 6

Another possible schedule: 1 -> 3 -> 2 -> 4
- Task 1: Completion time = 5, Lateness = max(0, 5-10) = 0
- Task 3: Completion time = 5 + 8 = 13, Lateness = max(0, 13-20) = 0
- Task 2: Completion time = 13 + 3 = 16, Lateness = max(0, 16-15) = 1
- Task 4: Completion time = 16 + 2 = 18, Lateness = max(0, 18-12) = 6
Maximum Lateness = 6

While other schedules are possible, none will result in a maximum lateness lower than 6.
```

**Judging Criteria:**

Your code will be judged on:

1.  **Correctness:**  Does your code produce the correct schedule with the minimal maximum lateness?
2.  **Efficiency:**  Your solution should be efficient enough to handle input sizes within the given constraints in a reasonable time. Inefficient algorithms will likely time out.
3.  **Clarity:** While not directly scored, well-structured and readable code is always appreciated.

**Hints:**

*   Consider topological sorting to handle dependencies.
*   Think about how to prioritize tasks once you have a valid topological order.  Earliest Deadline First (EDF) is a good starting point, but might not always give the *optimal* result with dependencies.
*   Consider dynamic programming or branch and bound strategies for more optimal solutions, especially if EDF fails. However, brute-force approaches will likely time out.
*   Be mindful of edge cases, such as tasks with zero duration or equal deadlines.

Good luck!
