## Question: Optimal Multi-Resource Task Scheduling

**Description:**

You are tasked with building a task scheduler for a high-performance computing environment. The environment consists of a cluster of heterogeneous machines, each possessing varying quantities of several resource types (e.g., CPU cores, GPU units, memory, disk space, network bandwidth).

There is a stream of incoming tasks that need to be scheduled on these machines. Each task requires a specific amount of each resource type to execute.  A task can only be executed on a machine if the machine has sufficient available resources to satisfy the task's requirements.  Once a task starts executing on a machine, it occupies those resources for its entire duration. Tasks are non-preemptive; once started, they cannot be paused or migrated to another machine.

Your goal is to design a scheduler that maximizes the throughput of the system (i.e., maximizes the number of tasks completed within a given time frame) while adhering to the resource constraints of each machine.

**Input:**

The input will be provided in the following format:

1.  **Machine Descriptions:** A list of machines, where each machine is described by:
    *   A unique machine ID (integer).
    *   A list of resource types and their available quantities on that machine.  Resource types are represented by strings (e.g., "CPU", "GPU", "Memory", "Disk", "Network"). Quantities are non-negative integers.

2.  **Task Stream:** A stream of tasks, where each task is described by:
    *   A unique task ID (integer).
    *   A list of resource types and their required quantities for execution.
    *   An estimated execution time (integer representing time units).
    *   An arrival time (integer representing time units).

3.  **Scheduling Horizon:** An integer representing the total time units for which the scheduler should operate.

**Output:**

Your scheduler should output a schedule of tasks. The schedule should be a list of tuples, where each tuple represents a scheduled task and contains:

*   The task ID.
*   The machine ID on which the task is scheduled.
*   The start time of the task.
*   The end time of the task.

**Constraints and Requirements:**

*   **Resource Constraints:**  No machine can execute more tasks than its available resources allow at any given time.
*   **Non-Preemption:** Once a task starts, it must run to completion on the same machine.
*   **Throughput Maximization:**  The scheduler should prioritize scheduling tasks to maximize the number of completed tasks within the scheduling horizon.
*   **Arrival Times:** Tasks cannot start executing before their arrival time.
*   **Optimization:** The number of machines and the length of the task stream can be very large. Design your algorithm to be efficient in terms of both time and space complexity. A naive brute-force approach will likely time out.
*   **Real-world Considerations:**  The scheduler should be robust and handle various edge cases, such as:
    *   Tasks with resource requirements that exceed the capacity of any single machine.
    *   Tasks arriving in a non-deterministic order.
    *   Machines with varying resource capacities.
*   **Tie-Breaking:** If multiple machines can accommodate a task, the scheduler should use a heuristic to select the "best" machine. You can implement your own heuristic or use a well-known scheduling algorithm for this purpose (e.g., First-Fit, Best-Fit, Worst-Fit).  Document your tie-breaking strategy.
*   **Scalability:** The solution should scale reasonably well with the number of machines and tasks.

**Example:**

(This is a simplified example. Real test cases will be much larger and more complex.)

**Input:**

```
Machines:
  Machine 1: {CPU: 4, Memory: 8}
  Machine 2: {CPU: 2, Memory: 4}

Tasks:
  Task 1: {CPU: 2, Memory: 4, Duration: 2, Arrival: 0}
  Task 2: {CPU: 1, Memory: 2, Duration: 3, Arrival: 1}
  Task 3: {CPU: 3, Memory: 6, Duration: 1, Arrival: 2}

Scheduling Horizon: 5
```

**Possible Output:**

```
[
  (Task 1, Machine 1, 0, 2),
  (Task 2, Machine 2, 1, 4),
  (Task 3, Machine 1, 2, 3)
]
```

**Grading:**

The solution will be evaluated based on the number of tasks completed within the scheduling horizon, subject to the resource constraints.  Performance (execution time) will also be a factor.  Solutions that correctly handle all test cases and achieve high throughput will receive higher scores.

This problem is designed to be challenging and requires a good understanding of data structures, algorithms, and system design principles. Good luck!
