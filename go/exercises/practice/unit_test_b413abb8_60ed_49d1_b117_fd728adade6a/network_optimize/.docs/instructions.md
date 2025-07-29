## Project Name

`NetworkOptimization`

## Question Description

You are tasked with optimizing data transfer across a complex network. The network consists of `n` nodes, numbered from `0` to `n-1`. Each node represents a server, and the connections between them represent communication links with varying bandwidth capacities.

You are given the following information:

*   `n`: The number of nodes in the network.
*   `edges`: A list of tuples, where each tuple `(u, v, capacity)` represents a directed edge from node `u` to node `v` with a bandwidth `capacity`.  Assume that the capacity is a positive integer. Multiple edges could exist between two nodes.
*   `source`: The source node (an integer between `0` and `n-1`).
*   `destination`: The destination node (an integer between `0` and `n-1`), different from source.
*   `latency`: A map of tuples to integers, where each tuple `(u, v)` represents the latency (in milliseconds) of the directed edge from node `u` to node `v`. The latency is guaranteed to be positive. There is a latency entry for each existing edge.

Your goal is to design a system that can efficiently handle a series of data transfer requests between the `source` and `destination` nodes. For each data transfer request of `data_size` (in bytes), you need to determine the optimal path that maximizes the effective throughput, considering both bandwidth capacity and latency.

The effective throughput of a path is defined as:

`Effective Throughput = min(bandwidths along the path) / (latency of the path)`

where:

*   `bandwidths along the path` are the capacities of all the edges in the path, in bytes per millisecond.
*   `latency of the path` is the sum of latencies of all the edges in the path, in milliseconds.

Your solution must implement a function `optimize_network(n, edges, source, destination, latency, data_size)` that returns the optimal path (a list of node indices representing the path from source to destination) and the corresponding effective throughput (a float).

**Constraints and Requirements:**

1.  **Network Size:** The network can be large (up to `10^5` nodes and `10^6` edges).
2.  **Edge Cases:** Handle cases where no path exists between the source and destination, or where the network is disconnected. In these cases, return an empty list for the path and `0.0` for the effective throughput.
3.  **Negative Cycles:** The graph does not contain negative cycles.
4.  **Bandwidth Units:**  Assume that bandwidths are given in bytes per millisecond.
5.  **Data Size:** `data_size` should not directly factor into the path selection, it only serves to indicate a request is made.
6.  **Memory Constraints:** The solution should be memory-efficient, avoiding unnecessary data duplication or large auxiliary data structures.
7.  **Time Complexity:** The solution should be efficient in terms of time complexity. Aim for an algorithm with a complexity better than O(n^2) for finding the path.
8.  **Real-World Considerations:** The problem simulates a real-world network optimization scenario where both bandwidth and latency are critical factors.
9.  **Multiple Optimal Paths:** If multiple paths have the same optimal effective throughput, return any one of them.
10. **Practicality:** The choice of algorithm should be something reasonably practical for real-world networks.

**Example:**

```
n = 4
edges = [(0, 1, 100), (0, 2, 50), (1, 2, 75), (1, 3, 200), (2, 3, 150)]
source = 0
destination = 3
latency = {(0, 1): 10, (0, 2): 5, (1, 2): 8, (1, 3): 20, (2, 3): 12}
data_size = 1024 # irrelevant to path selection

path, throughput = optimize_network(n, edges, source, destination, latency, data_size)

# Possible optimal path and throughput (results may vary depending on implementation choices):
# path = [0, 1, 3]
# throughput = 100.0 / 30.0 = 3.3333 (approximately)
```

The challenge is to find an efficient algorithm and its Go implementation that balances bandwidth and latency to maximize effective throughput in a large and potentially complex network, while adhering to memory constraints and handling edge cases.
