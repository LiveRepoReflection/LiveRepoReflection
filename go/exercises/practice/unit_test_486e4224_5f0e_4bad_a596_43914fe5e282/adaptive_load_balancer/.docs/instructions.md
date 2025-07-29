## Problem: Distributed Load Balancing with Adaptive Hashing

**Question Description:**

You are designing a distributed system for handling a massive stream of incoming requests. To distribute the load evenly across multiple servers, you need to implement a dynamic load balancing strategy using adaptive consistent hashing.

You have `N` servers, each identified by a unique integer ID from `0` to `N-1`. The incoming requests are characterized by a `request_id` (a string). Your task is to design a load balancer that can efficiently map each `request_id` to a server ID, while also being able to handle server additions and removals with minimal disruption.

**Requirements:**

1.  **Adaptive Consistent Hashing:** Implement the core logic of adaptive consistent hashing.  The hash space is a ring of size `2^32`. Each server is assigned a set of `virtual nodes` (also called `replicas`) randomly distributed across the hash ring. The `request_id` is hashed to a point on the ring, and the server responsible for that point is the one whose virtual node is the closest in the clockwise direction.

2.  **Dynamic Server Pool:**  The load balancer must support adding and removing servers. When a server is added, new virtual nodes should be created and distributed on the hash ring.  When a server is removed, all its virtual nodes must be removed from the hash ring.  The number of virtual nodes assigned to each server should be configurable (see below).

3.  **Request Mapping:**  Given a `request_id`, the load balancer should return the ID of the server responsible for handling that request. This should be efficient, ideally with logarithmic complexity.

4.  **Load Balancing:**  The distribution of virtual nodes should aim to distribute the load evenly across all servers.

5.  **Minimizing Disruption:** When a server is added or removed, only a small fraction of the requests should be re-mapped to different servers.  Consistent hashing helps achieve this.

6. **Adaptive Virtual Nodes:** Implement a mechanism to adapt the number of virtual nodes per server based on server capacity. The system receives requests to update a server's capacity. The number of virtual nodes assigned to each server should be proportional to its capacity. You can assume server capacity is represented by an integer.

**Input:**

You will receive the following types of requests:

*   `add_server <server_id> <capacity>`: Adds a new server with the given ID and capacity to the load balancer.
*   `remove_server <server_id>`: Removes the server with the given ID from the load balancer.
*   `get_server <request_id>`: Returns the ID of the server responsible for handling the given request ID.
*   `update_capacity <server_id> <new_capacity>`: Updates the capacity of the specified server.
*   `get_distribution`: Returns a map of `server_id` to a list of its virtual nodes.

**Constraints:**

*   `0 <= server_id < N` (where N is the maximum number of servers, say 1000). Server IDs are unique.
*   `1 <= capacity <= 1000`
*   The number of virtual nodes per server must be at least 1 and dynamically adjustable based on the capacity.
*   The hashing function should be deterministic.  You can use a standard hashing algorithm (e.g., MD5, SHA-256) and map the hash output to the ring space.
*   Minimize the number of re-mappings when adding or removing servers and updating capacity.
*   The `get_server` operation should be efficient.
*   Your solution must be thread-safe. Multiple requests can arrive concurrently.

**Output:**

*   For `get_server` requests, return the `server_id` (integer) responsible for handling the request.
*   For `get_distribution` requests, return a map[int][]uint32 where the keys are the `server_id` and the values are a slice of the server's virtual nodes.
*   For `add_server`, `remove_server`, and `update_capacity` requests, no output is expected.

**Example:**

```
add_server 0 100
add_server 1 200
get_server "request1"  // Output: 1 (may vary based on hash function and initial distribution)
update_capacity 0 50
get_server "request2"  // Output: 1 (may vary, but ideally should be the same as before if server 1 still has more capacity)
remove_server 1
get_server "request3"  // Output: 0
```

**Judging Criteria:**

*   Correctness: The load balancer must correctly map requests to servers.
*   Load Balancing: The load should be distributed as evenly as possible across servers.
*   Minimizing Disruption: The number of re-mappings when adding or removing servers should be minimized.
*   Efficiency: The `get_server` operation should be efficient.
*   Thread Safety: The solution must be thread-safe.
*   Adaptive Virtual Nodes: The number of virtual nodes should be appropriately adjusted based on capacity updates.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a good understanding of consistent hashing, data structures, and concurrency.  It also requires careful consideration of the trade-offs between load balancing, disruption, and efficiency. Good luck!
