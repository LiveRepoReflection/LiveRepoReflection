Okay, here's a challenging JavaScript coding problem designed with your specified criteria in mind:

## Problem Description

**Title: Optimal Task Scheduling with Dependencies and Deadlines**

**Problem Statement:**

You are tasked with designing an optimal task scheduling algorithm for a distributed computing system. The system needs to execute a set of `N` tasks. Each task `i` has the following properties:

*   `id`: A unique integer identifier (0 to N-1).
*   `duration`: An integer representing the time units required to complete the task.
*   `deadline`: An integer representing the time unit by which the task must be completed.
*   `dependencies`: An array of integer `id`s representing the tasks that must be completed before this task can start. A task cannot start until all its dependencies are finished.

Your goal is to create a schedule that maximizes the number of tasks completed before their deadlines.

**Input:**

A list of `N` task objects, where each task object has the following structure:

```javascript
{
  id: number,
  duration: number,
  deadline: number,
  dependencies: number[] // Array of task IDs
}
```

**Output:**

Return an array containing the `id`s of the tasks that can be completed before their deadlines, sorted in the order in which they should be executed. If no schedule can complete any tasks, return an empty array.

**Constraints:**

*   `1 <= N <= 1000`
*   `1 <= duration <= 100`
*   `1 <= deadline <= 10000`
*   Dependencies can form complex graphs, including cycles.
*   The solution must be computationally efficient. A naive brute-force approach will likely time out.
*   If multiple optimal schedules exist (i.e., schedules that complete the same maximum number of tasks), return the lexicographically smallest schedule. Task IDs are integers, so standard integer comparison applies.

**Edge Cases to Consider:**

*   Cyclic dependencies: The task graph might contain cycles, making it impossible to complete all tasks in the cycle. You need to detect and handle these cases.
*   Tasks with no dependencies.
*   Tasks with very tight deadlines.
*   Conflicting dependencies and deadlines that make it impossible to complete all tasks, or even a significant number of tasks.
*   Empty input (no tasks).

**Optimization Requirements:**

*   The algorithm should be efficient in terms of time complexity. Aim for a solution better than O(N^2) if possible.
*   Consider using appropriate data structures to optimize the dependency resolution and scheduling process.

**System Design Aspects (Implicit):**

*   The solution should be scalable to handle a larger number of tasks.
*   Consider how the solution might be adapted to handle tasks with priorities or different resource requirements in a real-world distributed system.

Good luck!
