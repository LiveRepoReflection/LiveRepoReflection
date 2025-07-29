## Problem: Distributed Task Scheduler

**Question Description:**

You are tasked with building a distributed task scheduler in JavaScript. The scheduler must manage a large number of tasks across a cluster of worker nodes. Each task has a unique ID, a priority, a deadline (timestamp), and a function to execute. Worker nodes have limited processing capacity and can only execute one task at a time.

The scheduler needs to efficiently distribute tasks to available worker nodes, considering the following factors:

1.  **Priority:** Higher priority tasks should be executed before lower priority tasks.
2.  **Deadline:** Tasks with earlier deadlines should be prioritized.
3.  **Worker Availability:** The scheduler should assign tasks to available workers, minimizing idle time.
4.  **Fault Tolerance:** The scheduler should be resilient to worker node failures. If a worker node fails while executing a task, the task should be automatically re-scheduled to another available worker.
5.  **Scalability:** The scheduler should be able to handle a large number of tasks and worker nodes.
6.  **Optimality:** The scheduler should aim to minimize the overall completion time for all tasks.

**Input:**

*   A stream of task objects. Each task object has the following properties:
    *   `taskId`: (string) A unique identifier for the task.
    *   `priority`: (number) A numerical value representing the task's priority (higher value = higher priority).
    *   `deadline`: (number) A timestamp representing the task's deadline (milliseconds since epoch).
    *   `execute`: (function) A function that performs the task's work. The function can return a Promise to represent asynchronous operations.
*   A list of worker node IDs.

**Output:**

The scheduler should continuously monitor the task stream and worker node availability. When a worker node becomes available, the scheduler should select the next task to execute based on the priority, deadline, and availability constraints. The scheduler should log the start and completion of each task on each worker node. If a task fails, it should be retried on a different worker. The scheduler does not need to return any specific value, but it should demonstrate that it can efficiently manage and execute tasks in a distributed environment.

**Constraints:**

*   The number of tasks can be very large (millions).
*   The number of worker nodes can be large (hundreds or thousands).
*   Tasks can have varying execution times (from milliseconds to minutes).
*   Worker nodes can fail at any time.
*   The scheduler should be optimized for performance and scalability.
*   The scheduler should handle task failures gracefully.
*   You must implement a mechanism to detect task failure and reschedule tasks.
*   Assume worker nodes are stateless and can execute any task.

**Requirements:**

*   Implement the core scheduling logic.
*   Implement task prioritization based on priority and deadline.
*   Implement worker node failure detection and task rescheduling.
*   Demonstrate scalability by simulating a large number of tasks and worker nodes.
*   Optimize the scheduling algorithm for minimal overall completion time.
*   Provide clear and concise code with appropriate comments.
*   Consider using appropriate data structures and algorithms to optimize performance (e.g., priority queues, heaps, graphs).
*   Consider using asynchronous programming techniques (e.g., Promises, async/await) to handle concurrent task execution.
*   The solution should be written in Javascript.

**Bonus:**

*   Implement a mechanism to track task progress and provide real-time status updates.
*   Implement a load balancing strategy to distribute tasks evenly across worker nodes.
*   Implement a task dependency system, where tasks can depend on the completion of other tasks.
*   Provide a visualization of the task scheduling process.
