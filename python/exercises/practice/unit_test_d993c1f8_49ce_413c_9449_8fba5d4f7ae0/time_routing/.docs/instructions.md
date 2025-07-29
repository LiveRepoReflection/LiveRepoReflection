## Question: Optimized Network Routing with Time-Dependent Costs

### Question Description

You are tasked with designing an optimal routing algorithm for a network where the cost of traversing each connection (edge) varies depending on the time of day. This network represents a complex system, such as a transportation network or a data delivery system, where congestion and other factors affect travel times or bandwidth availability.

The network consists of **N** nodes (numbered 0 to N-1) and **M** directed edges. Each edge has a source node, a destination node, and a time-dependent cost function. The cost function is represented as a list of **K** (time, cost) pairs, sorted by time.  The cost at any given time *t* for an edge is determined by linear interpolation between the two nearest time points in its cost function. If *t* is before the first time point, the cost is equal to the cost of the first time point. Similarly, if *t* is after the last time point, the cost is equal to the cost of the last time point.

Your goal is to find the minimum cost path from a given start node to a given end node, departing at a specific start time.

**Input:**

*   **N**: The number of nodes in the network (1 <= N <= 1000).
*   **M**: The number of directed edges in the network (1 <= M <= 5000).
*   **edges**: A list of M tuples, where each tuple represents an edge:
    *   (source, destination, cost_function)
        *   `source`: Integer representing the source node (0 <= source < N).
        *   `destination`: Integer representing the destination node (0 <= destination < N).
        *   `cost_function`: A list of K tuples, where each tuple represents a (time, cost) pair. (1 <= K <= 20). Times are non-negative integers. Costs are positive floating-point numbers.  The time values within a cost_function are strictly increasing.
*   **start_node**: The starting node (0 <= start_node < N).
*   **end_node**: The destination node (0 <= end_node < N).
*   **start_time**: The departure time from the start node (a non-negative integer).

**Output:**

*   The minimum cost to travel from the start node to the end node, departing at the specified start time. If no path exists, return -1.

**Constraints:**

*   The algorithm must be efficient enough to handle a large number of nodes and edges.
*   The time-dependent cost functions must be handled accurately.
*   The algorithm should consider all possible paths and find the minimum cost path.
*   Your solution must provide the result within a reasonable time limit (e.g., within 10 seconds).
*   All nodes are reachable from the start node.

**Example:**

```
N = 4
M = 5
edges = [
    (0, 1, [(0, 1.0), (10, 2.0)]),
    (0, 2, [(0, 3.0), (5, 1.0), (15, 4.0)]),
    (1, 2, [(0, 2.0), (7, 5.0)]),
    (1, 3, [(0, 1.0)]),
    (2, 3, [(0, 4.0), (12, 2.0)])
]
start_node = 0
end_node = 3
start_time = 2

```

In this example, a possible path is:

1.  Start at node 0 at time 2.
2.  Travel to node 1. The cost of edge (0, 1) at time 2 is interpolated as: `1.0 + (2-0)/(10-0) * (2.0 - 1.0) = 1.2`.  Arrival time at node 1 is `2 + 1.2 = 3.2`.
3.  Travel to node 3. The cost of edge (1, 3) at time 3.2 is 1.0. Arrival time at node 3 is `3.2 + 1.0 = 4.2`.

Your algorithm should find the path with the minimum total cost, considering the time-dependent costs of the edges.

**Judging Criteria:**

*   Correctness: The algorithm must correctly find the minimum cost path for all valid inputs.
*   Efficiency: The algorithm must be efficient enough to handle large networks within the time limit.
*   Code Quality: The code should be well-structured, readable, and maintainable.
