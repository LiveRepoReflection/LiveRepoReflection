## Project Name

**Distributed Load Balancer Simulation**

## Question Description

You are tasked with simulating a simplified distributed load balancer. The system consists of a load balancer and multiple backend servers. The load balancer receives requests and distributes them to the available backend servers based on a specific algorithm. The goal is to efficiently manage the requests and ensure that no server is overloaded while minimizing response time.

**System Components:**

1.  **Load Balancer:** The entry point for all requests. It maintains a list of available backend servers and distributes incoming requests to them.

2.  **Backend Servers:** These servers process the incoming requests. Each server has a limited processing capacity, measured in "units of work" it can handle concurrently.

**Request Specification:**

Each request is defined by:

*   `request_id`: A unique identifier for the request (string).
*   `workload`: The amount of "units of work" the request requires (integer).
*   `priority`: An integer representing the priority of the request (higher value means higher priority).

**Backend Server Specification:**

Each backend server is defined by:

*   `server_id`: A unique identifier for the server (string).
*   `capacity`: The maximum "units of work" the server can handle concurrently (integer).
*   `processing_speed`: The number of "units of work" the server can complete per second (integer).

**Load Balancing Algorithm:**

The load balancer should use a modified Least Loaded algorithm that considers both the current load and the priority of incoming requests.

1.  **Priority-Based Selection:** The load balancer should prioritize sending requests to servers that have the capacity to handle them. Higher priority requests should be assigned first.

2.  **Least Loaded with Weighting:** From the available servers, the load balancer calculates a weighted load for each server. The weighted load is calculated as:

```
Weighted Load = (Current Load / Capacity) * (1 - Priority Weight * Request Priority)
```

   Where:

   *   `Current Load` is the sum of "units of work" of the requests currently being processed by the server.
   *   `Capacity` is the server's capacity.
   *   `Request Priority` is the request's priority.
   *   `Priority Weight` is a system-wide constant (float between 0 and 1, inclusive) that determines the influence of request priority on server selection.

   The load balancer should select the server with the *lowest* weighted load.

**Constraints:**

*   The system should handle a large number of concurrent requests (up to 100,000).
*   The number of backend servers can vary (up to 100).
*   Backend servers can become unavailable (simulated by removing them from the load balancer's list). The load balancer should gracefully handle this situation.
*   Requests can be canceled before completion (simulated by removing them from the server's processing queue).
*   The simulation should run for a specified duration (simulated time in seconds).
*   The `Priority Weight` should be configurable.
*   The solution should be optimized for performance. Inefficient solutions may time out.

**Requirements:**

Implement the load balancer simulation, including the following functionalities:

1.  **Add Backend Server:** Add a new backend server to the load balancer's pool.
2.  **Remove Backend Server:** Remove a backend server from the load balancer's pool.
3.  **Submit Request:** Submit a new request to the load balancer. The load balancer should assign the request to an appropriate backend server based on the algorithm described above.
4.  **Cancel Request:** Cancel a request that is currently being processed by a backend server.
5.  **Simulate:** Run the simulation for a specified duration, processing requests and updating server loads.
6.  **Metrics:** Collect the following metrics during the simulation:
    *   Average response time (time from request submission to completion).
    *   Maximum load on any server at any given time (as a percentage of capacity).
    *   Number of requests successfully completed.
    *   Number of requests cancelled.
    *   Number of requests that failed due to server unavailability.

**Input:**

Your code should accept a sequence of commands to configure the system and run the simulation. The commands will be in the following format:

*   `ADD_SERVER server_id capacity processing_speed`
*   `REMOVE_SERVER server_id`
*   `SUBMIT_REQUEST request_id workload priority`
*   `CANCEL_REQUEST request_id`
*   `SIMULATE duration priority_weight`
*   `END`

**Output:**

After the `SIMULATE` command is processed, your code should output the collected metrics in the following format:

```
Average Response Time: <average_response_time>
Maximum Load: <maximum_load_percentage>%
Completed Requests: <completed_requests>
Cancelled Requests: <cancelled_requests>
Failed Requests: <failed_requests>
```

**Grading Criteria:**

*   Correctness: The simulation should accurately implement the described load balancing algorithm and handle all specified scenarios.
*   Efficiency: The solution should be optimized for performance and handle a large number of requests and servers within the given time constraints.
*   Scalability: The solution should be able to handle a varying number of backend servers and requests.
*   Robustness: The solution should gracefully handle errors and unexpected input.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires careful consideration of data structures, algorithms, and concurrency. Good luck!
