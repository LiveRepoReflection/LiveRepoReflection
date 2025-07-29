## Project Name

`OptimalSchedule`

## Question Description

You are designing a highly efficient task scheduling system for a multi-core processor. You are given a set of `n` tasks, each with a deadline and a CPU core affinity. Your goal is to determine the maximum number of tasks that can be scheduled while respecting all deadlines and core affinities.

**Tasks:**

Each task `i` has the following properties:

*   `deadline[i]`: An integer representing the deadline by which the task must be completed. A task can start executing at time 0 and must finish *no later than* its deadline.
*   `affinity[i]`: An integer representing the CPU core this task *must* run on.

**Constraints:**

*   Only one task can run on a given CPU core at any given time.
*   A task, once started, must run continuously until completion (no preemption). The execution time of each task is assumed to be 1 unit.
*   A task `i` must be executed on the CPU core specified by `affinity[i]`.
*   You have `k` CPU cores, numbered from 0 to `k-1`.

**Input:**

*   `n`: The number of tasks.
*   `k`: The number of CPU cores.
*   `deadline`: A list of integers, where `deadline[i]` is the deadline for task `i`.
*   `affinity`: A list of integers, where `affinity[i]` is the CPU core affinity for task `i`.

**Output:**

An integer representing the maximum number of tasks that can be scheduled while respecting all deadlines and core affinities.

**Example:**

```
n = 5
k = 2
deadline = [2, 2, 3, 4, 4]
affinity = [0, 1, 0, 1, 0]

Output: 5

Explanation:
One possible schedule is:
- Task 0 on core 0 at time 0 (finishes at time 1)
- Task 1 on core 1 at time 0 (finishes at time 1)
- Task 2 on core 0 at time 1 (finishes at time 2)
- Task 3 on core 1 at time 1 (finishes at time 2)
- Task 4 on core 0 at time 2 (finishes at time 3)
```

**Constraints:**

*   `1 <= n <= 1000`
*   `1 <= k <= 100`
*   `1 <= deadline[i] <= 1000` for all `i`
*   `0 <= affinity[i] < k` for all `i`

**Optimization Requirements:**

Your solution should be efficient enough to handle large values of `n` and `k` within a reasonable time limit (e.g., a few seconds). Consider using dynamic programming, greedy algorithms, or other optimization techniques.

**Edge Cases to Consider:**

*   Tasks with the same deadline and affinity.
*   Tasks with very early deadlines.
*   A large number of tasks competing for the same CPU core.
*   Empty input lists.
*   No possible schedule exists.

**Real-world Practical Scenario:**

This problem models a simplified version of real-time scheduling in operating systems, where tasks have deadlines and resource constraints. Efficient scheduling is crucial for meeting performance requirements in embedded systems, robotics, and other time-critical applications.
