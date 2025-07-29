## Project Name

**Distributed Task Scheduler**

## Question Description

Design and implement a distributed task scheduler. This system should allow users to submit tasks, schedule them for execution on a cluster of worker nodes, and monitor their progress. Focus on scalability, reliability, and fault tolerance.

**Detailed Requirements:**

1.  **Task Submission:**
    *   Users can submit tasks with associated metadata, including:
        *   A unique task ID.
        *   A command to execute (e.g., a shell script or executable).
        *   Resource requirements (CPU, memory, disk space).
        *   Dependencies on other tasks (a task should only execute after its dependencies are completed successfully).
        *   Priority (tasks with higher priority should be scheduled first).
        *   Maximum execution time.
    *   The scheduler should validate task submissions and reject invalid tasks.

2.  **Task Scheduling:**
    *   The scheduler must efficiently assign tasks to available worker nodes, considering:
        *   Resource availability on each node.
        *   Task dependencies.
        *   Task priority.
        *   Data locality (if applicable, try to schedule tasks on nodes where the required data is already located).
    *   Implement a scheduling algorithm that balances load across the cluster and minimizes task completion time. At least two scheduling algorithms should be implemented, and the system should allow switching between them (e.g., First-Come, First-Served, Priority Scheduling, Shortest Job First).
    *   The scheduler should handle task preemption and rescheduling in case of node failures or resource contention.

3.  **Worker Node Management:**
    *   Worker nodes register with the scheduler upon startup and periodically report their status (CPU usage, memory usage, available disk space, etc.).
    *   The scheduler maintains a real-time view of the cluster's resources and node availability.
    *   The scheduler should detect and handle node failures gracefully, rescheduling tasks that were running on the failed nodes.

4.  **Task Monitoring:**
    *   Users can query the status of submitted tasks (pending, running, completed, failed).
    *   The scheduler provides detailed information about each task, including:
        *   Start time, end time, execution time.
        *   The worker node on which the task is running/ran.
        *   Resource usage (CPU, memory, disk I/O).
        *   Standard output and standard error.
    *   Implement a mechanism for real-time monitoring of task progress (e.g., using web sockets or server-sent events).

5.  **Fault Tolerance:**
    *   The scheduler should be resilient to failures of worker nodes and the scheduler itself.
    *   Implement mechanisms for:
        *   Task checkpointing (periodically save the state of a running task to disk so it can be resumed from the last checkpoint in case of failure).
        *   Scheduler replication (maintain multiple instances of the scheduler to provide high availability).
        *   Leader election (if using scheduler replication, implement a mechanism for electing a leader among the scheduler instances).

6.  **Scalability:**
    *   The system should be able to handle a large number of tasks and worker nodes.
    *   Consider using distributed data structures and algorithms to ensure scalability.
    *   Implement techniques for load balancing and resource management.

7.  **Concurrency:**
    *   The system should handle concurrent task submissions and status queries efficiently.
    *   Use appropriate locking mechanisms to prevent race conditions and ensure data consistency.

8.  **Optimizations:**
    *   Minimize task scheduling latency.
    *   Maximize resource utilization.
    *   Reduce task completion time.

**Constraints:**

*   The number of worker nodes can be up to 1000.
*   The number of tasks can be up to 1 million.
*   Task execution time can range from seconds to hours.
*   Network latency between nodes can vary.
*   Node failures are possible and should be handled gracefully.
*   The system should be able to handle different types of tasks with varying resource requirements.

**Bonus:**

*   Implement a web-based user interface for task submission and monitoring.
*   Support task prioritization based on user-defined criteria.
*   Implement dynamic resource allocation (tasks can request more resources during execution).
*   Integrate with a cloud-based infrastructure (e.g., AWS, Azure, GCP).
*   Implement a plugin system to support different task execution environments (e.g., Docker, Kubernetes).
