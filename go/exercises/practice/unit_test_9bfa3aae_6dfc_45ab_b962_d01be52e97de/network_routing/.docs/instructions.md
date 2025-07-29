Okay, here's a challenging Go coding problem designed to test a range of skills, including algorithm design, data structure manipulation, and optimization.

## Project Name

```
network-routing
```

## Question Description

You are tasked with designing an efficient routing algorithm for a data network. The network consists of `n` nodes (numbered 0 to n-1) and `m` bidirectional links. Each link connects two nodes and has an associated latency (a non-negative integer representing the time it takes for data to travel across the link).

The network is dynamic. Over time, links can be added or removed from the network. When links are removed, your algorithm need to recalculate the network routes.

Your goal is to implement a system that can quickly answer shortest path queries and efficiently update the routing table when the network topology changes.

Specifically, you need to implement the following:

1.  **`NewNetwork(n int)`**: Creates a new network with `n` nodes and no links.

2.  **`AddLink(node1, node2, latency int)`**: Adds a bidirectional link between `node1` and `node2` with the specified `latency`. If the link already exists, update the latency to the new value.

3.  **`RemoveLink(node1, node2 int)`**: Removes the link between `node1` and `node2`.

4.  **`GetShortestPath(startNode, endNode int)`**: Returns the shortest path (minimum total latency) between `startNode` and `endNode`. If no path exists, return -1.

**Constraints:**

*   `1 <= n <= 1000` (Number of Nodes)
*   `0 <= m <= n * (n - 1) / 2` (Number of Links)
*   `0 <= latency <= 1000`
*   The network may not be fully connected.
*   The number of calls to `AddLink`, `RemoveLink`, and `GetShortestPath` can be up to 10000.
*   The nodes are numbered from 0 to n-1.

**Efficiency Requirements:**

*   `GetShortestPath` should be reasonably fast, even on larger networks. Naive implementations (e.g., repeatedly running Dijkstra's algorithm for each query) may not be efficient enough.
*   `AddLink` and `RemoveLink` should also be relatively efficient. Consider how these operations affect the overall routing strategy.  You might need to recalculate the shortest paths of the network.
*   Memory usage should be reasonable. Avoid storing excessive amounts of data that are not needed.

**Considerations for Difficulty:**

*   **Dynamic Updates:** The constant addition and removal of links require a routing strategy that can adapt quickly.  Recalculating everything on every change will be too slow.
*   **Disconnected Graphs:**  The network might not be fully connected, requiring handling of cases where no path exists.
*   **Negative Cycles (Optional - Increases Difficulty Further):** *For a truly masochistic challenge, consider the case where negative latency links might be added. This would require using the Bellman-Ford algorithm or detecting negative cycles.*  If negative cycles are present, `GetShortestPath` should return -2.

This problem requires careful consideration of algorithm selection (Dijkstra, A*, Floyd-Warshall, or more advanced routing algorithms), data structure choices (adjacency lists, matrices, heaps), and optimization techniques to meet the efficiency requirements. The dynamic nature of the network adds a significant layer of complexity. Good luck!
