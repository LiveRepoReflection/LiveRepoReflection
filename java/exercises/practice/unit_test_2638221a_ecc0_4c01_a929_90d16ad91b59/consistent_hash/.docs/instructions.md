## Project Name

`Consistent Hashing Load Balancer`

## Question Description

You are tasked with designing and implementing a highly efficient and scalable load balancer using consistent hashing. This load balancer distributes incoming requests across a cluster of backend servers to ensure optimal resource utilization and high availability.

**Scenario:**

Imagine a distributed system where numerous clients send requests to a set of backend servers. The goal is to distribute these requests evenly across the servers while minimizing disruption when servers are added or removed from the cluster. Traditional hashing methods often lead to significant redistribution of requests upon server changes, causing performance bottlenecks and potential downtime. Consistent hashing addresses this issue by ensuring that only a minimal subset of requests are remapped when the server topology changes.

**Requirements:**

1.  **Consistent Hashing Implementation:** Implement the core consistent hashing algorithm. You should use a hash ring data structure (e.g., a sorted map or tree) to represent the servers and their virtual nodes (replicas) on the ring.

2.  **Scalability:** Design your solution to handle a large number of backend servers (up to 10,000) and a high request rate (millions of requests per second).

3.  **Fault Tolerance:** Implement mechanisms to detect and handle server failures. When a server fails, requests should be automatically rerouted to the next available server on the ring.

4.  **Dynamic Server Management:** Support the addition and removal of servers from the cluster without causing excessive request remapping. When adding a new server, only a small fraction of existing requests should be redirected.

5.  **Virtual Nodes (Replicas):** Implement virtual nodes to improve the evenness of request distribution. Each physical server should be represented by multiple virtual nodes on the hash ring. The number of virtual nodes should be configurable.

6.  **Performance Optimization:** Your solution should be optimized for low latency and high throughput. Consider using techniques such as caching and concurrency to improve performance.

7.  **API Design:** Provide a clear and concise API for adding servers, removing servers, and routing requests.

    *   `addServer(serverId, weight)`: Adds a server with a given weight (influences the number of virtual nodes).
    *   `removeServer(serverId)`: Removes a server.
    *   `getServer(key)`: Returns the server ID responsible for a given key.

8.  **Constraints:**

    *   Minimize the number of requests that need to be remapped when servers are added or removed.
    *   Ensure that the load is distributed as evenly as possible across all servers.
    *   The solution must be thread-safe to handle concurrent requests.
    *   The hashing algorithm should be efficient and produce a uniform distribution of hash values.
    *   The number of virtual nodes for each server should be proportional to its weight.  Higher weight means more virtual nodes.

9. **Edge Cases:**

    * Handle empty server list gracefully (return null or throw exception appropriately).
    * Handle requests with null or empty keys.
    * Handle duplicate server additions or removals.
    * Handle negative or zero weights for servers.
    * Ensure correct behavior when the hash ring wraps around (the highest hash value points to the lowest).

**Bonus Challenges:**

*   Implement a monitoring system to track server load and identify potential bottlenecks.
*   Implement a dynamic weight adjustment mechanism to automatically adjust server weights based on their current load.
*   Integrate your load balancer with a real-world application (e.g., a web server or a database).

This problem requires a solid understanding of consistent hashing, data structures, algorithms, and system design principles. It challenges the solver to create a robust, scalable, and efficient load balancer that can handle the demands of a modern distributed system. Good luck!
