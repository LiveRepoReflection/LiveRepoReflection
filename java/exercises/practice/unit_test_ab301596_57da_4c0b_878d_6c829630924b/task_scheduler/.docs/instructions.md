## Question: Optimal Task Scheduling with Dependencies and Deadlines

**Description:**

You are tasked with designing an optimal task scheduler for a complex system. The system consists of 'N' tasks, each with the following properties:

*   `id`: A unique integer identifier for the task (1 to N).
*   `duration`: The time (in arbitrary units) required to complete the task.
*   `deadline`: The latest time by which the task must be completed.
*   `dependencies`: A list of task IDs that must be completed before this task can start. A task cannot start until all its dependencies are finished.

The goal is to find a valid schedule that completes all tasks before their respective deadlines while minimizing the overall completion time (makespan) of the entire system. However, minimizing the makespan is secondary to meeting all deadlines.

**Constraints and Requirements:**

1.  **Deadline Guarantee:** The primary objective is to complete all tasks before their deadlines. If no schedule can meet all deadlines, the system should report that a valid schedule is impossible.
2.  **Dependency Satisfaction:** All task dependencies must be strictly adhered to.
3.  **Single Processor:** Assume only one processor is available, so tasks cannot be executed in parallel.
4.  **Preemption Not Allowed:** Once a task starts, it must run to completion without interruption (no preemption).
5.  **Optimization:** If multiple schedules meet all deadlines, the schedule with the shortest makespan (overall completion time) should be preferred.
6.  **Large Input:** The number of tasks 'N' can be large (up to 10,000). Ensure your solution is efficient enough to handle this scale.
7.  **Cyclic Dependencies:** Detect and report if cyclic dependencies exist, as they make a valid schedule impossible.
8.  **Task IDs are Sequential:** Task IDs will always be a sequence of integers from 1 to N. This can be used to optimize data structure choices.
9.  **No two tasks share the same Task ID.**
10. **Durations are non-negative integers.**

**Input:**

The input will be a list of tasks. Each task is represented as a data structure (you can define your own Java class/struct). The overall input will be a list of these task structures.

**Output:**

If a valid schedule exists (all deadlines met, no cyclic dependencies), return a list of task IDs representing the optimal execution order. If no valid schedule exists (deadlines cannot be met or cyclic dependencies detected), return an empty list.

**Example:**

```
Tasks:
Task 1: duration = 5, deadline = 10, dependencies = []
Task 2: duration = 3, deadline = 15, dependencies = [1]
Task 3: duration = 2, deadline = 12, dependencies = [1]
Task 4: duration = 4, deadline = 20, dependencies = [2, 3]

Possible Valid Schedules (meeting deadlines):
1. [1, 2, 3, 4] - Completion Time: 5 + 3 + 2 + 4 = 14
2. [1, 3, 2, 4] - Completion Time: 5 + 2 + 3 + 4 = 14

Optimal Schedule (shortest makespan, meeting deadlines): Either [1, 2, 3, 4] or [1, 3, 2, 4] is acceptable.
```

**Challenge:**

This problem requires you to combine graph algorithms (for dependency resolution and cycle detection), potentially topological sorting, and potentially search or optimization techniques to find the best schedule that meets all constraints.  Consider using efficient data structures and algorithms to handle the large input size. The multiple constraints and optimization goal make this a challenging problem.
