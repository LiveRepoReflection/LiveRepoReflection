## Question: Distributed Load Balancing with Dynamic Resource Allocation

### Question Description

You are tasked with designing a distributed load balancing system that dynamically allocates resources based on real-time demand. The system consists of a central Load Balancer (LB) and a cluster of worker nodes. The LB receives incoming requests and distributes them to available worker nodes. Worker nodes process the requests and return results.

**System Requirements:**

1.  **Dynamic Resource Allocation:** The system must automatically scale the number of active worker nodes based on the incoming request rate. If the request queue on the LB exceeds a certain threshold, new worker nodes should be provisioned. Conversely, if the request rate drops below a threshold and worker nodes are idle for a specified period, they should be deprovisioned to save resources.

2.  **Request Prioritization:** Requests have different priorities (High, Medium, Low). The LB should prioritize High-priority requests over Medium and Low-priority requests, and Medium-priority over Low-priority. Within each priority level, requests should be processed in a First-In, First-Out (FIFO) manner.

3.  **Worker Node Capacity:** Each worker node has a limited processing capacity, defined as the maximum number of requests it can handle concurrently. The LB must track the current load on each worker node and avoid overloading them.

4.  **Health Monitoring:** The LB must continuously monitor the health of the worker nodes. If a worker node becomes unresponsive or reports an error, the LB should immediately stop sending requests to that node and re-distribute its pending requests to other available nodes.

5.  **Request Timeout:** Each request has a timeout value. If a request is not processed and returned within the timeout period, the LB should consider it failed and re-queue it for processing by another available worker node.

6.  **Fault Tolerance:** The system should be resilient to failures. If the LB itself fails, there should be a mechanism to elect a new LB from a set of backup LBs. The new LB should be able to recover the state of the system (active worker nodes, pending requests, etc.) and continue processing requests seamlessly.

**Input:**

Your solution will be evaluated based on its ability to handle a stream of incoming requests, each described by the following parameters:

*   `request_id`: A unique identifier for the request (string).
*   `priority`: The priority of the request (string: "High", "Medium", "Low").
*   `processing_time`: The estimated time required to process the request (integer, in milliseconds).
*   `timeout`: The maximum time allowed for the request to be processed (integer, in milliseconds).

**Constraints:**

*   The number of worker nodes is initially limited.
*   The time it takes to provision a new worker node is significant and should be factored into the load balancing strategy.
*   The system must be able to handle a high volume of requests with varying priorities and processing times.
*   The solution must be memory efficient, especially considering the LB might have lots of requests in memory.

**Output:**

Your solution should provide the following functionalities:

1.  `submit_request(request_id, priority, processing_time, timeout)`: Submits a new request to the LB.
2.  `worker_node_available()`: Simulates a worker node becoming available (newly provisioned or finished processing a request).  Returns the allocated `request_id` or `None` if no requests can be allocated.
3.  `worker_node_finished(request_id)`: Simulates a worker node finishing processing a request.
4.  `worker_node_failed(request_id)`: Simulates a worker node failing while processing a request.
5.  `get_system_state()`: Returns a dictionary representing the current state of the system, including the number of active worker nodes, the number of pending requests for each priority level, and the average response time for each priority level.

**Evaluation Criteria:**

*   **Correctness:** The system must correctly prioritize and process requests, handle timeouts, and recover from failures.
*   **Efficiency:** The system should minimize the average response time for requests, especially for high-priority requests.
*   **Scalability:** The system should be able to handle a large number of requests and worker nodes without performance degradation.
*   **Robustness:** The system should be resilient to failures and handle unexpected events gracefully.
*   **Code Quality:** The code should be well-structured, documented, and easy to understand.

This problem requires a deep understanding of data structures, algorithms, distributed systems concepts, and optimization techniques. Good luck!
