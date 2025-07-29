## Question: Asynchronous Distributed Task Scheduler with Resource Management

**Problem Description:**

You are tasked with designing and implementing a simplified asynchronous distributed task scheduler with resource management capabilities. This scheduler will be responsible for receiving task requests, distributing them across a cluster of worker nodes, managing the resources used by these tasks, and handling potential failures gracefully.

**System Overview:**

The system consists of the following components:

1.  **Central Scheduler:** This component receives task requests, maintains a queue of pending tasks, and assigns tasks to available worker nodes based on resource requirements and node availability.
2.  **Worker Nodes:** These are individual machines in the cluster that execute the assigned tasks. Each worker node has a fixed amount of resources (CPU, Memory).
3.  **Task Definition:** Each task is defined by a unique ID, a function to execute, and a resource requirement profile (CPU, Memory). The function is a black box, you just need to execute it.
4.  **Resource Manager:** Tracks the available resources on each worker node and prevents over-allocation.

**Specific Requirements:**

1.  **Asynchronous Task Execution:** Tasks must be executed asynchronously on the worker nodes. The scheduler should not block while waiting for a task to complete.
2.  **Resource Awareness:** The scheduler must consider the resource requirements of each task and the available resources on each worker node before assigning a task.
3.  **Fault Tolerance:** The scheduler must be able to handle worker node failures. If a worker node fails while executing a task, the scheduler should re-queue the task and assign it to another available worker node. There might be a limit on retry count.
4.  **Task Prioritization:** Tasks should be executed based on their priority. Higher priority tasks should be scheduled before lower priority tasks.
5.  **Scalability:** The system should be designed to handle a large number of tasks and worker nodes.
6.  **Deadlock Prevention:** The system should be designed to avoid deadlocks when allocating resources.
7.  **Dynamic Resource Allocation:** Task can have a maximum resource allocation range, and it can use less than it asks for. It should release unused resources when possible.
8.  **Cancellation:** Task can be cancelled before or during the running period. If cancelled, it should be requeued.

**Input:**

*   A stream of task requests. Each task request includes:
    *   `task_id`: A unique identifier for the task (string).
    *   `priority`: An integer representing the priority of the task (higher value = higher priority).
    *   `function`: A function to be executed (assume a function pointer or similar mechanism exists).
    *   `cpu_needed`: Integer representing the CPU cores required by the task.
    *   `memory_needed`: Integer representing the memory (in MB) required by the task.
    *   `max_cpu_needed`: Integer representing the Maximum CPU cores required by the task.
    *   `max_memory_needed`: Integer representing the Maximum memory (in MB) required by the task.

*   A list of worker nodes, each with:
    *   `node_id`: A unique identifier for the worker node (string).
    *   `total_cpu`: Integer representing the total CPU cores available on the worker node.
    *   `total_memory`: Integer representing the total memory (in MB) available on the worker node.

**Output:**

*   The system should log the scheduling decisions, task start/end times, and any failures.
*   Implement a mechanism to query the status of a specific task (e.g., "pending," "running," "completed," "failed").

**Constraints:**

*   The number of worker nodes can be up to 1000.
*   The number of tasks can be very large (millions).
*   Resource requirements for tasks can vary significantly.
*   Tasks should be scheduled and executed as quickly as possible while respecting resource constraints.
*   You can assume that the network communication between the scheduler and worker nodes is reliable (no packet loss).
*   You must use Python.

**Judging Criteria:**

*   Correctness: The system must correctly schedule tasks based on resource requirements and priority.
*   Efficiency: The system must schedule tasks quickly and efficiently, minimizing idle time on worker nodes.
*   Fault Tolerance: The system must handle worker node failures gracefully.
*   Scalability: The system must be able to handle a large number of tasks and worker nodes.
*   Code Quality: The code should be well-structured, documented, and easy to understand.
*   Deadlock handling: Should prevent deadlock cases.
*   Dynamic resource allocation: Efficiently manage resource usage.
*   Cancellation handling: Gracefully handle task cancellations.

**Hints:**

*   Consider using appropriate data structures (e.g., priority queues, heaps, graphs) to manage tasks and worker nodes.
*   Use asynchronous programming techniques (e.g., `asyncio` in Python) to handle task execution and communication.
*   Implement a resource manager component to track resource usage on worker nodes.
*   Use a locking mechanism to prevent race conditions when accessing shared resources.
*   Consider using a distributed consensus algorithm (e.g., Raft) for the central scheduler to ensure high availability. (Optional - can be simulated with a single process for the scheduler for simplicity in a coding competition setting).

Good luck!
