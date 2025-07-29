## Problem: Optimal Task Scheduling with Dependencies and Deadlines

### Question Description

You are tasked with designing an optimal task scheduling algorithm for a distributed system. The system has a set of *n* tasks to execute. Each task *i* has the following properties:

*   **`id`**: A unique integer identifier for the task (0 to n-1).
*   **`duration`**: An integer representing the time (in seconds) required to complete the task.
*   **`deadline`**: An integer representing the deadline (in seconds) by which the task must be completed.  The deadline is relative to the start of the scheduling period (time 0).
*   **`dependencies`**: A list of task IDs that must be completed before this task can start.

Your system has the ability to execute tasks in parallel, but a single task must be executed on a single worker node without interruption. You have an *unlimited* number of worker nodes available.

The goal is to find a schedule that minimizes the **tardiness** of the tasks. Tardiness of a task is defined as `max(0, completion_time - deadline)`. The overall tardiness of the schedule is the sum of the tardiness of all tasks.

**Input:**

A list of tasks, where each task is represented as a dictionary or object with the properties mentioned above.

**Output:**

An integer representing the minimum total tardiness achievable by scheduling the tasks.

**Constraints:**

*   `1 <= n <= 1000` (Number of tasks)
*   `1 <= duration <= 1000` for each task
*   `1 <= deadline <= 10000` for each task
*   The dependencies form a Directed Acyclic Graph (DAG). There are no circular dependencies.
*   All task IDs will be valid (i.e., within the range 0 to n-1).

**Optimization Requirements:**

Your solution must be efficient enough to handle the maximum input size (n=1000) within a reasonable time limit (e.g., a few seconds). A naive brute-force approach will not be feasible. Consider using dynamic programming or other optimization techniques.

**Real-world Scenario:**

This problem models real-world scenarios in cloud computing, distributed systems, and project management, where tasks have dependencies, deadlines, and varying execution times.

**Example:**

```python
tasks = [
    {"id": 0, "duration": 5, "deadline": 10, "dependencies": []},
    {"id": 1, "duration": 3, "deadline": 8, "dependencies": [0]},
    {"id": 2, "duration": 7, "deadline": 15, "dependencies": [1]},
    {"id": 3, "duration": 2, "deadline": 20, "dependencies": []}
]

# One possible optimal schedule (not necessarily the only one):
# Task 0 starts at 0, finishes at 5
# Task 3 starts at 0, finishes at 2
# Task 1 starts at 5, finishes at 8
# Task 2 starts at 8, finishes at 15

# Tardiness:
# Task 0: max(0, 5 - 10) = 0
# Task 1: max(0, 8 - 8) = 0
# Task 2: max(0, 15 - 15) = 0
# Task 3: max(0, 2 - 20) = 0

# Minimum total tardiness: 0

```

**Multiple Valid Approaches:**

There might be multiple optimal schedules that achieve the minimum total tardiness. Your solution only needs to return the minimum total tardiness value, not the specific schedule. The solver is encouraged to explore different algorithmic strategies to find the most efficient solution.

**Algorithmic Efficiency Requirements:**

Solutions with time complexity worse than O(n^2) might time out for larger test cases.
