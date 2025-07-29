## Question: Distributed Load Balancer with Adaptive Routing

### Question Description

You are tasked with designing and implementing a distributed load balancer for a large-scale online service. The service consists of multiple backend servers (nodes), each capable of handling a certain number of requests per second. The load balancer must distribute incoming client requests across these nodes in an efficient and adaptive manner, minimizing latency and preventing overload.

The system operates under the following constraints:

*   **Dynamic Node Capacity:** Each node has a maximum request processing capacity (requests per second, RPS). This capacity is not fixed and can change dynamically due to fluctuations in resource availability (CPU, memory, etc.). The load balancer receives periodic updates about each node's current capacity.

*   **Variable Request Latency:** The latency (response time) of processing a request can vary between different nodes due to factors such as geographical location, network conditions, and data locality. The load balancer needs to estimate the latency of each node based on historical data and adapt its routing decisions accordingly.

*   **Node Failures:** Nodes can fail unexpectedly. The load balancer must detect node failures and quickly redirect traffic to healthy nodes.

*   **Request Prioritization:** The system supports different request priorities (e.g., high, medium, low). High-priority requests should be given preference and routed to nodes with lower latency, even if it means slightly unbalancing the load.

*   **Geographic Routing:** The system aims to route requests to the geographically closest node to reduce latency, but this should be balanced with other factors like node capacity and request priority. You are given the geographic location (latitude, longitude) of each node and each incoming request.

Your goal is to implement a load balancing algorithm that intelligently routes requests to the appropriate nodes, taking into account the following factors:

1.  **Node Capacity:** Avoid overloading nodes by ensuring that the request rate does not exceed their reported capacity.
2.  **Latency:** Minimize overall latency by routing requests to nodes with lower estimated latency.
3.  **Availability:** Quickly detect and handle node failures by redirecting traffic to healthy nodes.
4.  **Request Priority:** Prioritize high-priority requests by routing them to faster nodes.
5.  **Geographic Proximity:** Route requests to geographically closer nodes when possible, considering other factors.
6.  **Algorithm Performance:** Ensure the routing decision process is efficient (low overhead) to avoid becoming a bottleneck.

You need to implement a class `LoadBalancer` with the following methods:

*   `__init__(self, nodes)`: Initializes the load balancer with a list of `Node` objects.
*   `update_node_capacity(self, node_id, capacity)`: Updates the capacity of a node.
*   `update_node_latency(self, node_id, latency)`: Updates the latency of a node (e.g., based on recent request response times).
*   `handle_request(self, request)`: Routes a single request to the most suitable node and returns the ID of the chosen node.

You will be given a `Node` class and a `Request` class, as shown below.  Do not modify these classes.

```python
import math

class Node:
    def __init__(self, node_id, latitude, longitude, capacity=0, latency=float('inf')):
        self.node_id = node_id
        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.latency = latency
        self.is_healthy = True

    def __repr__(self):
        return f"Node(id={self.node_id}, capacity={self.capacity}, latency={self.latency}, healthy={self.is_healthy})"

    def set_unhealthy(self):
        self.is_healthy = False

    def set_healthy(self):
        self.is_healthy = True


class Request:
    def __init__(self, request_id, latitude, longitude, priority="medium"):
        self.request_id = request_id
        self.latitude = latitude
        self.longitude = longitude
        self.priority = priority

    def __repr__(self):
        return f"Request(id={self.request_id}, priority={self.priority})"
```

**Constraints:**

*   The number of nodes can range from 1 to 1000.
*   Node capacities can range from 0 to 1000 requests per second.
*   Latencies can range from 1 ms to 1000 ms.
*   Request priorities are "high", "medium", or "low".
*   You are free to use any data structures and algorithms to solve this problem.
*   Your solution should be optimized for performance, as it will be handling a large volume of requests.

**Example Usage:**

```python
node1 = Node("node1", 34.0522, -118.2437, capacity=100, latency=50)
node2 = Node("node2", 37.7749, -122.4194, capacity=50, latency=100)
node3 = Node("node3", 40.7128, -74.0060, capacity=75, latency=75)

load_balancer = LoadBalancer([node1, node2, node3])

request1 = Request("req1", 34.0522, -118.2437, priority="high")
request2 = Request("req2", 37.7749, -122.4194, priority="medium")
request3 = Request("req3", 40.7128, -74.0060, priority="low")

node_id1 = load_balancer.handle_request(request1)
node_id2 = load_balancer.handle_request(request2)
node_id3 = load_balancer.handle_request(request3)

print(f"Request {request1.request_id} routed to {node_id1}")
print(f"Request {request2.request_id} routed to {node_id2}")
print(f"Request {request3.request_id} routed to {node_id3}")

load_balancer.update_node_capacity("node1", 150)
load_balancer.update_node_latency("node2", 60)

request4 = Request("req4", 34.0522, -118.2437, priority="high")
node_id4 = load_balancer.handle_request(request4)
print(f"Request {request4.request_id} routed to {node_id4}")
```

**Scoring Criteria:**

*   **Correctness:** The load balancer must correctly route requests to healthy nodes while respecting their capacity.
*   **Latency Optimization:** The load balancer should minimize the overall latency of request processing.
*   **Priority Handling:** High-priority requests should be routed to faster nodes.
*   **Geographic Proximity:** The load balancer should consider geographic proximity when making routing decisions.
*   **Efficiency:** The load balancer's routing algorithm should be efficient and avoid becoming a bottleneck.
*   **Scalability:** The load balancer should be able to handle a large number of nodes and requests.
*   **Failure Handling:** The load balancer should handle node failures gracefully and redirect traffic to healthy nodes.

This problem requires a combination of data structures, algorithms, and system design considerations to implement an efficient and robust distributed load balancer. Good luck!
