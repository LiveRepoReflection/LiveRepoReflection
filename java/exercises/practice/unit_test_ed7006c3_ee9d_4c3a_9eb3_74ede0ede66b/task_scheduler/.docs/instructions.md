## Question Title:  Scalable Distributed Task Scheduler

### Question Description

You are tasked with designing and implementing a scalable distributed task scheduler.  Imagine a system where numerous clients submit tasks to be executed on a cluster of worker nodes. The scheduler's responsibility is to efficiently manage and distribute these tasks to available workers, ensuring optimal resource utilization and meeting specific Quality of Service (QoS) requirements.

**Core Requirements:**

1.  **Task Submission:** Clients can submit tasks to the scheduler. Each task is defined by:
    *   `task_id`: A unique identifier for the task (String).
    *   `priority`: An integer representing the task's priority (higher value indicates higher priority).
    *   `resource_requirements`: A map specifying the resources required by the task (e.g., CPU cores, memory in GB, disk space in GB).  This map will use String for resource name and Integer for required amount.  Example: `{"CPU": 2, "Memory": 4, "Disk": 10}`.
    *   `estimated_execution_time`: An estimate of the task's execution time in seconds (Integer).
    *   `client_id`: An identifier for the client that submitted the task (String).

2.  **Worker Node Registration:** Worker nodes register with the scheduler, providing information about their available resources. Each worker node is defined by:
    *   `worker_id`: A unique identifier for the worker node (String).
    *   `available_resources`: A map specifying the resources available on the worker node (similar format to `resource_requirements`).  Example: `{"CPU": 8, "Memory": 16, "Disk": 100}`.
    *   `heartbeat_interval`:  The frequency (in seconds) at which the worker sends a heartbeat to the scheduler (Integer).

3.  **Task Scheduling:** The scheduler should assign tasks to worker nodes based on the following criteria:
    *   **Resource Availability:** A task can only be assigned to a worker if the worker has sufficient available resources to meet the task's requirements.
    *   **Priority:** Higher-priority tasks should be scheduled before lower-priority tasks.
    *   **Fairness:**  The scheduler should strive for fairness among clients.  No single client should monopolize the cluster resources.  A possible implementation is to limit the maximum number of concurrent tasks from each client on the cluster.
    *   **Locality (Optional, but highly encouraged):** If a client has recently executed tasks on a specific worker node, the scheduler should attempt to schedule subsequent tasks from the same client on that worker node (assuming resource availability). This simulates data locality and can improve performance in real-world scenarios.

4.  **Task Execution Monitoring:** The scheduler should monitor the execution status of tasks on worker nodes.  Worker nodes periodically report the status of their assigned tasks. Possible task states include: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`.

5.  **Fault Tolerance:** The scheduler must be fault-tolerant. If a worker node fails (e.g., stops sending heartbeats), the scheduler should detect this failure and reschedule any tasks that were running on the failed worker node.

6.  **Scalability:** The scheduler must be able to handle a large number of tasks and worker nodes.  Consider the data structures and algorithms used to ensure efficient performance as the system scales. Focus on efficient lookups and updates to the task and worker state.

7.  **Concurrency:**  The scheduler must handle concurrent task submissions and worker node registrations.

**Constraints and Edge Cases:**

*   The number of tasks and worker nodes can be very large (millions).
*   Tasks can have varying resource requirements and execution times.
*   Worker nodes can have heterogeneous resource configurations.
*   Network latency between the scheduler and worker nodes can be significant.
*   Worker nodes can fail unexpectedly.
*   Task priorities can change dynamically (although you don't need to implement the dynamic update of priority, just consider it).
*   Consider potential deadlocks and race conditions in your design.
*   The scheduler should be able to gracefully handle resource contention.  If no worker node has sufficient resources to run a task, the task should remain in a `QUEUED` state until resources become available.
*   Clients may submit identical task IDs. How should the scheduler handle this? (e.g., reject the duplicate, overwrite the existing task, queue multiple instances). Clearly document your design decision.

**Deliverables:**

1.  **Code:**  Implement the core components of the distributed task scheduler in Java. Focus on the scheduling logic, resource management, fault tolerance, and scalability.
2.  **Design Document:**  Provide a document that describes your design, including:
    *   Data structures used to store task and worker node information.  Justify your choices.
    *   Algorithms used for task scheduling and resource allocation.  Justify your choices.
    *   How you address fault tolerance, scalability, and concurrency.
    *   Trade-offs you made in your design.
    *   Potential areas for future improvement.
    *   How you handle edge cases and constraints.

**Evaluation Criteria:**

*   **Correctness:** The scheduler correctly assigns tasks to worker nodes based on resource availability, priority, and fairness.
*   **Efficiency:** The scheduler efficiently manages resources and minimizes task completion time.
*   **Scalability:** The scheduler can handle a large number of tasks and worker nodes without performance degradation.
*   **Fault Tolerance:** The scheduler can recover from worker node failures without losing tasks.
*   **Code Quality:** The code is well-structured, documented, and easy to understand.
*   **Design Document:** The design document is clear, comprehensive, and justifies the design choices.
*   **Handling of Edge Cases and Constraints:** The scheduler gracefully handles edge cases and constraints.

This problem requires a strong understanding of data structures, algorithms, distributed systems concepts, and concurrency. Good luck!
