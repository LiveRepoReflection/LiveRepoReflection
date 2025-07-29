Okay, here is a challenging and sophisticated Python coding problem, designed to be difficult and require a deep understanding of algorithms and data structures.

## Project Name

`ResourceAllocationOptimizer`

### Question Description

A large-scale distributed system manages a heterogeneous pool of resources (CPU cores, memory, disk space, network bandwidth, etc.).  Each resource type has a limited capacity.  Incoming tasks arrive dynamically, each with a deadline and a request for a specific quantity of each resource type.  Tasks are independent and can be executed in any order, but once started, cannot be preempted or migrated.

Your task is to implement a resource allocation optimizer that maximizes the number of tasks completed before their deadlines.

Specifically, you are given:

1.  `resource_capacities`: A dictionary where the keys are resource types (strings, e.g., "CPU", "Memory", "Disk") and the values are the available capacity of each resource (integers).  This represents the total capacity of the resource pool at the start.

2.  `tasks`: A list of tuples, where each tuple represents a task. Each tuple has the following format: `(task_id, deadline, resource_requests)`.
    *   `task_id`: A unique identifier for the task (integer).
    *   `deadline`: The time by which the task must be completed (integer, representing a timestamp).
    *   `resource_requests`: A dictionary where the keys are resource types (strings, same as `resource_capacities`) and the values are the amount of each resource type required by the task (integers).

3.  `task_durations`: A dictionary where the keys are `task_id`s and the values are the amount of time it takes to complete this task.(integers)

You need to implement a function `optimize_allocation(resource_capacities, tasks, task_durations)` that returns a list of `task_id`s representing the optimal set of tasks to execute to maximize the number of completed tasks before their deadlines.

**Constraints and Requirements:**

*   **Maximization:** The primary goal is to maximize the *number* of tasks completed by their deadlines, NOT to maximize resource utilization.
*   **Dynamic Arrival:** Tasks arrive dynamically (all tasks are given in the initial `tasks` list), so you need to consider the best scheduling strategy to accommodate as many as possible.
*   **Non-Preemption:** Once a task starts executing, it cannot be stopped or moved.
*   **Independent Tasks:** Tasks are independent of each other. There are no dependencies between tasks.
*   **Resource Constraints:** At any given time, the total resource consumption of running tasks must not exceed the `resource_capacities`.
*   **Deadline Constraints:** Tasks must be completed by their deadlines.  You must consider the execution time of each task when deciding whether to schedule it.
*   **Optimization:**  The solution should be efficient, especially for a large number of tasks (e.g., 1000+ tasks).  Brute-force approaches will likely time out. Consider using dynamic programming or greedy approaches with intelligent heuristics.
*   **Edge Cases:** Handle cases where:
    *   A task requests more of a resource than is available.
    *   There are no tasks to schedule.
    *   No task can be completed by its deadline given resource constraints.
    *   Tasks have identical deadlines.
*   **Multiple Valid Solutions:** If multiple sets of tasks achieve the same maximum number of completed tasks, any one of them is considered a valid solution.
*   **Resource contention:** The tasks are highly resource-intensive, and there will be substantial contention for resources, making scheduling decisions critical.

**Input Format:**

```python
resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
tasks = [
    (1, 10, {"CPU": 4, "Memory": 8, "Disk": 100}),
    (2, 15, {"CPU": 2, "Memory": 4, "Disk": 50}),
    (3, 20, {"CPU": 8, "Memory": 16, "Disk": 200}),
    (4, 12, {"CPU": 1, "Memory": 2, "Disk": 25}),
    (5, 18, {"CPU": 4, "Memory": 8, "Disk": 100}),
]
task_durations = {1: 5, 2: 3, 3: 10, 4: 2, 5: 6}
```

**Expected Output:**

A list of `task_id`s representing the optimal set of tasks to schedule, e.g., `[1, 2, 4, 5]`

**Scoring:**

Solutions will be evaluated based on correctness (all tasks in the returned list are completed by their deadlines and resource constraints are met), the number of tasks completed, and the efficiency of the algorithm (runtime). Solutions that pass the correctness tests but are slow will receive a lower score.

This problem requires a careful balancing act between resource management, scheduling, and optimization. Good luck!
