## Project Name:

### Optimal Network Routing

### Question Description:

You are tasked with designing an optimal routing algorithm for a large-scale communication network. The network consists of `N` nodes, interconnected by `M` bidirectional links. Each link has a cost associated with it, representing factors like latency, bandwidth consumption, and security risk. Your goal is to implement an algorithm that can efficiently determine the lowest-cost path between any two given nodes in the network, subject to the following constraints and requirements:

1.  **Dynamic Network Topology:** The network topology is not static. Links can fail or new links can be established at any time. Your algorithm must be able to adapt to these changes efficiently, without requiring a complete recomputation of all paths. The update operations will consist of adding a new link or removing an existing link.

2.  **Time-Varying Link Costs:** The cost associated with each link is not constant. It can change over time, depending on network congestion, security threats, or other factors. Your algorithm must be able to handle these cost changes efficiently, again without requiring a complete recomputation.

3.  **Multiple Cost Metrics:** Each link has *k* cost metrics associated with it: cost1, cost2, ..., costk. The user should be able to define a weight for each of these metrics: weight1, weight2, ..., weightk. The total cost of a link is the weighted sum of its cost metrics.

4.  **Scalability:** The network can be very large (up to 10^6 nodes and 10^7 links). Your algorithm must be scalable and efficient, both in terms of time and memory complexity. Inefficient solutions will time out.

5.  **Real-Time Queries:** The system must be able to respond to pathfinding queries in real-time. Given a source node, a destination node, and a set of metric weights, your algorithm must quickly return the lowest-cost path.

6.  **Handling Failures:** Your algorithm must be resilient to node failures. If a node fails, the algorithm should dynamically re-route traffic to avoid the failed node.

7.  **Path Reconstruction:** The algorithm must be able to efficiently reconstruct the optimal path, not just its cost.

**Input:**

Your solution will receive the following inputs:

*   A list of initial network links, where each link is represented as a tuple `(node1, node2, [cost1, cost2, ..., costk])`.
*   A series of update operations, which can be either:
    *   `add (node1, node2, [cost1, cost2, ..., costk])`: Add a new link between node1 and node2 with the given costs.
    *   `remove (node1, node2)`: Remove the existing link between node1 and node2.
    *   `cost_change (node1, node2, [new_cost1, new_cost2, ..., new_costk])`: Change the costs of the link between node1 and node2 to the given new costs.
    *   `weights_change([new_weight1, new_weight2, ..., new_weightk])`: Change the weights assigned to each cost metric.
*   A series of pathfinding queries, where each query is represented as a tuple `(source_node, destination_node, [weight1, weight2, ..., weightk])`. Note that the metric weights are optional, the last set of weights must be reused if none are provided.

**Output:**

For each pathfinding query, your solution must output:

*   A list of nodes representing the lowest-cost path from the source node to the destination node. If no path exists, return an empty list.

**Constraints:**

*   `1 <= N <= 10^6` (Number of nodes)
*   `1 <= M <= 10^7` (Number of links)
*   `1 <= k <= 5` (Number of cost metrics)
*   Node IDs are integers from 0 to N-1.
*   Cost values are non-negative integers.
*   Weights are non-negative floating-point numbers.
*   The number of update operations and pathfinding queries can be large (up to 10^5).
*   Time limit: Several seconds.

**Example:**

```
Initial links: [(0, 1, [1, 2]), (1, 2, [3, 4]), (0, 2, [5, 6])]
Queries:
1.  (0, 2, [0.5, 0.5])  -> Output: [0, 1, 2] (Cost: (1*0.5 + 2*0.5) + (3*0.5 + 4*0.5) = 1.5 + 3.5 = 5)
2.  add (2, 3, [1, 1])
3.  (0, 3, [0.5, 0.5]) -> Output: [0, 1, 2, 3] (Cost: 5 + (1*0.5 + 1*0.5) = 6)
4.  remove (1, 2)
5.  (0, 2, [0.5, 0.5])  -> Output: [0, 2] (Cost: 5)
```

**Judging Criteria:**

*   Correctness: Your solution must correctly find the lowest-cost path for all test cases.
*   Efficiency: Your solution must be scalable and efficient, both in terms of time and memory complexity. Solutions that time out will be rejected.
*   Handling Dynamic Updates: Your solution must efficiently handle network topology changes and link cost changes.
*   Code Quality: Your code should be well-structured, readable, and maintainable.

Good luck! This is a challenging problem that requires a deep understanding of graph algorithms, data structures, and optimization techniques.
