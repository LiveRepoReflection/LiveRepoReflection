## Question: Optimal Task Assignment with Dependencies and Deadlines

**Problem Description:**

You are tasked with designing a task scheduling system for a complex project. The project consists of `N` tasks, numbered from 0 to `N-1`. Each task has the following properties:

*   **ID:** A unique integer identifier (0 to N-1).
*   **Duration:** An integer representing the time required to complete the task.
*   **Deadline:** An integer representing the latest time the task must be completed.
*   **Dependencies:** A list of task IDs that must be completed before this task can start.

Your system needs to determine the optimal order in which to execute these tasks to minimize the overall project completion time (makespan) while ensuring that all deadlines are met.

**Input:**

The input will be provided as a list of tasks. Each task is represented by a struct or a similar data structure containing its ID, duration, deadline, and a list of dependencies. Specifically, the input is a slice of structs `[]Task` where Task is defined as:

```go
type Task struct {
	ID         int
	Duration   int
	Deadline   int
	Dependencies []int
}
```

**Output:**

The function should return:

1.  A slice of integers representing the optimal task execution order (task IDs).
2.  The makespan (total time to complete all tasks) of the optimal schedule.
3.  A boolean indicating whether a feasible schedule exists (i.e., all tasks can be completed before their deadlines).

Return an empty slice, `0`, and `false` if no feasible schedule exists.

**Function Signature:**

```go
func ScheduleTasks(tasks []Task) ([]int, int, bool)
```

**Constraints and Requirements:**

*   **Number of Tasks (N):** 1 <= N <= 1000
*   **Task Duration:** 1 <= Duration <= 100
*   **Task Deadline:** 1 <= Deadline <= 10000
*   **Dependencies:** A task can depend on any number of other tasks (including none).
*   **Cycle Detection:** Your solution must handle cyclic dependencies. If a cycle exists, return an empty slice, `0`, and `false`.
*   **Optimization:** The primary goal is to find *a* feasible schedule with a minimal makespan, not necessarily *the* minimal makespan (finding the absolute minimum makespan with deadlines can be NP-hard, so finding one solution quickly is sufficient to pass the test)
*   **Efficiency:** Aim for a solution with reasonable time complexity. Brute-force approaches will likely time out. Consider using topological sorting, dynamic programming, or greedy approaches combined with heuristics.
*   **Real-World Considerations:** Think about how task priorities might influence scheduling in real-world scenarios. While not explicitly part of the scoring, considering this can help guide your design choices.
*   **Edge Cases:** Thoroughly consider edge cases, such as tasks with no dependencies, tasks with very tight deadlines, and scenarios where the task durations are significantly longer than the deadlines.

**Scoring:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** Does the solution produce a valid schedule that meets all dependencies and deadlines when a feasible schedule exists?
2.  **Feasibility Detection:** Does the solution correctly identify and report infeasible schedules (cycles, impossible deadlines)?
3.  **Makespan Optimization:** How close is the makespan of the generated schedule to the optimal makespan (within a reasonable margin)? You don't have to find the absolute optimal, but significant deviations will be penalized.
4.  **Time Complexity:** Is the solution efficient enough to handle the maximum input size within the time limit?

This problem requires a combination of graph algorithms (for dependency management and cycle detection), scheduling techniques (for deadline handling and makespan optimization), and careful consideration of edge cases.
