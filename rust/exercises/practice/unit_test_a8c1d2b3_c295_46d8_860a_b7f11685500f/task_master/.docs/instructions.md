Okay, here's a challenging Rust coding problem designed to test a range of skills.

## Project Name

```
DistributedTaskScheduler
```

## Question Description

You are tasked with designing and implementing a distributed task scheduler. This scheduler will be responsible for receiving tasks, distributing them across a cluster of worker nodes, monitoring their execution, and handling failures gracefully.  The core components are a central scheduler and multiple worker nodes.

**Detailed Requirements:**

1.  **Task Definition:** A task is defined as a self-contained, independent unit of work represented by a string.  The scheduler does not interpret the content of the string; it simply needs to distribute it to a worker.  Tasks have unique IDs (UUIDv4). Tasks also have a priority assigned to them upon submission.

2.  **Scheduler:** The scheduler is a single process that acts as the central coordinator.  It should:
    *   Accept new tasks with priorities. Higher numerical values indicate higher priority (e.g., 10 is higher priority than 1).
    *   Store tasks in a prioritized queue. This queue determines the order in which tasks are assigned to workers.
    *   Distribute tasks to available workers in a fair manner, prioritizing tasks based on their priority.  Fairness means attempting to distribute tasks evenly across all available workers.
    *   Track the status of each task (Pending, Running, Completed, Failed).
    *   Handle worker failures. If a worker fails, the scheduler should re-queue the tasks that were assigned to that worker, maintaining their original priority.
    *   Expose an API (you define the format – could be a simple CLI, HTTP endpoint, etc.) to submit new tasks. It should also expose an API to query the status of a task by its ID.
    *   The number of workers can vary over time (workers can join or leave the cluster).
    *   The scheduler itself must be resilient to restarts, meaning that it should persist the queue of tasks and be able to restore it when it restarts.

3.  **Worker Node:** Worker nodes are independent processes that execute tasks.  Each worker node should:
    *   Register itself with the scheduler upon startup.
    *   Continuously poll the scheduler for new tasks.
    *   Execute the tasks it receives. Simulating task execution is sufficient (e.g., a `thread::sleep` for a duration derived from the task string's hash).
    *   Report the completion status (Completed or Failed) of each task back to the scheduler.  A task can fail due to arbitrary reasons (e.g., the simulated execution detects a problem).
    *   Each worker has a limited capacity to handle tasks concurrently.

4.  **Communication:** You must define a communication mechanism between the scheduler and worker nodes. Consider using message queues (e.g., RabbitMQ, Redis Pub/Sub), gRPC, or other suitable inter-process communication (IPC) methods available in Rust.

5.  **Concurrency:** The scheduler and worker nodes must be highly concurrent to handle multiple tasks and workers efficiently.  Use Rust's concurrency primitives (e.g., `async/await`, `channels`, `Mutex`, `RwLock`) appropriately.

6.  **Error Handling:** Implement robust error handling to gracefully handle unexpected situations such as network errors, worker failures, and invalid task submissions.

7.  **Optimization:** The scheduler should be optimized for throughput and latency. Consider strategies for minimizing task assignment delays and maximizing worker utilization.

**Constraints:**

*   The number of worker nodes can range from 1 to 100.
*   The scheduler should be able to handle a sustained load of 1000+ tasks per second.
*   Task strings can be up to 1MB in size.
*   Worker nodes have a maximum concurrent task capacity of 10.
*   Persisted data should be recoverable even in the event of a system crash.
*   The system must be able to handle tasks with widely varying execution times (from milliseconds to several minutes).

**Bonus Challenges:**

*   Implement task prioritization preemption: Higher priority tasks can interrupt lower priority tasks running on workers (requires a mechanism to pause and resume tasks, which can be simulated).
*   Add support for task dependencies: Tasks can depend on the completion of other tasks before they can be executed.
*   Implement autoscaling: Dynamically adjust the number of worker nodes based on the task load.
*   Provide metrics and monitoring: Expose metrics about task throughput, latency, and worker utilization.
*   Implement a web-based UI to monitor the system's status and submit tasks.

This problem requires a solid understanding of concurrency, distributed systems design, and Rust's ecosystem. Good luck!
