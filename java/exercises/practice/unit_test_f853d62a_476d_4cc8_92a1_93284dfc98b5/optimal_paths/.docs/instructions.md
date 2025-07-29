## Question: Optimal Multi-Source Shortest Paths with Capacity Constraints

### Question Description

You are given a directed graph represented by a list of nodes and a list of edges. Each edge has a weight (representing distance) and a capacity (representing the maximum flow allowed through that edge).

Specifically:

*   **Nodes:** Represented by integers from `0` to `N-1`, where `N` is the total number of nodes.
*   **Edges:** Represented as a list of tuples `(u, v, weight, capacity)`, where `u` is the source node, `v` is the destination node, `weight` is the distance of the edge, and `capacity` is the maximum flow allowed through the edge.
*   **Source Nodes:** You are given a list of `K` source nodes.
*   **Target Node:** You are given a single target node.

Your task is to find the shortest possible distance from **any** of the source nodes to the target node, subject to the following constraints:

1.  **Capacity Constraint:** The total flow along any edge cannot exceed its capacity. You do *not* need to calculate the actual flow distribution; you only need to ensure that a feasible flow exists from a source to the target.  Consider that you can only send the "flow" through the path with capacity constraints to the target node.
2.  **Multi-Source:** You must consider all source nodes simultaneously. The shortest path can originate from *any* of the provided source nodes.
3.  **Non-Negative Weights:** Edge weights are non-negative.
4.  **Disconnected Graph:** The graph may be disconnected. If the target node is not reachable from any of the source nodes, return `-1`.
5.  **Optimization:** Minimize the time complexity of your solution, especially when dealing with a large number of nodes and edges.  Dijkstra-based solutions are encouraged.

**Input:**

*   `N`: The number of nodes in the graph (an integer).
*   `edges`: A list of tuples `(u, v, weight, capacity)` representing the edges.
*   `sources`: A list of integers representing the source nodes.
*   `target`: An integer representing the target node.

**Output:**

*   The shortest distance from any source node to the target node, respecting capacity constraints. Return `-1` if the target node is unreachable from any source node.

**Constraints:**

*   `1 <= N <= 10^5`
*   `0 <= len(edges) <= 10^5`
*   `0 <= u, v, target < N`
*   `0 <= weight <= 10^4`
*   `0 <= capacity <= 10^4`
*   `1 <= len(sources) <= N`
*   All source nodes are distinct.
*   The graph might contain cycles.

**Example:**

Let's say we have:

*   `N = 6`
*   `edges = [(0, 1, 2, 10), (0, 2, 4, 5), (1, 3, 5, 15), (2, 3, 1, 8), (3, 4, 3, 20), (4, 5, 2, 7)]`
*   `sources = [0, 2]`
*   `target = 5`

The shortest path from source `0` to target `5` is `0 -> 1 -> 3 -> 4 -> 5` with a total distance of `2 + 5 + 3 + 2 = 12`. All edges have sufficient capacity to allow flow.

The shortest path from source `2` to target `5` is `2 -> 3 -> 4 -> 5` with a total distance of `1 + 3 + 2 = 6`. All edges have sufficient capacity to allow flow.

Therefore, the answer is `6` because it's the minimum of the shortest paths from any source.

**Note:** The challenge lies in efficiently handling the multi-source aspect and the capacity constraints while minimizing the overall time complexity. A naive approach will likely time out.
