Okay, here's your challenging Python coding problem.

## Problem: Optimal Multi-Commodity Flow Routing

### Description

You are tasked with designing the optimal routing strategy for a network that transports multiple commodities. The network is represented as a directed graph, where nodes represent locations and edges represent connections between locations with associated capacities. Each commodity has a source node, a destination node, and a demand representing the amount of that commodity that must be transported from its source to its destination.

Your goal is to determine the flow of each commodity along the network edges such that:

1.  The demand for each commodity is satisfied.
2.  The capacity of each edge is not exceeded by the total flow of all commodities passing through it.
3.  The total cost of transporting all commodities across the network is minimized. The cost of transporting a commodity along an edge is proportional to the flow of the commodity on that edge and a given cost factor associated with that edge.

**Input:**

*   `num_nodes`: An integer representing the number of nodes in the network (nodes are numbered from 0 to `num_nodes - 1`).
*   `edges`: A list of tuples, where each tuple `(u, v, capacity, cost)` represents a directed edge from node `u` to node `v` with capacity `capacity` and cost per unit flow `cost`.
*   `commodities`: A list of tuples, where each tuple `(source, destination, demand)` represents a commodity that needs to be transported from `source` to `destination` with a demand of `demand`.

**Output:**

A dictionary mapping each edge `(u, v)` to a dictionary of commodity flows. Specifically, `result[(u, v)][i]` should represent the amount of commodity `i` flowing from node `u` to node `v`. If there is no feasible solution, return `None`.

**Constraints:**

*   `1 <= num_nodes <= 100`
*   `1 <= len(edges) <= 500`
*   `1 <= len(commodities) <= 100`
*   `0 <= u, v < num_nodes`
*   `1 <= capacity <= 1000` for each edge
*   `1 <= cost <= 100` for each edge
*   `0 <= source, destination < num_nodes` for each commodity
*   `1 <= demand <= 500` for each commodity
*   The graph may not be fully connected.
*   Multiple edges may exist between the same pair of nodes.
*   The graph might contain cycles.
*   Self-loops are not allowed.
*   The solution should minimize the total cost, not just find any feasible solution.

**Optimization Requirement:**

Your solution should be efficient enough to handle networks with up to 100 nodes, 500 edges, and 100 commodities within a reasonable time limit (e.g., 1 minute). Consider using appropriate algorithms and data structures to achieve optimal performance.

**Example:**

```python
num_nodes = 4
edges = [
    (0, 1, 10, 1),
    (0, 2, 5, 2),
    (1, 2, 15, 1),
    (1, 3, 7, 3),
    (2, 3, 12, 1)
]
commodities = [
    (0, 3, 8)
]

# Expected output (example, might not be the only optimal solution):
# {
#     (0, 1): {0: 7},
#     (0, 2): {0: 1},
#     (1, 2): {0: 0},
#     (1, 3): {0: 7},
#     (2, 3): {0: 1}
# }
```

This problem requires a good understanding of network flow algorithms and optimization techniques. Good luck!
