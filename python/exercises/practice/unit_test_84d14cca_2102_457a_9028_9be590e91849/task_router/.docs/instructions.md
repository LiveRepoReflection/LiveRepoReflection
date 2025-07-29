## The Optimal Task Router

### Question Description

You are designing a task routing system for a large-scale distributed computing platform. This platform handles a massive number of tasks of varying types, priorities, and resource requirements. The goal is to design an efficient and intelligent task router that can distribute tasks to available worker nodes in a way that minimizes overall completion time and maximizes resource utilization.

**Input:**

*   `tasks`: A list of dictionaries, where each dictionary represents a task with the following keys:
    *   `task_id`: A unique integer identifier for the task.
    *   `task_type`: A string representing the type of task (e.g., "CPU-bound", "IO-bound", "Memory-intensive").
    *   `priority`: An integer representing the priority of the task (higher value means higher priority).
    *   `cpu_needed`: An integer representing the number of CPU cores required by the task.
    *   `memory_needed`: An integer representing the amount of memory (in GB) required by the task.
    *   `disk_io_needed`: An integer representing the I/O intensity of the task (higher value means more I/O operations).
*   `workers`: A list of dictionaries, where each dictionary represents a worker node with the following keys:
    *   `worker_id`: A unique integer identifier for the worker node.
    *   `cpu_available`: An integer representing the number of CPU cores available on the worker node.
    *   `memory_available`: An integer representing the amount of memory (in GB) available on the worker node.
    *   `disk_io_capacity`: An integer representing the I/O capacity of the worker node (higher value means more I/O operations).
    *   `task_types_supported`: A list of strings representing the task types that the worker node can execute.

**Output:**

A dictionary where the keys are `worker_id`s and the values are lists of `task_id`s assigned to that worker. Tasks should be routed in an optimal fashion (more details below). If a task cannot be assigned, it should be included in an 'unassigned' list as part of the returned dictionary.

**Constraints and Requirements:**

1.  **Feasibility:** A task can only be assigned to a worker if the worker has sufficient `cpu_available`, `memory_available`, and `disk_io_capacity` to meet the task's `cpu_needed`, `memory_needed`, and `disk_io_needed` requirements, respectively. The worker must also support the task's `task_type`.

2.  **Optimization Goal:** Your primary objective is to minimize the overall makespan, which is defined as the maximum completion time across all worker nodes. Assume that the execution time of each task is proportional to its `cpu_needed` value. Therefore, the completion time of a worker is the sum of `cpu_needed` values of the tasks assigned to it. Minimize the maximum of these sums across all workers.

3.  **Priority Handling:** Higher priority tasks should be given preference in assignment. If multiple tasks can be assigned to a worker, the highest priority task should be assigned first.

4.  **Resource Utilization:** While minimizing makespan is the primary goal, you should also strive to achieve good resource utilization across all worker nodes. Avoid assigning all tasks to a single worker if other workers have available resources.

5.  **Scalability:** Your solution should be efficient enough to handle a large number of tasks and workers (e.g., thousands of tasks and hundreds of workers).

6.  **Tie-Breaking:** If multiple workers are equally suitable for a task (i.e., they have the same completion time after assigning the task), choose the worker with the smallest `worker_id`.

7.  **Immutability:** Do not modify the input `tasks` and `workers` lists.

**Example:**

```python
tasks = [
    {"task_id": 1, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
    {"task_id": 2, "task_type": "IO-bound", "priority": 1, "cpu_needed": 1, "memory_needed": 2, "disk_io_needed": 3},
    {"task_id": 3, "task_type": "CPU-bound", "priority": 3, "cpu_needed": 3, "memory_needed": 6, "disk_io_needed": 2},
]

workers = [
    {"worker_id": 1, "cpu_available": 4, "memory_available": 8, "disk_io_capacity": 4, "task_types_supported": ["CPU-bound", "IO-bound"]},
    {"worker_id": 2, "cpu_available": 3, "memory_available": 6, "disk_io_capacity": 2, "task_types_supported": ["CPU-bound"]},
]

# Expected (or similar) output:
# {
#     1: [2, 3],  # Worker 1: Task 2 (IO-bound, priority 1) and Task 3 (CPU-bound, priority 3)
#     2: [1],  # Worker 2: Task 1 (CPU-bound, priority 2)
#     'unassigned': []
# }
```

**Judging Criteria:**

*   Correctness: The solution must produce a feasible assignment of tasks to workers, satisfying all constraints.
*   Optimality: The solution will be evaluated based on how well it minimizes the makespan and maximizes resource utilization.
*   Efficiency: The solution must be efficient enough to handle large input sizes.
*   Code Quality: The solution should be well-structured, readable, and maintainable.

**Hints:**

*   Consider using data structures such as heaps or priority queues to efficiently manage tasks and workers.
*   Explore different task scheduling algorithms, such as shortest processing time first, longest processing time first, or a combination of both.
*   Implement a greedy approach with backtracking to explore different assignment possibilities.
*   Think about how to balance priority handling with resource utilization.
*   Profile your code to identify performance bottlenecks and optimize accordingly.

This problem requires a combination of algorithm design, data structure selection, and optimization techniques. Good luck!
