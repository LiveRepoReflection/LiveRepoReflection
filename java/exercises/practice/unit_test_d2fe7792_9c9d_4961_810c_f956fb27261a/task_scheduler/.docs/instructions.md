## Project Name

`DistributedTaskScheduler`

## Question Description

You are tasked with designing and implementing a distributed task scheduler. This scheduler needs to manage and execute tasks across a cluster of worker nodes, ensuring efficient resource utilization, fault tolerance, and scalability.

**Scenario:** Imagine a large-scale data processing pipeline where numerous independent tasks need to be executed. These tasks might involve data transformation, model training, or any other computationally intensive operation. You have a cluster of machines (worker nodes) available to execute these tasks.

**Requirements:**

1.  **Task Submission:** Implement a mechanism for submitting tasks to the scheduler. Each task is defined by:

    *   A unique task ID (String).
    *   A resource requirement (CPU cores, Memory in MB) represented by a `Resource` object.
    *   An execution command (String) - the actual command to run on the worker node.  Assume this command can be executed directly by the operating system of the worker node.
    *   Dependencies: A list of task IDs that must complete successfully before this task can start.

2.  **Resource Management:** The scheduler must track the available resources on each worker node. It should intelligently assign tasks to worker nodes based on their resource requirements and availability, avoiding over-allocation. Worker nodes report their resources to the scheduler upon joining the cluster and update the scheduler when a task completes.

3.  **Task Scheduling:** The scheduler must prioritize tasks based on a configurable priority. Tasks with higher priority should be scheduled before those with lower priority, given that resources are available and dependencies are met. If tasks have the same priority, schedule based on FIFO.

4.  **Dependency Management:** The scheduler must ensure that tasks are only executed after all their dependencies have been successfully completed. Implement a robust dependency tracking mechanism.

5.  **Fault Tolerance:** If a worker node fails during task execution, the scheduler must detect the failure, reschedule the incomplete task on a different available worker node (if possible, and resources allow), and notify relevant parties (e.g., logging, alerting).  The number of retries for a given task is limited to a configurable `maxRetries` value.

6.  **Scalability:** The scheduler should be designed to handle a large number of tasks and worker nodes. Consider data structures and algorithms that can scale efficiently.

7.  **Concurrency:** All operations must be thread-safe to ensure concurrent access from multiple clients and worker nodes.

8.  **Monitoring:** Provide mechanisms for monitoring the status of tasks and worker nodes. This could include methods to retrieve task status (PENDING, RUNNING, COMPLETED, FAILED), worker node availability, and resource utilization.

**Constraints:**

*   Worker nodes are homogeneous in terms of their OS.
*   Assume basic communication infrastructure exists between the scheduler and worker nodes (e.g., TCP/IP). You don't need to implement the actual networking layer.  Focus on the scheduling logic.
*   You do **not** need to implement persistence (saving scheduler state to disk). The scheduler can be in-memory only.
*   Minimize external library dependencies.  Focus on core Java data structures and concurrency constructs.  Using lightweight thread pools is acceptable.
*   The scheduler must handle potential deadlocks caused by circular task dependencies gracefully.  Detect and report such situations instead of hanging indefinitely.

**Bonus Challenges:**

*   Implement preemption: Allow higher-priority tasks to preempt (interrupt) lower-priority tasks that are currently running, freeing up resources for the higher-priority tasks. The preempted task should be rescheduled.
*   Implement a task placement strategy that considers data locality (if tasks operate on data stored on specific worker nodes).
*   Develop a simple web-based UI to monitor the scheduler's status.

This problem requires a strong understanding of data structures, algorithms, concurrency, and distributed systems principles. The focus should be on designing a robust, efficient, and scalable task scheduler that can handle various real-world scenarios. Optimizing for resource usage and implementing a clean, maintainable codebase are key.
