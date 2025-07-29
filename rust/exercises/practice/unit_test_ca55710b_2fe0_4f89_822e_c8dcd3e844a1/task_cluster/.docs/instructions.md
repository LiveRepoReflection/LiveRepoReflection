## Project Name

`Distributed Task Scheduler`

## Question Description

You are tasked with designing and implementing a distributed task scheduler. This scheduler needs to handle a large number of independent tasks, distribute them across a cluster of worker nodes, and ensure that all tasks are eventually executed, even in the face of node failures.

**Core Requirements:**

1.  **Task Submission:** The scheduler must accept tasks for execution. Each task is represented by a unique ID and a command to be executed on a worker node.  Tasks are idempotent -- running the same task twice should have the same effect as running it once.

2.  **Task Distribution:** The scheduler must distribute tasks across available worker nodes in the cluster.  The distribution algorithm should aim for fairness and load balancing, avoiding overloading any single worker.

3.  **Fault Tolerance:** The system must be resilient to worker node failures. If a worker node fails while executing a task, the scheduler must detect the failure and re-schedule the affected task on another available worker node. Task retries should be limited to prevent indefinite looping.

4.  **Task Completion Tracking:** The scheduler must track the status of each task (pending, in progress, completed, failed).  It must provide a mechanism to query the status of a specific task by its ID.

5.  **Worker Node Management:** The scheduler must be able to register new worker nodes joining the cluster and deregister nodes leaving the cluster (either gracefully or due to failure).

6. **Scalability:** The system should be able to handle a large number of tasks and worker nodes. Consider the trade-offs between different approaches to task distribution, fault tolerance, and task status tracking to ensure scalability.

**Constraints and Considerations:**

*   **Communication:**  Worker nodes communicate with the scheduler over a network. You can assume a reliable but potentially high-latency network connection.  Consider using message queues (e.g., Redis Pub/Sub, RabbitMQ) for asynchronous communication between the scheduler and workers.
*   **Concurrency:** The scheduler must handle multiple concurrent task submissions and worker node updates. Use appropriate concurrency primitives to ensure data consistency and avoid race conditions.
*   **Resource Limits:** Assume each worker node has limited CPU and memory resources.  The scheduler should avoid assigning too many tasks to a single worker node, leading to resource exhaustion.
*   **Ordering:** The tasks do not have dependencies on each other, and their execution order is not important.
*   **Idempotency:** Tasks are guaranteed to be idempotent.
*   **Task Execution:** You do not need to implement the actual task execution on the worker nodes (e.g., using `std::process::Command`). You only need to simulate it with a delay. Assume each task, on average, takes 1-10 seconds to execute.
*   **Retry Limit:** Each task can be retried at most 3 times. After 3 failures, the task should be marked as "failed."
*   **Cluster Size:** The number of worker nodes can range from 1 to 100.
*   **Task Volume:** The system should be able to handle up to 1,000,000 tasks submitted over a period of 24 hours.

**Optimization Requirements:**

*   **Minimizing Task Completion Time:**  The primary goal is to minimize the overall time required to complete all submitted tasks.  Consider strategies for efficient task distribution and fault recovery.
*   **Resource Utilization:**  The system should strive to maximize the utilization of available worker node resources (CPU, memory) without overloading any individual node.

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** Does the scheduler correctly distribute tasks, handle failures, and track task status?
*   **Performance:** How quickly does the scheduler complete a large batch of tasks?
*   **Scalability:** How well does the scheduler handle a large number of tasks and worker nodes?
*   **Fault Tolerance:** How resilient is the scheduler to worker node failures?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Concurrency Safety:** Are appropriate concurrency primitives used to ensure data consistency and avoid race conditions?

This problem requires a strong understanding of distributed systems concepts, concurrency, and data structures. You will need to make informed design decisions to balance performance, scalability, and fault tolerance. Good luck!
