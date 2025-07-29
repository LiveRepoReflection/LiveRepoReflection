## Question Title: Optimal Task Scheduling with Dependencies and Deadlines

**Question Description:**

You are tasked with designing an optimal task scheduling algorithm for a high-performance computing system. The system needs to execute a set of `N` tasks, where each task `i` has the following properties:

*   `id_i`: A unique identifier for the task (integer).
*   `duration_i`: The time (in milliseconds) required to execute the task (integer).
*   `deadline_i`: The time (in milliseconds) by which the task must be completed (integer, relative to the start of the scheduling period).
*   `dependencies_i`: A list of `id`s of other tasks that must be completed before task `i` can start.  A task cannot begin execution until all of its dependencies have been completed.

The computing system has a limited number of `K` identical processing units (cores) that can execute tasks in parallel. A core can only execute one task at a time. Once a task starts on a core, it must run to completion without interruption.

Your goal is to design an algorithm that determines a schedule for executing the tasks such that the following objectives are optimized in order of priority:

1.  **Feasibility:** All tasks must be completed by their deadlines. If it is impossible to meet all deadlines, the algorithm should return an indication of infeasibility (e.g., a specific error code or exception).
2.  **Makespan Minimization:** If a feasible schedule exists, minimize the makespan. The makespan is the total time required to complete all tasks (the completion time of the last task to finish).
3.  **Resource Utilization:** Among feasible schedules with similar makespans, prefer schedules that maximize resource utilization. Resource utilization can be measured as the average core usage over time, defined as `(sum of task durations) / (makespan * K)`.

**Input:**

The input will be provided as a list of tasks and the number of cores:

*   `tasks`: A list of `Task` objects, where `Task` is defined as:

```java
class Task {
    int id;
    int duration;
    int deadline;
    List<Integer> dependencies;
}
```

*   `numCores`: An integer representing the number of processing cores (`K`).

**Output:**

If a feasible schedule exists, return a list of `ScheduleEvent` objects, representing the schedule. The `ScheduleEvent` is defined as:

```java
class ScheduleEvent {
    int taskId;
    int coreId;
    int startTime;
    int endTime;
}
```

Each `ScheduleEvent` indicates that task `taskId` is executed on `coreId` starting at `startTime` and finishing at `endTime`. The events in the list should be sorted by `startTime` in ascending order.

If no feasible schedule exists, return `null`.

**Constraints:**

*   `1 <= N <= 1000` (number of tasks)
*   `1 <= K <= 100` (number of cores)
*   `1 <= duration_i <= 1000` (duration of each task in milliseconds)
*   `1 <= deadline_i <= 100000` (deadline of each task in milliseconds)
*   Task IDs are unique and range from 1 to N (inclusive).
*   Dependencies form a directed acyclic graph (DAG). There are no circular dependencies.

**Example:**

```java
// Example Task Data (Task ID, Duration, Deadline, Dependencies)
Task task1 = new Task(1, 10, 50, List.of());
Task task2 = new Task(2, 15, 60, List.of(1)); // Depends on task 1
Task task3 = new Task(3, 8, 40, List.of());
Task task4 = new Task(4, 12, 70, List.of(2, 3)); // Depends on task 2 and task 3

List<Task> tasks = List.of(task1, task2, task3, task4);
int numCores = 2;

// Expected output (example, actual output depends on optimal scheduling algorithm)
// ScheduleEvent(taskId=1, coreId=0, startTime=0, endTime=10)
// ScheduleEvent(taskId=3, coreId=1, startTime=0, endTime=8)
// ScheduleEvent(taskId=2, coreId=0, startTime=10, endTime=25)
// ScheduleEvent(taskId=4, coreId=1, startTime=25, endTime=37)
```

**Judging Criteria:**

The solution will be judged based on correctness, efficiency, and adherence to the specified constraints. Correctness will be assessed by verifying that the generated schedule is feasible (all tasks complete by their deadlines and dependencies are satisfied) and produces the optimal makespan. Efficiency will be measured by the execution time of the algorithm.  Solutions with significantly higher time complexity will be penalized. Bonus points may be awarded for elegant and well-documented code. Solutions that correctly handle edge cases and optimize for resource utilization will also be favored.

**Hints:**

*   Consider using graph algorithms for dependency management.
*   Explore different scheduling heuristics (e.g., earliest deadline first, longest processing time first) and adapt them to handle dependencies and multiple cores.
*   Dynamic programming or branch-and-bound techniques might be helpful for finding optimal solutions, but be mindful of time complexity constraints.
*   Carefully manage resource allocation to minimize idle time and maximize parallelism.
*   Pay close attention to potential race conditions and synchronization issues when dealing with parallel execution.
