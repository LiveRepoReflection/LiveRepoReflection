## Problem: Optimal Task Scheduling with Dependencies and Resource Constraints

### Description

You are tasked with designing an optimal task scheduling algorithm for a complex project. The project consists of `N` tasks, each with a specific duration, resource requirement, and set of dependencies. Your goal is to determine a schedule that minimizes the project's overall completion time (makespan), while adhering to all task dependencies and resource constraints.

Each task `i` has the following properties:

*   `duration[i]` : An integer representing the time required to complete the task.
*   `resource_requirement[i]` : An integer representing the amount of a single, shared resource required by the task while it is being executed.
*   `dependencies[i]` : A list of integers representing the tasks that must be completed before task `i` can start. Task IDs are 0-indexed.

The project also has the following constraints:

*   **Dependencies:** A task cannot start until all of its dependencies have been completed.
*   **Resource Constraint:** At any given time, the total resource usage of all concurrently executing tasks cannot exceed a global `resource_limit`.
*   **Non-preemption:** Once a task starts, it must run to completion without interruption.

Your algorithm must determine the start time for each task such that the project's makespan is minimized.

**Input:**

*   `N`: An integer representing the number of tasks. `1 <= N <= 100`
*   `duration`: A vector of integers, where `duration[i]` is the duration of task `i`. `1 <= duration[i] <= 100`
*   `resource_requirement`: A vector of integers, where `resource_requirement[i]` is the resource requirement of task `i`. `1 <= resource_requirement[i] <= 50`
*   `dependencies`: A vector of vectors of integers, where `dependencies[i]` is a list of tasks that must be completed before task `i` can start.
*   `resource_limit`: An integer representing the maximum available resource. `1 <= resource_limit <= 100`

**Output:**

*   A vector of integers, where `start_time[i]` is the optimal start time for task `i`. If no valid schedule exists return an empty vector. If multiple optimal schedules with the same makespan exist, return any one of them.

**Constraints:**

*   Your solution must find a valid schedule if one exists.
*   Your solution should aim to minimize the makespan.
*   The time complexity of your solution is important. Solutions with exponential time complexity are unlikely to pass all test cases.
*   Consider different algorithmic approaches and data structures to optimize your solution.

**Example:**

```
N = 3
duration = [3, 2, 4]
resource_requirement = [2, 3, 2]
dependencies = [[], [0], [1]]
resource_limit = 4

Output: [0, 3, 5]

Explanation:
Task 0 starts at time 0 and finishes at time 3, using 2 resources.
Task 1 starts at time 3 (after task 0 finishes) and finishes at time 5, using 3 resources.
Task 2 starts at time 5 (after task 1 finishes) and finishes at time 9, using 2 resources.
The makespan is 9. This is the optimal schedule given the constraints.
```

**Challenge:**

This problem requires careful consideration of task dependencies, resource constraints, and makespan optimization. Efficient algorithms and data structures will be necessary to solve it within reasonable time limits. Explore approaches such as topological sorting, dynamic programming, constraint satisfaction, or heuristics to find the optimal or near-optimal schedule. Consider edge cases such as cyclic dependencies (which should result in returning an empty vector) and situations where no valid schedule is possible due to resource limitations.
