## The Optimal Task Scheduler

**Question Description:**

You are tasked with designing an optimal task scheduler for a distributed computing system. The system consists of `n` identical worker nodes and needs to execute `m` independent tasks. Each task `i` has a known processing time `t_i` and a deadline `d_i`.

The scheduler's goal is to assign tasks to worker nodes in such a way that:

1.  **Each task is assigned to exactly one worker node.**
2.  **A worker node can execute tasks sequentially, one after another.**
3.  **The makespan (the maximum completion time among all worker nodes) is minimized.**
4.  **The number of tasks that miss their deadlines is minimized. In case of ties in makespan, prioritize minimizing deadline misses.**

**Input:**

The input consists of two parts:

*   `n`: The number of worker nodes (integer).
*   `tasks`: A list of `m` tasks, where each task is represented as a tuple `(t_i, d_i)`:
    *   `t_i`: The processing time of task `i` (integer).
    *   `d_i`: The deadline of task `i` (integer).

**Output:**

Return a list of `m` integers, where the `i`-th integer represents the worker node (numbered from `0` to `n-1`) assigned to the `i`-th task. The assignment should be optimal according to the criteria described above.

**Constraints:**

*   `1 <= n <= 10`
*   `1 <= m <= 1000`
*   `1 <= t_i <= 100`
*   `1 <= d_i <= 10000`

**Optimization Requirements:**

*   The solution must be efficient enough to handle the given constraints. Brute-force approaches will likely time out.
*   Consider the trade-offs between makespan and deadline misses when designing your scheduling algorithm.

**Edge Cases and Considerations:**

*   What happens if it's impossible to meet all deadlines? How do you prioritize which deadlines to miss?
*   How does the algorithm behave when `n` is small compared to `m`?
*   How does the algorithm behave when all tasks have very tight deadlines?
*   How does the algorithm behave when all tasks have identical deadlines?
*   The processing time and deadline are not related; it is possible to have a short task with a very early deadline, or a long task with a distant deadline.

**Example:**

```
n = 2
tasks = [(50, 100), (40, 120), (30, 150), (20, 200)]

Possible Optimal Output:
[0, 1, 0, 1]
```

In this example, one possible optimal assignment is to assign tasks 0 and 2 to worker 0, and tasks 1 and 3 to worker 1. The makespan would be `max(50+30, 40+20) = 80`.  The number of missed deadlines would depend on the actual execution order on each worker, and the algorithm should aim to minimize those misses.  A different assignment might achieve the same makespan, but with a different (perhaps higher) number of missed deadlines, and would therefore not be considered optimal.
