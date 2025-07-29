## Problem: Distributed Load Balancer with Adaptive Routing

**Description:**

You are tasked with designing and implementing a simplified distributed load balancer. This load balancer distributes incoming requests across a cluster of backend servers. However, the challenge lies in intelligently routing these requests based on real-time server load and network latency.

**System Architecture:**

Imagine a system with the following components:

1.  **Load Balancer (LB):** The entry point for all client requests.  The LB needs to decide to which backend server to route the request.
2.  **Backend Servers (BS):** Servers that process the requests. Each BS has a limited capacity and can become overloaded.
3.  **Monitoring Service (MS):** A service that periodically collects load metrics (CPU usage as a percentage) from each BS and latency data (average response time in milliseconds) between the LB and each BS.  The MS provides this data to the LB.

**Functionality:**

Implement the following functions within a `LoadBalancer` struct:

*   `RegisterServer(serverID string, capacity int)`: Adds a new backend server to the load balancer's pool, along with its maximum capacity.
*   `RemoveServer(serverID string)`: Removes a backend server from the load balancer's pool.
*   `ReceiveMetrics(serverMetrics map[string]int, latencyMetrics map[string]int)`: Updates the LB with the latest load metrics (CPU usage percentage) and latency metrics (average response time) from the MS. `serverMetrics` is a map of serverID to CPU usage, and `latencyMetrics` is a map of serverID to latency.
*   `RouteRequest() string`:  Routes an incoming request to the "best" backend server. The "best" server is determined based on the following criteria:

    *   **Availability:** The server must not be overloaded (CPU usage < 90%).
    *   **Load Balancing:**  Prioritize servers with lower CPU usage.
    *   **Latency:** Among servers with acceptable load, prefer those with lower latency.

    If no server is available (all overloaded), the `RouteRequest` function should return an empty string (""). If multiple servers have the same load and latency, return the server that was registered first.

**Constraints and Requirements:**

*   **Scalability:** The load balancer should be able to handle a large number of backend servers.
*   **Real-time Data:** The routing decision must be based on the most recent metrics received from the Monitoring Service.
*   **Concurrency:** The `RegisterServer`, `RemoveServer`, `ReceiveMetrics`, and `RouteRequest` functions may be called concurrently from multiple goroutines. You **must** ensure thread safety.
*   **Efficiency:** Optimize the routing algorithm to minimize the time it takes to select a backend server. Aim for O(n) complexity for the `RouteRequest` function, where n is the number of registered servers.  Avoid unnecessary sorting or complex computations.
*   **Dynamic Updates:** The set of backend servers can change at any time due to server failures or scaling events.
*   **Edge Cases:** Handle edge cases such as:
    *   No servers registered.
    *   All servers overloaded.
    *   Metrics not available for a server.
    *   Adding or removing a server while routing a request.

**Input:**

The input to the `RouteRequest` function is implicit: it uses the internal state of the `LoadBalancer`, which is updated by `RegisterServer`, `RemoveServer`, and `ReceiveMetrics`.

**Output:**

The `RouteRequest` function should return the `serverID` of the selected backend server, or an empty string ("") if no server is available.

**Example:**

```go
lb := LoadBalancer{}
lb.RegisterServer("server1", 100)
lb.RegisterServer("server2", 100)

// Initially no metrics are available.  Routing might be random
// or based on registration order.

lb.ReceiveMetrics(map[string]int{"server1": 50, "server2": 70}, map[string]int{"server1": 10, "server2": 20})
// RouteRequest() might return "server1" (lower load and latency).

lb.ReceiveMetrics(map[string]int{"server1": 95, "server2": 60}, map[string]int{"server1": 10, "server2": 5})
// RouteRequest() should return "server2" (server1 is overloaded).

lb.RemoveServer("server2")
// Now only server1 remains (even if overloaded).
lb.ReceiveMetrics(map[string]int{"server1": 98}, map[string]int{"server1": 10})
// RouteRequest() should return "" (no servers available).
```

This problem requires a good understanding of data structures, algorithms, concurrency, and system design principles. It challenges the solver to balance competing constraints and optimize for performance in a dynamic environment.  Good luck!
