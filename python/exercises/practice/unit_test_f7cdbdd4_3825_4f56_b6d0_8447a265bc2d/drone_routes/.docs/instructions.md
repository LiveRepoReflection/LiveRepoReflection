## Problem: Optimal Multi-Hop Route Planner for Drone Delivery Network

**Description:**

A revolutionary drone delivery network is being planned for a large metropolis. The city is represented as a weighted, directed graph where nodes represent delivery locations and edges represent possible drone flight paths between locations. Each edge has an associated *cost* representing energy consumption, flight time, and risk factors.

Due to drone battery limitations, direct flights between all locations aren't always possible. Therefore, drones must sometimes travel through multiple hops (intermediate locations) to reach their destination. A central server needs to efficiently calculate the *optimal* route for each delivery request, minimizing the *maximum* cost of any single hop along the route. This 'bottleneck' cost is critical for reliability – a high bottleneck cost could represent a risky or congested flight path that needs to be avoided.

Your task is to implement a function that, given the city's graph, a starting location, a destination location, and a maximum allowed number of hops, finds the route that minimizes the *maximum edge cost* (bottleneck cost) along the path.

**Input:**

*   `graph`: A dictionary representing the weighted directed graph. Keys are node IDs (integers), and values are dictionaries mapping neighbor node IDs to edge costs (integers).  For example:
    ```python
    graph = {
        0: {1: 10, 2: 5},
        1: {2: 2, 3: 8},
        2: {3: 15},
        3: {}
    }
    ```
    This represents a graph with four nodes (0, 1, 2, 3). There's a path from 0 to 1 with a cost of 10, from 0 to 2 with a cost of 5, and so on.

*   `start`: The starting node ID (integer).
*   `destination`: The destination node ID (integer).
*   `max_hops`: The maximum number of hops allowed in the route (integer). A hop is one edge traversal. If a route cannot be found within `max_hops`, return `None`.

**Output:**

*   A list of node IDs representing the optimal route from `start` to `destination` that minimizes the maximum edge cost (bottleneck cost) along the path, or `None` if no such route exists within the `max_hops` constraint.

**Constraints:**

*   The graph can contain cycles.
*   Node IDs are non-negative integers.
*   Edge costs are positive integers.
*   `0 <= max_hops <= N` where N is the number of nodes in the graph.
*   The graph can be disconnected.  It is possible that no route exists.
*   The graph's size can be large (up to 1000 nodes and potentially many edges).
*   Efficiency is critical. A naive brute-force approach will likely time out.  Consider algorithms that can prune the search space effectively.

**Example:**

```python
graph = {
    0: {1: 10, 2: 5},
    1: {2: 2, 3: 8},
    2: {3: 15},
    3: {}
}
start = 0
destination = 3
max_hops = 3

# A possible optimal route would be [0, 1, 3] with a bottleneck cost of 10.
# Another route [0, 2, 3] has a bottleneck cost of 15.
# Therefore the optimal route is [0, 1, 3].

# expected output: [0, 1, 3]
```

**Judging Criteria:**

*   **Correctness:** The code must return the optimal route with the minimum bottleneck cost.
*   **Efficiency:** The code must execute within a reasonable time limit, even for large graphs. Consider algorithmic complexity and data structure choices.
*   **Handling Edge Cases:** The code must correctly handle disconnected graphs, cycles, invalid inputs, and cases where no route exists within `max_hops`.
*   **Code Clarity:** While efficiency is crucial, the code should also be reasonably readable and well-structured.

This problem requires a combination of graph traversal algorithms, optimization techniques, and careful handling of constraints. Good luck!
