Okay, here's a challenging C++ coding problem designed to be intricate and demanding, drawing inspiration from the examples you've provided.

### Project Name

```
OptimalNetworkPathfinder
```

### Question Description

A large-scale distributed system is comprised of `n` nodes, uniquely identified by integers from `0` to `n-1`. These nodes are interconnected via a network.  Each connection between two nodes has a *latency* (a positive integer representing the time it takes for a message to travel between them) and a *bandwidth* (a positive integer representing the maximum data transfer rate).

You are given the following inputs:

1.  `n`: The number of nodes in the network.
2.  `connections`: A vector of tuples, where each tuple `(node1, node2, latency, bandwidth)` represents a bidirectional connection between `node1` and `node2` with the specified latency and bandwidth.  Note that multiple connections can exist between the same two nodes, each with potentially different latency and bandwidth values.
3.  `start_node`: The ID of the starting node.
4.  `end_node`: The ID of the destination node.
5.  `required_bandwidth`: The minimum bandwidth required for the communication path.

Your task is to find the path from `start_node` to `end_node` that minimizes the *total latency* while ensuring that *every connection* along the path has a bandwidth *greater than or equal to* `required_bandwidth`.

If multiple paths satisfy these conditions, return the path with the fewest number of hops (intermediate nodes). If no such path exists, return an empty vector.

**Constraints:**

*   `1 <= n <= 10000`
*   `0 <= node1, node2 < n`
*   `1 <= latency <= 1000`
*   `1 <= bandwidth <= 1000`
*   `0 <= start_node, end_node < n`
*   `1 <= required_bandwidth <= 1000`
*   The network may not be fully connected.
*   There might be cycles in the network.
*   The same node may appear multiple times within the 'connections' vector.

**Efficiency Requirements:**

Your solution must be efficient enough to handle large networks (up to `n = 10000`) within a reasonable time limit.  Consider the algorithmic complexity of your approach carefully.  Solutions with high time complexity may not pass all test cases.

**Edge Cases:**

*   `start_node` and `end_node` are the same.  Should return a path containing only the `start_node`.
*   No path exists between `start_node` and `end_node` that meets the bandwidth requirement.
*   `start_node` or `end_node` are invalid (out of range).
*   The `connections` vector is empty.

**Output:**

Return a `std::vector<int>` representing the optimal path from `start_node` to `end_node`.  The vector should contain the node IDs in the order they are visited along the path, starting with `start_node` and ending with `end_node`.

**Example:**

```
n = 5
connections = {
    {0, 1, 5, 10},
    {0, 2, 10, 5},
    {1, 2, 2, 8},
    {1, 3, 8, 12},
    {2, 3, 5, 7},
    {3, 4, 3, 15}
}
start_node = 0
end_node = 4
required_bandwidth = 8

Optimal Path: {0, 1, 3, 4}
```

**Explanation:**

The path `0 -> 1 -> 3 -> 4` has a total latency of `5 + 8 + 3 = 16`. All connections on this path have a bandwidth greater than or equal to `8`. Other paths might exist (e.g., `0 -> 1 -> 2 -> 3 -> 4`), but they either have higher latency or include connections with bandwidth less than 8.

This problem is designed to be challenging due to the combination of graph traversal, optimization criteria (latency *and* hop count), bandwidth constraints, and the potential for large input sizes.  Good luck!
