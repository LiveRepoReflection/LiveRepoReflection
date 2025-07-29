## The Optimal Task Assignment Problem

**Question Description:**

You are managing a large-scale distributed computing system responsible for processing a massive number of independent tasks. Each task requires a specific amount of computational resources (CPU, Memory, Disk I/O) and has a deadline by which it must be completed.

Your system consists of a heterogeneous cluster of machines, each with varying capabilities in terms of CPU cores, memory, and disk I/O speed. Each machine can execute multiple tasks concurrently, but its resources are limited. The execution time of a task on a machine depends on both the task's resource requirements and the machine's capabilities.

Given:

*   **N Tasks:** Each task `i` has:
    *   `cpu_req[i]`: CPU cores required (integer).
    *   `mem_req[i]`: Memory required (in GB, integer).
    *   `io_req[i]`: Disk I/O required (integer).
    *   `deadline[i]`: Deadline in seconds (integer).
    *   `estimated_runtime[i]`: Estimated runtime on a "standard" machine (integer seconds).
*   **M Machines:** Each machine `j` has:
    *   `cpu_capacity[j]`: Number of CPU cores available (integer).
    *   `mem_capacity[j]`: Memory available (in GB, integer).
    *   `io_speed[j]`: Disk I/O speed factor (float, e.g., 1.0 is standard, 2.0 is twice as fast).
*   A function `calculate_runtime(task_runtime, cpu_req, cpu_capacity, mem_req, mem_capacity, io_req, io_speed)` that estimates the actual runtime of a task on a given machine. This function factors in the resource requirements of the task and the machine's capabilities. Assume that higher CPU capacity, higher memory capacity and higher I/O speed will decrease actual runtime. The exact nature of the `calculate_runtime` function is provided but you are expected to leverage it efficiently.
*   A scaling factor `overload_penalty` that multiplies the `estimated_runtime` if the machine is overloaded (see below)

Your goal is to find an assignment of tasks to machines that maximizes the number of completed tasks before their deadlines. A task is considered completed if its actual runtime on the assigned machine is less than or equal to its deadline.

**Constraints and Requirements:**

1.  **Resource Constraints:** A machine cannot be assigned tasks that, in aggregate, exceed its CPU and memory capacity at any given time.  Consider the *worst-case* scenario for resource usage. If multiple tasks are assigned to a machine, assume their resource usage is additive and happens concurrently.
2.  **Optimization Goal:** Maximize the number of tasks completed *before* their deadlines.
3.  **Runtime Efficiency:** The solution must be computationally efficient. The number of tasks and machines can be large (up to 1000 tasks and 100 machines).  Brute-force approaches will not be feasible. Consider algorithmic complexity in your solution.
4.  **Machine Overload:** If the *total* CPU requirement of tasks assigned to a machine exceeds its CPU capacity, or the total memory requirement of tasks assigned to a machine exceeds its memory capacity, the machine is considered *overloaded*. The `estimated_runtime` of each task running on an overloaded machine should be multiplied by an `overload_penalty` factor. This penalty should be applied *before* comparing the actual runtime with the deadline.
5.  **Tie-Breaking:** If multiple assignments lead to the same number of completed tasks, prioritize assignments that minimize the total resource usage across all machines (CPU + Memory).
6.  **`calculate_runtime` Function:** The `calculate_runtime` function is provided, and you *must* use it to estimate the runtime of each task on each machine.  You are not allowed to modify this function.
7.  **No Preemption:** Once a task is assigned to a machine, it must run to completion on that machine. Task migration or preemption is not allowed.
8.  **All tasks must be assigned:** Even if the task cannot be completed before its deadline.
9.  **Input Format:** The input will be provided as lists and integers as described above.

**Output:**

A list of integers representing the machine assignment for each task. The i-th element of the list should be the index `j` of the machine to which task `i` is assigned (0-indexed).

**Example:**
```python
def calculate_runtime(task_runtime, cpu_req, cpu_capacity, mem_req, mem_capacity, io_req, io_speed):
    """
    Estimates the runtime of a task on a given machine.
    This is a simplified model and can be changed for testing.
    """
    cpu_factor = min(1.0, cpu_capacity / cpu_req) if cpu_req > 0 else 1.0
    mem_factor = min(1.0, mem_capacity / mem_req) if mem_req > 0 else 1.0
    adjusted_io_speed = max(0.1, io_speed) # Avoid division by zero or negative values
    io_factor = adjusted_io_speed
    return int(task_runtime / (cpu_factor * mem_factor * io_factor))

# Example usage (not a complete test case)
cpu_req = [2, 4, 1]
mem_req = [4, 8, 2]
io_req = [10, 5, 1]
deadline = [100, 200, 50]
estimated_runtime = [50, 100, 25]

cpu_capacity = [4, 8]
mem_capacity = [8, 16]
io_speed = [1.0, 2.0]

overload_penalty = 2

# Expected output (this is just a possible assignment, not necessarily optimal)
# [0, 1, 0]  # Task 0 assigned to machine 0, Task 1 assigned to machine 1, Task 2 assigned to machine 0

```

**Judging Criteria:**

*   Correctness: The solution must produce a valid task assignment that respects the resource constraints.
*   Optimality: The solution must maximize the number of completed tasks before their deadlines.  A higher score will be given to solutions that consistently achieve higher completion rates.
*   Efficiency: The solution must execute within a reasonable time limit.  Solutions that are too slow will be penalized.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires careful consideration of resource allocation, scheduling, and optimization techniques. Good luck!
