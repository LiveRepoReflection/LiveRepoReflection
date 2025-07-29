## Project Name:

```
OptimalNetworkTopology
```

## Question Description:

You are designing the network infrastructure for a large-scale distributed system. The system consists of `n` nodes, each uniquely identified by an integer from 0 to `n-1`. Due to cost constraints, you can only establish a limited number of direct connections between nodes.

Your goal is to design a network topology that minimizes the average latency between any two nodes while adhering to the following constraints:

1.  **Limited Connections:** You are allowed to create at most `m` bidirectional connections (edges) between the nodes.
2.  **Latency Metric:** The latency between two nodes is defined as the minimum number of hops required to reach one node from the other.
3.  **Connectivity:** All nodes must be reachable from each other. The graph must be connected.
4.  **Node Capacity:** Each node has a limited capacity. Node `i` can handle at most `k[i]` direct connections.

Write a function `optimal_network_topology(n, m, k)` that returns a list of tuples, where each tuple `(u, v)` represents a bidirectional connection between node `u` and node `v`. The function should produce a network topology that minimizes the average latency between all pairs of nodes while satisfying the given constraints. If no such topology can be created due to the given constrains, it should return an empty list.

**Input:**

*   `n` (int): The number of nodes in the system.
*   `m` (int): The maximum number of connections allowed.
*   `k` (list of int): A list of length `n`, where `k[i]` represents the maximum number of connections that node `i` can handle.

**Output:**

*   `connections` (list of tuples): A list of tuples, where each tuple `(u, v)` represents a connection between node `u` and node `v`. The connections should be sorted lexicographically (i.e., sorted by the first element, then by the second element).

**Constraints:**

*   3 <= `n` <= 100
*   `n` - 1 <= `m` <= `n * (n - 1) / 2`
*   1 <= `k[i]` <= `n` - 1 for all `i`
*   You must ensure that the graph is connected.
*   The solution must attempt to *minimize* the average latency. While a "perfect" solution might be computationally infeasible, the algorithm should employ strategies that *generally* lead to lower average latencies (e.g., favoring shorter paths, avoiding long chains, and considering node capacities). The testing process will involve comparison with other possible solution, with a good enough solution accepted.

**Example:**

```python
n = 5
m = 7
k = [4, 4, 4, 4, 4]

connections = optimal_network_topology(n, m, k)
# Possible output (order may vary, but should be sorted):
# [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4)]
```

**Note:** The problem is intentionally open-ended. There is no single "correct" solution. Your algorithm will be evaluated based on its ability to generate a valid network topology and its effectiveness in reducing the average latency between nodes, considering the constraints.
