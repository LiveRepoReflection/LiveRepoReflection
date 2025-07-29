Okay, I'm ready. Here's a challenging Rust coding problem:

## Project Name

`NetworkTopologyOptimization`

## Question Description

You are tasked with designing and optimizing a communication network for a large-scale distributed system. The network consists of `n` nodes, where each node represents a server.  The goal is to minimize the average latency between any two nodes in the network, while adhering to specific cost constraints and fault tolerance requirements.

The network topology is represented as an undirected graph where nodes are vertices and communication links are edges. Each edge has a cost associated with it (e.g., construction or leasing cost), and a capacity (maximum bandwidth).  The total cost of the network is the sum of the costs of all edges in the graph. The latency between two nodes is defined as the shortest path latency between them, calculated by summing the latencies of the edges along the shortest path. The latency of an edge is inversely proportional to its capacity: `latency = 1 / capacity`.

You are given the following inputs:

*   `n`: The number of nodes in the network (nodes are numbered from 0 to n-1).
*   `edge_costs`: A `HashMap<(usize, usize), u32>` where the key `(u, v)` represents an edge between node `u` and node `v`, and the value is the cost of that edge.  Note that the graph is undirected, so if `(u, v)` exists, `(v, u)` also exists with the same cost.
*   `edge_capacities`: A `HashMap<(usize, usize), u32>` where the key `(u, v)` represents an edge between node `u` and node `v`, and the value is the capacity of that edge. Again, the graph is undirected. The minimum possible capacity of an edge is 1.
*   `max_total_cost`: The maximum allowable total cost for the entire network.
*   `fault_tolerance`: An integer representing the minimum number of *edge-disjoint paths* required between any two nodes.

Your task is to write a function `optimize_network` that takes these inputs and returns the *minimum possible average latency* across all pairs of nodes in the network, subject to the given constraints. If no valid network topology can be constructed that meets all constraints, return `None`.

**Constraints and Requirements:**

*   The graph must be connected.
*   The total cost of the edges in the graph must not exceed `max_total_cost`.
*   For every pair of nodes (u, v), there must be at least `fault_tolerance` edge-disjoint paths between them.  Edge-disjoint paths are paths that share no common edges.
*   The average latency is calculated as the sum of all shortest path latencies between all pairs of nodes, divided by the number of node pairs (n \* (n - 1) / 2).
*   The solution must be computationally efficient.  Brute-force approaches that explore all possible graph topologies will likely time out. Consider using appropriate graph algorithms and data structures.
*   Consider the edge cases where `n` is small (e.g., 1 or 2) or `fault_tolerance` is high relative to `n`.
*   The solution should handle potentially large values of `n` (up to 1000) and reasonably large values for `edge_costs` and `edge_capacities` (up to u32::MAX).

**Function Signature:**

```rust
use std::collections::HashMap;

fn optimize_network(
    n: usize,
    edge_costs: &HashMap<(usize, usize), u32>,
    edge_capacities: &HashMap<(usize, usize), u32>,
    max_total_cost: u32,
    fault_tolerance: usize,
) -> Option<f64> {
    // Your code here
    None // Placeholder return value
}
```

**Example:**

Let's say you have a small example with 4 nodes, a limited budget, and a high fault tolerance requirement.  The solution should be able to determine if a valid network configuration exists within the cost constraints while satisfying the edge-disjoint path requirement. If no such configuration exists, it should return `None`. If one or more configurations exist, it should return the average latency of the optimal configuration.

This problem requires a combination of graph theory knowledge, algorithmic design, and careful optimization to handle the constraints and large input sizes. Good luck!
