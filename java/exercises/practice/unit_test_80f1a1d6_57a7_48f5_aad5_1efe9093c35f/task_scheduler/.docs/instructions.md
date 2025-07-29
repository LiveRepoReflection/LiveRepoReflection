## Question: Distributed Task Scheduler with Resource Constraints

### Question Description

You are tasked with designing a distributed task scheduler for a high-performance computing cluster. The cluster consists of multiple worker nodes, each with varying amounts of CPU cores, memory, and GPU resources.  A user submits a series of tasks to the scheduler, where each task requires a specific amount of CPU cores, memory, GPU and execution time. The goal is to schedule these tasks across the worker nodes to minimize the overall makespan (the time when the last task finishes execution).

**Input:**

1.  **Worker Nodes:** A list of worker nodes, where each node is defined by its available CPU cores, memory (in GB), and GPU count. For example:
    `List<Node> nodes = List.of(new Node(8, 32, 1), new Node(16, 64, 2), new Node(4, 16, 0));`

2.  **Tasks:** A list of tasks, where each task is defined by its CPU core requirement, memory requirement (in GB), GPU requirement, and estimated execution time (in seconds). For example:
    `List<Task> tasks = List.of(new Task(2, 8, 0, 60), new Task(4, 16, 1, 120), new Task(1, 4, 0, 30), new Task(8, 32, 1, 240));`

3.  **Precedence Constraints:** A list of dependencies between tasks. This is represented as a list of pairs `(taskA, taskB)`, indicating that `taskB` cannot start execution until `taskA` has completed. For example:
    `List<Pair<Task, Task>> dependencies = List.of(new Pair<>(tasks.get(0), tasks.get(1)), new Pair<>(tasks.get(2), tasks.get(3)));`

**Output:**

A schedule that minimizes the makespan.  The schedule should be represented as a `Map<Task, Assignment>`, where each `Task` is mapped to an `Assignment` object containing the `Node` on which the task is executed and the start time (in seconds) of the task's execution.

**Constraints and Requirements:**

1.  **Resource Constraints:** A task can only be assigned to a node if the node has sufficient CPU cores, memory, and GPU resources available at the task's scheduled start time. Resources are released back to the node once the task completes execution.
2.  **Precedence Constraints:** All precedence constraints must be respected. A task cannot start until all its dependencies are completed.
3.  **Optimization Goal:** Minimize the makespan (the time when the last task finishes).
4.  **Scalability:** The solution should be reasonably efficient for a large number of tasks (up to 1000) and worker nodes (up to 100).
5.  **Real-time Scheduling Considerations:** While not a strict real-time system, the scheduling algorithm should aim to produce a schedule within a reasonable time (e.g., under 1 minute for 1000 tasks and 100 nodes).
6.  **Tie-breaking:** If multiple nodes can accommodate a task, prioritize nodes with lower utilization to balance the load across the cluster.  You can define utilization as the percentage of CPU cores currently in use.
7.  **Handling of Unfeasible Schedules:** If it is impossible to schedule all tasks given the resource constraints and precedence constraints, the algorithm should throw an exception indicating that a feasible schedule cannot be found.

**Classes Definition (Example):**

```java
class Node {
    int cpuCores;
    int memoryGB;
    int gpuCount;

    public Node(int cpuCores, int memoryGB, int gpuCount) {
        this.cpuCores = cpuCores;
        this.memoryGB = memoryGB;
        this.gpuCount = gpuCount;
    }
    // Add getter for cpuCores, memoryGB, gpuCount
    public int getCpuCores() { return cpuCores; }
    public int getMemoryGB() { return memoryGB; }
    public int getGpuCount() { return gpuCount; }
}

class Task {
    int cpuCoresRequired;
    int memoryGBRequired;
    int gpuCountRequired;
    int executionTimeSeconds;

    public Task(int cpuCoresRequired, int memoryGBRequired, int gpuCountRequired, int executionTimeSeconds) {
        this.cpuCoresRequired = cpuCoresRequired;
        this.memoryGBRequired = memoryGBRequired;
        this.gpuCountRequired = gpuCountRequired;
        this.executionTimeSeconds = executionTimeSeconds;
    }
    // Add getter for cpuCoresRequired, memoryGBRequired, gpuCountRequired, executionTimeSeconds
    public int getCpuCoresRequired() { return cpuCoresRequired; }
    public int getMemoryGBRequired() { return memoryGBRequired; }
    public int getGpuCountRequired() { return gpuCountRequired; }
    public int getExecutionTimeSeconds() { return executionTimeSeconds; }
}

class Assignment {
    Node node;
    int startTimeSeconds;

    public Assignment(Node node, int startTimeSeconds) {
        this.node = node;
        this.startTimeSeconds = startTimeSeconds;
    }
    // Add getter for node, startTimeSeconds
    public Node getNode() { return node; }
    public int getStartTimeSeconds() { return startTimeSeconds; }
}

class Pair<T, U> {
    T first;
    U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }
    // Add getter for first, second
    public T getFirst() { return first; }
    public U getSecond() { return second; }
}
```

**Evaluation Criteria:**

*   Correctness: The schedule must satisfy all resource and precedence constraints.
*   Makespan: The lower the makespan, the better.
*   Efficiency: The algorithm should be reasonably efficient for large input sizes.
*   Code Quality: The code should be well-structured, readable, and maintainable.

**Hints:**

*   Consider using data structures like priority queues to efficiently manage tasks and available nodes.
*   Explore different scheduling algorithms, such as list scheduling, earliest start time (EST), or genetic algorithms.
*   Be mindful of the time complexity of your solution.

This problem requires a combination of algorithm design, data structure knowledge, and optimization techniques, making it a challenging and sophisticated problem suitable for a high-level programming competition. Good luck!
