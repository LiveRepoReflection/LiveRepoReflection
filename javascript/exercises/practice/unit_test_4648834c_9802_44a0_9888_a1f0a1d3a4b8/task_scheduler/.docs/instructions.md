Okay, here's a hard-level JavaScript coding problem description, focusing on algorithmic efficiency and dealing with a complex, real-world scenario.

## Project Name

`DistributedTaskScheduler`

## Question Description

You are tasked with building a distributed task scheduler for a large-scale data processing system. This system comprises numerous worker nodes, each with varying computational capabilities and network latencies.  The scheduler's role is to efficiently assign tasks to these workers, minimizing the overall completion time (makespan) of a set of independent tasks.

Specifically, you are given the following:

*   **`tasks`**: An array of task objects. Each task object has a `duration` property, representing the estimated processing time required to complete the task on a "standard" worker node.  Assume all tasks are independent and can be executed in any order. `tasks` can have a length of up to `10^5`. The `duration` can be up to `10^3`.
*   **`workers`**: An array of worker node objects. Each worker object has a `speed` property, representing its relative processing speed compared to a "standard" worker. A worker with `speed: 2` will complete a task in half the time compared to a standard worker. Each worker also has a `location` property, representing the geographical location of the worker. `workers` can have a length of up to `10^3`. The `speed` can be up to `10^2`.
*   **`networkLatency`**: A function `networkLatency(location1, location2)` that returns the network latency (in milliseconds) between two geographical locations. This function is computationally expensive and should be called sparingly. Consider the real number return value will be up to `10^2`.
*   **`deadline`**: A time, in milliseconds, by which all tasks *must* be completed. If the scheduler cannot find an assignment to complete all tasks by this deadline, it should return `null`.

Your scheduler must:

1.  **Assign each task to *exactly one* worker.**
2.  **Minimize the makespan (the time when the last task completes).**
3.  **Account for both processing time *and* network latency.** Assume that a task's data must be transferred to the worker *before* processing can begin, and the result must be transferred back to a central location (the scheduler). You can assume the scheduler's location is "origin". The total time for a task is: `networkLatency("origin", worker.location) + (task.duration / worker.speed) + networkLatency(worker.location, "origin")`
4.  **Meet the specified `deadline`.**

**Constraints and Considerations:**

*   **Scale:** The number of tasks and workers can be quite large, requiring efficient algorithms and data structures.
*   **Optimization:** Finding the absolute optimal assignment is likely NP-hard.  Focus on developing a good heuristic that provides a near-optimal solution within a reasonable time.
*   **Heuristic vs. Exact:** You are not required to find the mathematically perfect solution. A well-reasoned and implemented heuristic algorithm is acceptable. Explain your choice of heuristic and its rationale in comments.
*   **Network Latency Cost:** The `networkLatency` function is expensive. Minimize the number of calls to this function.  Consider caching results.
*   **Tie-breaking:** If multiple workers are equally suitable for a task, define a consistent tie-breaking mechanism (e.g., worker ID).
*   **Real-World Concerns:** Consider real-world limitations. Task preemption or worker failures are *not* within the scope of this problem.
*   **Edge Cases:** Handle edge cases such as empty task lists, empty worker lists, and tasks with zero duration.

**Output:**

The function should return an object representing the task assignment. The object should have the following structure:

```javascript
{
  makespan: <number>, // The makespan of the assignment.
  assignments: {
    <taskId>: <workerId>, // Task ID (index in the `tasks` array) to Worker ID (index in the `workers` array) mapping.
    // ... other task assignments
  }
}
```

If a valid assignment cannot be found within the deadline, return `null`.

Good luck! This will require careful algorithm selection, implementation, and optimization.
