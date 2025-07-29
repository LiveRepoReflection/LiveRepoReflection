## Project Name

```
OptimalResourceAllocation
```

## Question Description

A large-scale distributed system manages a pool of heterogeneous resources (CPU cores, memory, disk space, network bandwidth, etc.) These resources are requested by various tasks with different priorities and resource requirements. Your task is to design and implement an efficient resource allocation algorithm that maximizes the overall system utility, considering resource fragmentation, task priorities, and real-time allocation constraints.

The system receives a continuous stream of task requests. Each task is characterized by:

*   **Task ID:** A unique identifier for the task (String).
*   **Priority:** An integer representing the task's priority (higher value means higher priority).
*   **Resource Requirements:** A map specifying the amount of each resource type required by the task (e.g., `{CPU: 4, Memory: 8GB, Disk: 100GB}`).
*   **Arrival Time:** The time at which the task request is received (long timestamp).
*   **Deadline:** The latest time at which the task must start executing to be considered successful (long timestamp).
*   **Expected Execution Time:** The estimated time the task will take to complete if allocated its required resources (long, simulation time).

The system has a finite capacity of each resource type. The resource pool is represented as a map of resource types to their available quantities (e.g., `{CPU: 64, Memory: 128GB, Disk: 1TB}`).

Your algorithm should:

1.  **Accept Task Requests:** Receive task requests from the input stream.
2.  **Allocate Resources:** Attempt to allocate the requested resources to each task. Allocation must be done before the task's deadline.
3.  **Maximize System Utility:** Prioritize tasks based on their priority and allocate resources to maximize the number of high-priority tasks that are successfully executed. Successfully executed means that the task has been assigned resources before its deadline.
4.  **Handle Resource Fragmentation:** Implement a strategy to minimize resource fragmentation, ensuring that available resources are utilized effectively over time.
5.  **Real-Time Constraints:** The allocation decision for each task must be made within a strict time limit (e.g., 100ms). Failing to meet this deadline will result in the task being rejected.
6.  **Preemption (Optional):** For an additional challenge, consider implementing a preemption mechanism where lower-priority tasks can be temporarily suspended to allocate resources to higher-priority tasks with imminent deadlines. Be careful to design the simulation to have the effect of preemption when necessary.
7.  **Return Task Status:** After processing each task request (allocation attempt or rejection), the system should return the following task processing information:
    *   **Task ID**
    *   **Allocation Status:** A boolean indicating whether the task was successfully allocated resources.
    *   **Start Time:** The timestamp at which the task started executing (if allocated).
    *   **End Time:** The timestamp at which the task is expected to complete, based on its expected execution time (if allocated).

**Constraints:**

*   The number of resource types is limited (e.g., CPU, Memory, Disk, Network).
*   The number of tasks in the input stream can be very large (e.g., millions).
*   The resource pool capacity is finite but reasonably large.
*   The allocation decision time limit is strict (e.g., 100ms).
*   The simulation time window is significant (e.g., 24 hours).
*   Resource allocation must be exclusive (a resource cannot be assigned to multiple tasks simultaneously).
*   Tasks can only be allocated resources once. Re-allocation is not permitted.

**Evaluation:**

Your solution will be evaluated based on the following metrics:

*   **Overall System Utility:** Measured as the weighted sum of successfully executed tasks, where the weights are the task priorities.
*   **Resource Utilization:** The average percentage of each resource type that is utilized over the simulation time.
*   **Algorithm Efficiency:** The average time taken to make allocation decisions for each task request.
*   **Fragmentation Level:** How much of the total resources remain unused due to fragmentation.

**Note:** This is a system design problem, so focus on the design and implementation of the resource allocation algorithm. Assume that the underlying infrastructure (task execution, resource monitoring, etc.) is already in place. You can use any appropriate data structures and algorithms to solve this problem. The ability to handle a large number of tasks efficiently and meet the real-time allocation constraints is crucial.
