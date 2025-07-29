## Question: Optimal Task Scheduling with Dependencies and Deadlines

### Project Name

`task_scheduler`

### Question Description

You are tasked with building an optimal task scheduler for a distributed computing system. The system has a set of `N` independent tasks that need to be executed. Each task `i` has the following properties:

*   `id_i`: A unique identifier for the task (integer).
*   `processing_time_i`: The time (in seconds) required to execute the task (integer).
*   `deadline_i`: The deadline (in seconds) by which the task must be completed (integer). The deadline is relative to the start of the scheduling process.
*   `dependencies_i`: A list of task IDs that must be completed before task `i` can start.

The system has a cluster of `K` identical machines that can execute tasks in parallel.  Each machine can only execute one task at a time.  Switching between tasks on a machine takes negligible time.

Your goal is to design an algorithm that determines a schedule for the tasks that minimizes the **tardiness**.  The tardiness of a task is defined as `max(0, completion_time_i - deadline_i)`, where `completion_time_i` is the time at which the task `i` finishes execution. The overall tardiness is the **sum** of the tardiness of all tasks.

You need to write a function that takes as input:

*   `N`: The number of tasks.
*   `K`: The number of machines.
*   A list of task properties represented as tuples: `(id_i, processing_time_i, deadline_i, dependencies_i)`.  `dependencies_i` is a list of integers representing the `id_i` of the prerequisite tasks.

Your function should return the **minimum possible overall tardiness** achieved by an optimal schedule. If it is impossible to schedule all tasks such that all dependencies are met, return `-1`.

**Constraints:**

*   `1 <= N <= 20`
*   `1 <= K <= N`
*   `1 <= processing_time_i <= 100`
*   `1 <= deadline_i <= 1000`
*   Task IDs are unique and range from 0 to N-1.
*   Dependencies form a Directed Acyclic Graph (DAG).  There are no circular dependencies.
*   The input list of task properties is provided in no particular order.

**Optimization Requirements:**

Your solution should aim for optimal or near-optimal performance.  Brute-force approaches that explore all possible schedules may not be efficient enough to pass all test cases within the time limit. Consider using techniques like dynamic programming, branch and bound, or heuristic search to improve performance.

**Edge Cases:**

*   Handle cases where no schedule can satisfy the dependencies.
*   Handle cases where K = 1 (single machine).
*   Handle cases where K = N (each task can be assigned to its own machine).
*   Handle cases with very tight deadlines.
*   Handle cases where some tasks have no dependencies and can be executed immediately.
