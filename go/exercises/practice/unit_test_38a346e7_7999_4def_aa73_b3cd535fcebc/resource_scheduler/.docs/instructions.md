## Question: Optimal Multi-Resource Task Scheduling

**Problem Description:**

You are tasked with building a task scheduler for a distributed computing system. This system has `n` worker nodes, each with varying amounts of different resource types. The resource types are CPU cores, RAM (in GB), and Disk space (in GB). Each worker node `i` has `cpu_i`, `ram_i`, and `disk_i` representing the available amount of each resource.

You have a set of `m` tasks to schedule. Each task `j` requires a specific amount of each resource: `cpu_j`, `ram_j`, and `disk_j`.

The goal is to schedule as many tasks as possible onto the worker nodes, subject to the following constraints:

1.  **Resource Constraints:** A task can only be assigned to a worker node if the worker node has enough of all three resource types to satisfy the task's requirements. Once a task is assigned to a worker node, the available resources on that node are reduced by the task's resource consumption.

2.  **Single Assignment:** Each task can be assigned to at most one worker node.

3.  **Node Capacity:** A worker node can have multiple tasks assigned to it as long as it has sufficient resources to satisfy all assigned tasks.

4.  **Priority:** Tasks have associated priorities. Higher priority tasks should be scheduled before lower priority tasks. Priorities are represented as integers, where a larger integer indicates higher priority.

5.  **Non-Preemption:** Once a task is assigned to a worker node, it cannot be moved to another node or preempted (removed to schedule another task).

Your program should take as input:

*   `n`: The number of worker nodes.
*   `m`: The number of tasks.
*   `workers`: A 2D array representing the worker nodes. `workers[i]` contains `cpu_i`, `ram_i`, and `disk_i` for worker node `i`.
*   `tasks`: A 2D array representing the tasks. `tasks[j]` contains `cpu_j`, `ram_j`, `disk_j`, and `priority_j` for task `j`.

Your program should output the maximum number of tasks that can be scheduled.

**Constraints:**

*   1 <= `n` <= 1000
*   1 <= `m` <= 1000
*   1 <= `cpu_i`, `ram_i`, `disk_i`, `cpu_j`, `ram_j`, `disk_j` <= 1000
*   1 <= `priority_j` <= 1000
*   The solution must be efficient. Brute-force solutions will likely time out. Consider algorithmic complexity.

**Example:**

```
n = 2
m = 3
workers = [[4, 4, 4], [3, 3, 3]]
tasks = [[2, 2, 2, 1], [1, 1, 1, 2], [3, 3, 3, 3]]

Output: 3
```

**Explanation of the Example:**

1.  Sort tasks by priority (descending): `[[3, 3, 3, 3], [1, 1, 1, 2], [2, 2, 2, 1]]`
2.  Schedule task 0 (priority 3) to worker 0. Remaining resources: worker 0 = `[2, 2, 2]`
3.  Schedule task 1 (priority 2) to worker 1. Remaining resources: worker 1 = `[2, 2, 2]`
4.  Schedule task 2 (priority 1) to worker 0. Remaining resources: worker 0 = `[0, 0, 0]`

All 3 tasks can be scheduled.

**Optimization Requirements:**

Aim for a solution with a time complexity better than O(n\*m\*log(m)) where n is the number of workers and m is the number of tasks. Solutions with high memory usage will also be penalized.

**Edge Cases:**

*   Tasks with extremely high resource requirements compared to worker node capacity.
*   Large numbers of tasks with identical priorities.
*   No tasks can be scheduled.

This problem requires a good understanding of resource allocation, scheduling algorithms, and efficient data structures. It also emphasizes the importance of considering various constraints and edge cases.
