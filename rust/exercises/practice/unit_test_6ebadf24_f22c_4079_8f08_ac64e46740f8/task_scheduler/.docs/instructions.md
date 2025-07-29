## Problem: Optimal Task Scheduling with Dependencies and Deadlines

You are tasked with designing an optimal task scheduling algorithm for a complex system. The system needs to execute a set of `n` tasks, each with dependencies on other tasks, a processing time, and a deadline.

Each task `i` has the following attributes:

*   `id`: A unique integer identifier (0 to n-1).
*   `processing_time`: An integer representing the time units required to complete the task.
*   `deadline`: An integer representing the latest time unit by which the task must be completed.
*   `dependencies`: A list of task `id`s that must be completed before this task can start. Circular dependencies are possible but will result in an invalid schedule.

Your goal is to find a schedule that minimizes the total *weighted tardiness* of the tasks. The *tardiness* of a task is defined as `max(0, completion_time - deadline)`, where `completion_time` is the time the task finishes executing. The *weighted tardiness* of a task is the tardiness multiplied by the task's `processing_time`.

Formally:

Minimize:  ∑ (`processing_time[i]` * max(0, `completion_time[i]` - `deadline[i]`)) for all `i` from 0 to n-1.

Subject to:

*   A task can only start after all its dependencies are completed.
*   Only one task can be executed at any given time.
*   Tasks must be executed non-preemptively (once a task starts, it must run until completion).

**Input:**

A vector of tasks, where each task is represented by a struct or class containing `id`, `processing_time`, `deadline`, and `dependencies`.

**Output:**

Return the minimum possible total weighted tardiness achievable by a valid schedule. If no valid schedule exists (due to circular dependencies making it impossible to complete all tasks), return -1.

**Constraints:**

*   `1 <= n <= 20`
*   `1 <= processing_time[i] <= 100`
*   `1 <= deadline[i] <= 1000`
*   Task IDs are unique and range from 0 to n-1.

**Efficiency Requirements:**

Given the small size of `n` this problem is NP-hard and backtracking or branch and bound may be suitable, but the solution must execute within a reasonable time limit (e.g., 1 second). Pay attention to pruning the search space to improve performance.

**Example:**

```rust
struct Task {
    id: usize,
    processing_time: i32,
    deadline: i32,
    dependencies: Vec<usize>,
}

fn solve_task_scheduling(tasks: Vec<Task>) -> i32 {
    // Your code here
}
```
