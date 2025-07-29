## Problem Title: Optimal Multi-Hop Delivery Network Design

**Problem Description:**

You are tasked with designing an optimal delivery network for a logistics company operating in a large, densely populated urban area. The area is represented as a graph where nodes represent delivery locations (warehouses, customer residences, pick-up points), and edges represent potential delivery routes between these locations. Each edge has associated with it a *cost* (representing fuel consumption, time, tolls, etc.) and a *reliability* (representing the probability of successful delivery without delays or incidents).

The company needs to deliver goods from a central warehouse (source node) to various customer locations (destination nodes). However, direct deliveries from the source to every destination are often not feasible due to distance, congestion, or reliability issues. Therefore, multi-hop deliveries, where goods are routed through intermediate nodes, are necessary.

Your goal is to design an algorithm that determines the optimal delivery route for each customer location, considering both the total *cost* and the overall *reliability* of the route. The optimal route is defined as the route that maximizes a combined score, calculated as follows:

`Score = (Reliability_of_Route)^α / (Cost_of_Route)^β`

Where:

*   `Reliability_of_Route` is the product of the reliabilities of all edges in the route.
*   `Cost_of_Route` is the sum of the costs of all edges in the route.
*   `α` and `β` are non-negative weighting factors that represent the company's priorities (e.g., higher `α` prioritizes reliability, higher `β` prioritizes cost). These will be given as input.

**Input:**

*   `n`: The number of nodes in the graph (numbered from 0 to n-1).
*   `edges`: A list of tuples, where each tuple represents an edge: `(source_node, destination_node, cost, reliability)`.  `source_node` and `destination_node` are integers representing the node IDs. `cost` is a positive float representing the cost of traversing the edge. `reliability` is a float between 0 and 1 (inclusive) representing the probability of successful delivery.
*   `source`: An integer representing the ID of the central warehouse (source node).
*   `destinations`: A list of integers representing the IDs of the customer locations (destination nodes).
*   `alpha`: A non-negative float representing the weighting factor for reliability.
*   `beta`: A non-negative float representing the weighting factor for cost.

**Output:**

*   A dictionary where the keys are the destination node IDs from the `destinations` list, and the values are lists representing the optimal path (sequence of node IDs) from the source to that destination. If no path exists to a destination, the value should be an empty list `[]`.

**Constraints:**

*   1 <= n <= 1000
*   1 <= number of edges <= 5000
*   0 <= `source` < n
*   All elements in `destinations` are valid node IDs (0 <= node ID < n).
*   0 <= `alpha` <= 10
*   0 <= `beta` <= 10
*   The graph may not be fully connected.
*   There may be multiple paths between any two nodes.
*   The solution must be efficient enough to handle relatively large graphs within a reasonable time limit (e.g., a few seconds). Consider algorithmic complexity when choosing your approach.
*   If multiple paths have the same optimal score for a given destination, return any one of those paths.

**Example:**

```
n = 5
edges = [
    (0, 1, 10, 0.9),
    (0, 2, 15, 0.8),
    (1, 3, 12, 0.7),
    (2, 3, 8, 0.95),
    (3, 4, 5, 0.99)
]
source = 0
destinations = [3, 4]
alpha = 1.0
beta = 1.0

# Expected Output (example - actual optimal path may vary based on your algorithm):
# {
#     3: [0, 2, 3],
#     4: [0, 2, 3, 4]
# }
```

**Scoring:**

Solutions will be evaluated based on correctness (producing valid paths) and efficiency (handling large graphs within the time limit). Submissions with significant performance bottlenecks will be penalized.
