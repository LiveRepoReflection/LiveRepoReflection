## Project Name

```
consistent-hashing-load-balancer
```

## Question Description

You are tasked with implementing a scalable and efficient load balancer using consistent hashing. This load balancer will distribute incoming requests across a cluster of backend servers. The goal is to minimize disruption when servers are added or removed from the cluster, ensuring high availability and performance.

**System Overview:**

*   You have a set of `N` backend servers, each identified by a unique string ID (e.g., "server-1", "server-2", etc.).
*   Incoming requests are identified by a unique string key.
*   The load balancer must route each request to a specific backend server based on the request key.
*   Consistent hashing should be used to map request keys to servers.

**Requirements:**

1.  **Consistent Hashing Implementation:** Implement a consistent hashing algorithm (e.g., using a ring-based approach). Consider the distribution of keys across the ring and techniques for improving distribution uniformity (e.g., virtual nodes/replicas).
2.  **Server Lifecycle Management:** The load balancer must support adding and removing servers dynamically. When a server is added or removed, only a minimal number of keys should be remapped to different servers.
3.  **Load Balancing:** The load balancer should distribute requests evenly across the available servers, preventing any single server from being overloaded.
4.  **Fault Tolerance:** If a server becomes unavailable, the load balancer should automatically redirect requests to another available server with minimal impact on performance.
5.  **Scalability:** The load balancer should be able to handle a large number of servers and a high volume of requests.
6.  **Key Distribution Analysis:** Implement a mechanism to analyze the key distribution across the servers. This should allow you to assess the effectiveness of your consistent hashing implementation and identify potential imbalances.

**Constraints:**

*   The number of backend servers `N` can range from 1 to 1000.
*   The number of requests can be very large (millions or billions).
*   Server IDs and request keys are strings with a maximum length of 256 characters.
*   The load balancer must be highly available and responsive.
*   Minimize the impact of server additions and removals on existing key mappings.

**Function Signature:**

You need to implement the following methods:

```go
type ConsistentHashLoadBalancer struct {
    // ... (internal data structures) ...
}

// NewConsistentHashLoadBalancer creates a new consistent hash load balancer.
func NewConsistentHashLoadBalancer(replicas int) *ConsistentHashLoadBalancer {
    // ...
}

// AddServer adds a new server to the load balancer.
func (lb *ConsistentHashLoadBalancer) AddServer(serverID string) {
    // ...
}

// RemoveServer removes a server from the load balancer.
func (lb *ConsistentHashLoadBalancer) RemoveServer(serverID string) {
    // ...
}

// GetServerForKey returns the server ID for a given request key.
func (lb *ConsistentHashLoadBalancer) GetServerForKey(key string) string {
    // ...
}

// GetKeyDistribution returns a map of server ID to the number of keys assigned to it.
func (lb *ConsistentHashLoadBalancer) GetKeyDistribution() map[string]int {
    // ...
}
```

**Evaluation Criteria:**

*   Correctness: The load balancer must correctly route requests to servers based on the consistent hashing algorithm.
*   Efficiency: The load balancer must be able to handle a large number of requests with low latency.
*   Scalability: The load balancer must be able to scale to a large number of servers without significant performance degradation.
*   Distribution: The key distribution across servers should be as even as possible.
*   Fault Tolerance: The load balancer must be able to handle server failures gracefully.
*   Code Quality: The code should be well-structured, readable, and maintainable.

**Bonus Points:**

*   Implement a mechanism for automatically detecting and removing unhealthy servers.
*   Implement different hashing algorithms and compare their performance and distribution characteristics.
*   Implement a visualization tool to display the key distribution across the servers.

This problem requires a strong understanding of consistent hashing, data structures, algorithms, and system design principles. Good luck!
