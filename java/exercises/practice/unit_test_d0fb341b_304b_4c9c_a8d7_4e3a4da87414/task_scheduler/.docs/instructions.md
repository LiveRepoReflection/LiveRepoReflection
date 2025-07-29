## Question: Optimal Task Scheduling with Dependencies and Deadlines

**Description:**

You are tasked with developing an optimal task scheduling algorithm for a complex system with numerous interdependent tasks and strict deadlines. The system consists of *n* tasks, where each task *i* has the following properties:

*   **`id` (Integer):** A unique identifier for the task (1 to *n*).
*   **`duration` (Integer):** The time (in arbitrary units) required to complete the task.
*   **`deadline` (Integer):** The latest time (in arbitrary units from the start of the schedule) by which the task must be completed.
*   **`dependencies` (List of Integers):** A list of task IDs that must be completed before this task can begin. A task cannot start if any of its dependencies are not yet finished.  The dependencies refer to the `id` of other tasks.

Your goal is to create a schedule that maximizes the number of tasks completed by their respective deadlines. The schedule should be represented as an ordered list of task IDs, indicating the sequence in which the tasks should be executed.

**Constraints:**

1.  **Valid Schedule:** The schedule must be valid, meaning that a task can only be scheduled if all its dependencies have been completed at that point in the schedule.
2.  **Single Processor:** You have only one processor, meaning only one task can be executed at any given time.
3.  **Non-Preemptive:** Once a task starts, it must run to completion without interruption.
4.  **Optimization Goal:** Maximize the number of tasks completed before or at their deadlines. If multiple schedules result in the same number of completed tasks, minimize the total lateness (sum of the positive differences between the completion time and deadline for all tasks).
5.  **Circular Dependencies:** Your algorithm must detect and handle circular dependencies. If circular dependencies exist, return an empty list.
6.  **Large Input:** The number of tasks *n* can be very large (up to 10,000). Your solution must be efficient enough to handle such large inputs within a reasonable time limit (e.g., a few seconds).
7.  **Integer Overflow:** Be mindful of potential integer overflows, especially when calculating completion times or lateness. Consider using appropriate data types (e.g., `long`) to prevent overflows.

**Input:**

A list of tasks, where each task is represented as an object or data structure containing the properties described above (`id`, `duration`, `deadline`, `dependencies`).

**Output:**

A list of task IDs representing the optimal schedule. If no valid schedule exists (due to circular dependencies), return an empty list.

**Example:**

```
Tasks:
Task 1: id=1, duration=3, deadline=7, dependencies=[]
Task 2: id=2, duration=2, deadline=5, dependencies=[1]
Task 3: id=3, duration=4, deadline=10, dependencies=[1, 2]
Task 4: id=4, duration=1, deadline=6, dependencies=[]

Possible Optimal Schedule: [1, 2, 4, 3]
(Task 1 finishes at 3, Task 2 finishes at 5, Task 4 finishes at 6, Task 3 finishes at 10. All tasks are completed on time.)

Another possible schedule: [4, 1, 2, 3]
(Task 4 finishes at 1, Task 1 finishes at 4, Task 2 finishes at 6, Task 3 finishes at 10. All tasks are completed on time.)

```

**Challenge:**

This problem requires a combination of graph algorithms (for dependency resolution), scheduling heuristics (to maximize completed tasks), and careful attention to detail to handle edge cases and optimization. Consider different scheduling algorithms (e.g., earliest deadline first, critical path method) and data structures (e.g., priority queues, adjacency lists) to achieve the best performance.

Good luck!
