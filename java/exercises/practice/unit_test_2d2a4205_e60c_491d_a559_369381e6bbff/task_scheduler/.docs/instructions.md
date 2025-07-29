## Question Title: Efficient Task Scheduling with Dependencies and Deadlines

### Question Description:

You are tasked with designing an efficient task scheduling system for a high-performance computing environment. There are `N` tasks that need to be executed. Each task `i` has the following properties:

*   `id_i`: A unique integer identifier (1 <= `id_i` <= N).
*   `duration_i`: The time (in seconds) required to execute the task.
*   `deadline_i`: The latest time (in seconds, from the start of the scheduling window) by which the task must be completed.
*   `dependencies_i`: A list of `id`s of other tasks that must be completed before task `i` can start.

The goal is to determine the optimal schedule to execute all tasks such that the number of late tasks (tasks completed after their deadline) is minimized. If multiple schedules achieve the same minimal number of late tasks, choose the schedule with the smallest total tardiness (sum of the lateness of each late task). Lateness of a task is defined as `max(0, completion_time - deadline)`.

**Input:**

A list of tasks, where each task is represented as a tuple: `(id, duration, deadline, dependencies)`. For example:

```
tasks = [
    (1, 5, 10, []),        # Task 1: id=1, duration=5, deadline=10, no dependencies
    (2, 3, 15, [1]),       # Task 2: id=2, duration=3, deadline=15, depends on task 1
    (3, 7, 20, [1, 2]),    # Task 3: id=3, duration=7, deadline=20, depends on tasks 1 and 2
    (4, 2, 12, []),        # Task 4: id=4, duration=2, deadline=12, no dependencies
    (5, 4, 25, [3, 4])     # Task 5: id=5, duration=4, deadline=25, depends on tasks 3 and 4
]
```

**Output:**

An optimal schedule represented as a list of task `id`s in the order they should be executed. If no schedule can complete all tasks (due to dependency conflicts or impossible deadlines), return an empty list `[]`.

**Constraints:**

*   `1 <= N <= 1000` (Number of tasks)
*   `1 <= duration_i <= 100`
*   `1 <= deadline_i <= 10000`
*   Dependencies can form complex directed acyclic graphs (DAGs).
*   The sum of all task durations will not exceed 50000.

**Efficiency Requirements:**

*   The solution must be efficient enough to handle the maximum input size (`N = 1000`) within a reasonable time limit (e.g., a few seconds). Consider time complexity when designing your algorithm.
*   Avoid unnecessary computations and data structure overhead.

**Edge Cases:**

*   Tasks with no dependencies.
*   Tasks with circular dependencies (should result in an empty list).
*   Tasks with conflicting deadlines and dependencies, making it impossible to complete all tasks on time (should result in an empty list).
*   Empty input list.

**Example:**

For the input `tasks` above, a possible optimal schedule could be `[1, 4, 2, 3, 5]`. Another valid solution is `[4, 1, 2, 3, 5]`. The exact optimal schedule might vary depending on your implementation and tie-breaking strategies. The key is to minimize late tasks and then total tardiness.
