## Question: Distributed Load Balancing with Dynamic Priority

### Question Description

You are tasked with designing a distributed load balancing system. You have `N` worker nodes and a stream of incoming tasks. Each task has a priority associated with it. Your system must distribute tasks to the worker nodes while adhering to the following constraints and requirements:

**System Requirements:**

1.  **Task Prioritization:** Tasks must be processed in order of priority. Higher priority tasks should be processed before lower priority tasks. Priorities are represented by integers, where lower values indicate higher priority (e.g., 1 is higher priority than 10).

2.  **Dynamic Load Balancing:** The system must dynamically balance the load across all worker nodes. A worker node's load is defined as the number of tasks currently assigned to it. The goal is to minimize the maximum load on any worker node.

3.  **Dynamic Worker Availability:** Worker nodes can join or leave the system at any time. The system must be able to adapt to changes in the available worker pool without interrupting task processing.

4.  **Fault Tolerance:** The system should be resilient to worker node failures. If a worker node fails, any tasks assigned to it should be re-queued and processed by other available worker nodes based on their priority.

5.  **Scalability:** The system should be able to handle a large number of worker nodes and a high volume of incoming tasks.

6.  **Real-time Performance:** The system should minimize the latency of task assignment and processing.

**Input:**

Your solution will receive two types of events:

*   **Task Arrival:** `("TASK", priority, task_id)` - Indicates a new task with the given priority and task ID has arrived. `priority` is an integer, and `task_id` is a unique identifier for the task (e.g., a UUID string).
*   **Worker Node Event:** `("WORKER_JOIN", worker_id)` or `("WORKER_LEAVE", worker_id)` - Indicates a worker node has joined or left the system. `worker_id` is a unique identifier for the worker node (e.g., a UUID string).

**Output:**

Your solution should implement the following functions:

*   `handle_event(event)`: This function is called for each incoming event. It should process the event and update the system state accordingly.  For `TASK` events, it should assign the task to an available worker node.  For `WORKER_JOIN` and `WORKER_LEAVE` events, it should update the worker pool.
*   `get_worker_tasks(worker_id)`: This function should return a list of `task_id` strings currently assigned to the given `worker_id`. The order of tasks in the list does not matter.
*   `get_unprocessed_tasks()`: This function should return a list of `task_id` strings for tasks that have arrived but have not yet been assigned to a worker node. The list should be sorted by priority (ascending priority value, i.e., lower values first).

**Constraints:**

*   The number of worker nodes `N` can range from 1 to 100,000.
*   The number of tasks can be very large (millions).
*   Task priorities can range from 1 to 1,000,000.
*   The system must be thread-safe, as multiple events can arrive concurrently.
*   The `handle_event` function must have an average time complexity of O(log N) or better with respect to the number of worker nodes.  Solutions with O(N) complexity will likely time out on larger test cases.

**Judging Criteria:**

Your solution will be judged based on the following factors:

*   **Correctness:** The solution must correctly process tasks according to their priority and handle worker node events.
*   **Load Balancing:** The solution must effectively balance the load across all worker nodes.
*   **Performance:** The solution must meet the time complexity requirements and handle a large volume of tasks efficiently.
*   **Fault Tolerance:** The solution must correctly re-queue tasks when worker nodes fail.
*   **Scalability:** The solution must be able to scale to a large number of worker nodes and tasks.
*   **Code Clarity and Readability:** The code should be well-structured, easy to understand, and properly documented.

This problem requires a sophisticated understanding of data structures, algorithms, and system design principles. You'll need to carefully choose the appropriate data structures and algorithms to meet the performance and scalability requirements while ensuring correctness and fault tolerance. Good luck!
