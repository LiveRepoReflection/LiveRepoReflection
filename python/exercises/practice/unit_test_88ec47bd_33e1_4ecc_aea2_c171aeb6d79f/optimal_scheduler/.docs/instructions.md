## Project Name

`OptimalTaskScheduler`

## Question Description

You are tasked with designing an optimal task scheduler for a distributed computing system. The system consists of `n` worker nodes and a stream of independent tasks that need to be executed. Each task `i` has a processing time `t_i` and a deadline `d_i`. Each worker node can only execute one task at a time.

The goal is to design a scheduling algorithm that minimizes the **maximum lateness** among all tasks. The lateness of a task `i` is defined as `max(0, completion_time_i - d_i)`.

**Input:**

*   `n`: The number of worker nodes (1 <= n <= 1000).
*   `tasks`: A list of tuples, where each tuple `(t_i, d_i)` represents a task. `t_i` is the processing time and `d_i` is the deadline of task `i` (1 <= t_i, d_i <= 10^9). The number of tasks can be very large (up to 10^6), arriving as a stream.

**Output:**

*   The minimum possible maximum lateness achievable by any scheduling algorithm.

**Constraints:**

*   **Online Scheduling:** You need to design an *online* algorithm, meaning you must make scheduling decisions as tasks arrive without knowing future tasks.
*   **Real-time Performance:** Given the large number of tasks, your algorithm must be efficient. Aim for a time complexity that avoids quadratic or worse behaviors.
*   **Task Assignment:** You need to decide which worker node will execute which task.
*   **Preemption is NOT allowed:** Once a task is assigned to a worker, it must run to completion without interruption.
*   **Prioritization:** You are free to come up with rules on how to prioritize tasks.
*   **Tie breaking**: If multiple workers are available at the same time, use a deterministic tie-breaking rule (e.g., assign to the worker with the lowest ID).

**Judging Criteria:**

*   The correctness of the solution (i.e., the computed maximum lateness is indeed the minimum possible given the schedule).
*   The efficiency of the algorithm (time complexity and memory usage).
*   The handling of edge cases and constraints.

**Example:**

```
n = 2  # 2 worker nodes
tasks = [(2, 5), (1, 3), (3, 8), (2, 4)]
```

One possible schedule (not necessarily optimal) could be:

*   Worker 1: Task 1 (2, 5), Task 3 (3, 8)
*   Worker 2: Task 2 (1, 3), Task 4 (2, 4)

Completion times:

*   Task 1: 2
*   Task 2: 1
*   Task 3: 2 + 3 = 5
*   Task 4: 1 + 2 = 3

Lateness:

*   Task 1: max(0, 2 - 5) = 0
*   Task 2: max(0, 1 - 3) = 0
*   Task 3: max(0, 5 - 8) = 0
*   Task 4: max(0, 3 - 4) = 0

Maximum Lateness: 0

**Challenge:**

The difficulty lies in finding a strategy that can adapt to the stream of tasks and make near-optimal decisions in real-time, as calculating the absolute optimal solution would likely require knowing the entire task set upfront (which is not possible in an online scenario). The large input size and the need for efficiency adds another layer of complexity.
