## Problem: Optimal Task Scheduling with Dependencies and Resource Constraints

**Description:**

You are tasked with designing an optimal task scheduling system for a high-performance computing cluster. The system needs to schedule a set of tasks, each with dependencies on other tasks and specific resource requirements, while minimizing the overall completion time (makespan).

**Input:**

The input consists of the following information:

*   `N`: The number of tasks. Tasks are numbered from 0 to N-1.
*   `tasks`: A vector of `N` task descriptions. Each task description contains:
    *   `duration`: An integer representing the execution time of the task.
    *   `resource_requirements`: A vector of pairs (resource_id, quantity) specifying the amount of each resource required by the task. Resource IDs are integers starting from 0.
    *   `dependencies`: A vector of integers representing the task IDs that must be completed before this task can start. Note that the dependencies can form a directed acyclic graph(DAG).
*   `resources`: A vector describing the available resources in the cluster. Each resource description contains:
    *   `capacity`: An integer representing the total capacity of the resource.

**Constraints:**

1.  **Dependencies:** A task can only start executing after all its dependencies are completed.
2.  **Resource Constraints:** A task can only execute if the cluster has enough available resources to satisfy the task's requirements *at the time of execution*. Multiple tasks can run concurrently, as long as resource constraints are respected. Each resource is globally available.
3.  **Non-preemption:** Once a task starts executing on the cluster, it cannot be interrupted or paused (non-preemptive scheduling).
4.  **Valid DAG:** The dependency graph formed by the tasks is guaranteed to be a Directed Acyclic Graph (DAG).
5.  **Task Order:** The tasks can start in any order that respects the dependencies.
6.  **Optimization Goal:** Minimize the overall makespan, which is the time when the last task finishes executing.
7.  **Resource ID:** Resource ID are consecutive number from 0.
8.  **Task ID:** Task ID are consecutive number from 0.

**Objective:**

Write a C++ program that takes the task and resource descriptions as input and determines the optimal schedule that minimizes the makespan. Your program should output the minimized makespan.

**Efficiency Requirements:**

*   The solution must be efficient enough to handle a large number of tasks (up to 1000) and resources (up to 100).
*   Consider using appropriate data structures and algorithms to achieve optimal performance. Backtracking solutions will likely time out.
*   Heuristic approaches might be necessary to achieve a good solution within the time limit.
*   The time complexity of the algorithm should be carefully considered.
*   You must use C++ in your implementation.

**Example:**

Let's say we have the following simplified input (This is not a complete input description):

*   `N = 3` (3 tasks)
*   Task 0: `duration = 5`, `dependencies = {}`
*   Task 1: `duration = 7`, `dependencies = {0}` (depends on Task 0)
*   Task 2: `duration = 3`, `dependencies = {0, 1}` (depends on Task 0 and Task 1)

A possible schedule:

1.  Task 0 starts at time 0 and finishes at time 5.
2.  Task 1 starts at time 5 (after Task 0 finishes) and finishes at time 12.
3.  Task 2 starts at time 12 (after Task 0 and Task 1 finish) and finishes at time 15.

In this schedule, the makespan is 15. The goal is to find the schedule that minimizes this makespan.

**Assumptions:**

*   All inputs are valid and adhere to the specified formats.
*   The problem is solvable (a valid schedule always exists).

This is a challenging optimization problem that requires careful consideration of dependencies, resource constraints, and algorithmic efficiency. Good luck!
