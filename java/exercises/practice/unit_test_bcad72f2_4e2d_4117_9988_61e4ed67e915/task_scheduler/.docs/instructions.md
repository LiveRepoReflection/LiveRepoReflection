## Problem: Distributed Task Scheduling with Resource Constraints

### Question Description

You are designing a distributed task scheduling system. The system comprises a cluster of worker nodes, each with varying resource capacities (CPU, Memory, Disk). A set of tasks needs to be scheduled across these workers. Each task has specific resource requirements and dependencies on other tasks.

**Objective:**

Implement a task scheduler that optimally assigns tasks to worker nodes, minimizing the overall completion time (makespan) while adhering to resource constraints and task dependencies.

**Input:**

1.  **Worker Nodes:** A list of `WorkerNode` objects. Each `WorkerNode` has the following attributes:
    *   `id`: Unique identifier (String).
    *   `cpuCapacity`: Available CPU units (integer).
    *   `memoryCapacity`: Available Memory units (integer).
    *   `diskCapacity`: Available Disk units (integer).

2.  **Tasks:** A list of `Task` objects. Each `Task` has the following attributes:
    *   `id`: Unique identifier (String).
    *   `cpuRequirement`: Required CPU units (integer).
    *   `memoryRequirement`: Required Memory units (integer).
    *   `diskRequirement`: Required Disk units (integer).
    *   `dependencies`: A set of `Task` IDs that must be completed before this task can start (Set<String>).
    *   `estimatedRunTime`: Estimated run time in seconds (integer).

**Output:**

A `Schedule` object representing the optimal task assignment. The `Schedule` object should contain:

*   A mapping of `Task` ID to `WorkerNode` ID, indicating which task is assigned to which worker (Map<String, String>).
*   The makespan of the schedule, i.e., the total time it takes to complete all tasks (integer, in seconds). If no valid schedule is possible, return -1.

**Constraints and Considerations:**

1.  **Resource Constraints:** A worker node can only execute a task if it has sufficient CPU, Memory, and Disk resources available. Resources are consumed for the duration of task execution.

2.  **Dependency Constraints:** A task can only be scheduled to start *after* all its dependencies have been completed.

3.  **Optimization Goal:** The primary objective is to minimize the makespan of the schedule.

4.  **Scalability:** The system should be able to handle a large number of tasks (up to 10,000) and worker nodes (up to 100).

5.  **Valid Schedule:** Return a valid schedule only, meaning that all constrains must be satisfied.

6.  **Tie-Breaking:** In case of multiple possible schedules with the same makespan, any valid schedule is acceptable.

7.  **No Preemption:** Once a task is assigned to a worker and starts execution, it cannot be preempted or migrated to another worker.

8.  **Real-World Simulation:** The `estimatedRunTime` is an *estimate*. The actual run time may vary. Assume that the actual run time does not affect the precomputed schedule. The scheduler must create an optimized schedule based on the estimated time, ignoring the case where actual time differs.

**Classes (Provide the following class definitions):**

```java
class WorkerNode {
    String id;
    int cpuCapacity;
    int memoryCapacity;
    int diskCapacity;
    // Constructor, Getters, etc.
}

class Task {
    String id;
    int cpuRequirement;
    int memoryRequirement;
    int diskRequirement;
    Set<String> dependencies;
    int estimatedRunTime;
    // Constructor, Getters, etc.
}

class Schedule {
    Map<String, String> taskAssignments; // Task ID -> Worker Node ID
    int makespan;
    // Constructor, Getters, etc.
}

class TaskScheduler {
    public Schedule scheduleTasks(List<WorkerNode> workerNodes, List<Task> tasks) {
        // Implementation goes here
    }
}
```

**Example:**

(Simplified for brevity)

Worker Nodes:

*   Worker1 (CPU: 4, Memory: 8, Disk: 10)
*   Worker2 (CPU: 2, Memory: 4, Disk: 5)

Tasks:

*   TaskA (CPU: 2, Memory: 4, Disk: 5, Dependencies: {}, Runtime: 10)
*   TaskB (CPU: 1, Memory: 2, Disk: 2, Dependencies: {TaskA}, Runtime: 5)
*   TaskC (CPU: 1, Memory: 2, Disk: 3, Dependencies: {}, Runtime: 8)

Possible Schedule:

*   TaskA -> Worker1
*   TaskB -> Worker2
*   TaskC -> Worker2

Makespan: 15 (TaskA runs for 10 on Worker1. TaskC runs for 8 on Worker2, then TaskB runs for 5 on Worker2, hence 8+5 =13.  Max(10, 13) is not equal to 13. The final makespan is the max of when all tasks are complete. TaskC needs to complete before TaskB can run.)

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   Correctness: Does the scheduler produce valid schedules that satisfy all constraints?
*   Optimality: Does the scheduler effectively minimize the makespan?
*   Efficiency: Is the scheduling algorithm efficient enough to handle large input sizes within a reasonable time limit?
*   Code Quality: Is the code well-structured, readable, and maintainable?

This problem is designed to be challenging and requires careful consideration of resource constraints, task dependencies, and optimization strategies. Good luck!
