## Question: Optimal Task Assignment with Dependencies and Deadlines

### Description

You are managing a large-scale project with `N` tasks. Each task `i` has the following properties:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= N).
*   `duration_i`: An integer representing the time (in days) required to complete the task.
*   `deadline_i`: An integer representing the deadline (in days from the start of the project) by which the task must be completed.
*   `dependencies_i`: A list of `id`s representing the tasks that must be completed before task `i` can start.

You have a team of `K` workers. Each worker can work on only one task at a time. You can assign any task to any worker, and tasks can be started on the same day if their dependencies are met.

The goal is to find a task assignment and scheduling that minimizes the number of late tasks (tasks completed after their deadline). If there are multiple schedules that minimize the number of late tasks, you want to further minimize the total lateness, where the lateness of a task is the amount of time (in days) by which it exceeds its deadline.

**Input:**

*   `N`: The number of tasks (1 <= `N` <= 1000).
*   `K`: The number of workers (1 <= `K` <= 100).
*   A list of `N` task descriptions, where each task description is a tuple: `(id_i, duration_i, deadline_i, dependencies_i)`. The `id`s are guaranteed to be unique and within the range `[1, N]`. The dependencies will refer to `id`s defined in the `N` task descriptions.

**Output:**

Return a tuple: `(num_late_tasks, total_lateness)`. If it's impossible to complete all tasks, return `(-1, -1)`.

**Constraints:**

*   Task durations are positive integers.
*   Deadlines are positive integers.
*   Dependencies form a directed acyclic graph (DAG).
*   The solution should be optimized for both time and memory efficiency. A naive solution might time out.
*   You need to handle edge cases, such as when the number of workers is much larger or smaller than the number of tasks.
*   The dependencies listed are valid, i.e., there are no circular dependencies.

**Example:**

```
N = 4
K = 2
tasks = [
    (1, 2, 5, []),  # id, duration, deadline, dependencies
    (2, 3, 7, [1]),
    (3, 1, 4, []),
    (4, 2, 9, [2, 3])
]

# Expected output: (0, 0)
# Explanation: One optimal schedule is:
# - Worker 1: Task 1 (days 0-2), Task 4 (days 5-7)
# - Worker 2: Task 3 (day 0), Task 2 (days 2-5)
# All tasks are completed on time.
```

**Judging Criteria:**

The solution will be judged based on the following criteria:

*   **Correctness:** The solution produces the correct output for various test cases, including edge cases.
*   **Efficiency:** The solution solves the problem within the time and memory limits. Solutions with high time complexity might time out.
*   **Code Quality:** The code is well-structured, readable, and maintainable.
