## Problem: Distributed Load Balancer Simulation

### Question Description

You are tasked with designing and implementing a simulation of a distributed load balancer for a high-traffic web application. The system consists of multiple servers and a load balancer that distributes incoming requests across these servers.

**System Architecture:**

1.  **Servers:** A cluster of `N` servers, each with a limited processing capacity. Each server has a unique ID (1 to N).
2.  **Load Balancer:** A central component that receives incoming requests and forwards them to the appropriate server based on a chosen load balancing algorithm.
3.  **Requests:** Incoming requests arrive at the load balancer at varying times. Each request requires a specific amount of processing time on a server.
4.  **Metrics:** The system needs to track key performance metrics, such as server utilization, request latency, and request rejection rate.

**Specific Requirements:**

1.  **Load Balancing Algorithms:** Implement the following load balancing algorithms:
    *   **Round Robin:** Distributes requests sequentially to each server.
    *   **Least Connections:** Sends requests to the server with the fewest active connections.
    *   **Weighted Round Robin:** Each server has a weight, and requests are distributed based on these weights.
    *   **Consistent Hashing:** Maps requests and servers to a hash ring, and assigns requests to the closest server on the ring.

2.  **Server Capacity:** Each server has a maximum processing capacity represented by the number of concurrent requests it can handle. If a server is at full capacity, new requests must be rejected or queued based on configuration.

3.  **Request Queuing (Optional):** Implement an optional request queue for each server. If a server is at capacity, incoming requests can be placed in a queue until the server becomes available. The queue has a maximum size. If the queue is full, the request is rejected.

4.  **Dynamic Server Health Checks:** Implement a mechanism to periodically check the health of each server. If a server is deemed unhealthy (e.g., exceeding a CPU utilization threshold or failing to respond to health checks), the load balancer should temporarily stop sending requests to it and redistribute the load to the remaining healthy servers. The health check interval is configurable.

5.  **Optimization:** The simulation should be able to handle a large number of requests and servers efficiently. Optimize the implementation to minimize latency and maximize throughput.

6.  **Concurrency:** Implement the simulation using concurrent programming techniques (e.g., threads, asyncio) to simulate the parallel processing of requests on multiple servers.

7.  **Real-time Metrics:** The simulation should provide real-time metrics about server utilization, request latency, and request rejection rate. Display these metrics during the simulation.

8.  **Configuration:** Design the system to be configurable. The number of servers, their processing capacity, the load balancing algorithm, queue sizes (if applicable), health check interval, and request arrival rates should be configurable parameters.

**Input:**

The simulation should accept the following inputs:

*   `N`: The number of servers.
*   `server_capacity`: The processing capacity of each server (number of concurrent requests).
*   `load_balancing_algorithm`: The load balancing algorithm to use (e.g., "round_robin", "least_connections", "weighted_round_robin", "consistent_hashing").
*   `server_weights` (if using "weighted\_round\_robin"): A list of weights for each server.
*   `queue_size` (optional): The maximum size of the request queue for each server. If 0, no queuing is used.
*   `health_check_interval`: The interval (in seconds) for performing server health checks.
*   `request_arrival_rate`: The average number of requests arriving per second.
*   `request_durations`: A list of the processing time (in seconds) required for each request.
*   `simulation_time`: The total simulation time (in seconds).

**Output:**

The simulation should output the following metrics:

*   Average server utilization (percentage).
*   Average request latency (seconds).
*   Request rejection rate (percentage).
*   Number of requests processed by each server.
*   A timeline of server health status (indicating when servers went down and recovered).

**Constraints:**

*   The number of servers (`N`) can be up to 100.
*   The server capacity can be up to 1000.
*   The simulation time can be up to 3600 seconds (1 hour).
*   The request arrival rate can be up to 1000 requests per second.
*   Minimize the simulation execution time, even with high request rates.
*   Handle edge cases gracefully, such as invalid input parameters or server failures.

**Judging Criteria:**

*   Correctness: The simulation accurately implements the load balancing algorithms and server health checks.
*   Efficiency: The simulation is able to handle a large number of requests and servers efficiently.
*   Scalability: The simulation can be easily scaled to handle more servers and higher request rates.
*   Code Quality: The code is well-structured, readable, and maintainable.
*   Completeness: All required features are implemented and work correctly.
*   Error Handling: The simulation handles errors gracefully and provides informative error messages.

This problem requires knowledge of data structures, algorithms, concurrent programming, and system design principles. It is designed to be challenging and requires careful planning and optimization.
