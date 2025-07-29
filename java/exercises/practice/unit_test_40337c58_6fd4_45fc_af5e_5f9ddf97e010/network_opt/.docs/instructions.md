## Project Name

`NetworkOptimization`

## Question Description

You are tasked with designing an efficient communication network for a large-scale distributed system. The system consists of `n` nodes, each identified by a unique integer ID from `0` to `n-1`. These nodes need to exchange data frequently, and the network's performance is crucial for the overall system efficiency.

The network is built upon a set of bidirectional communication links. Each link connects two nodes and has an associated cost representing the latency or bandwidth usage. The goal is to establish a communication infrastructure that minimizes the average latency between any two nodes while adhering to specific constraints.

You are given the following inputs:

*   `n` (integer): The number of nodes in the network.
*   `edges` (List of Lists of Integers): A list of edges, where each edge is represented as a list `[node1, node2, cost]`, indicating a bidirectional link between `node1` and `node2` with the given `cost`.
*   `k` (integer): The maximum number of links allowed in the final network configuration.  You *must* use no more than `k` links.  Using fewer than `k` links is acceptable.

Your task is to find a subset of at most `k` edges from the given `edges` list to construct a network that minimizes the *average shortest path* between all pairs of nodes.

The *average shortest path* is defined as the sum of the shortest path lengths between all pairs of distinct nodes, divided by the total number of distinct node pairs (`n * (n - 1) / 2`). If two nodes are unreachable, the shortest path between them is considered to be infinite. If any pair of nodes are unreachable in your final network, your algorithm must return `Double.MAX_VALUE`.

**Constraints:**

*   `2 <= n <= 100`
*   `0 <= edges.length <= n * (n - 1) / 2`
*   `0 <= edges[i][0], edges[i][1] < n`
*   `1 <= edges[i][2] <= 1000`
*   `edges[i][0] != edges[i][1]`
*   `1 <= k <= edges.length`
*   There will not be duplicate edges in the `edges` input.  That is, there will not be two entries with identical `node1` and `node2` values.

**Optimization Requirements:**

*   The solution must be computationally efficient, as the number of possible edge combinations can be large.  Brute-force approaches will likely time out.
*   Consider that the graph is not necessarily complete.
*   The cost represents the latency of a link, and your solution should aim to minimize the *average* latency across all node pairs.

**Example:**

`n = 4`
`edges = [[0, 1, 1], [0, 2, 5], [1, 2, 2], [1, 3, 1], [2, 3, 3]]`
`k = 4`

One possible solution could be to choose edges `[[0, 1, 1], [1, 2, 2], [1, 3, 1], [2, 3, 3]]`. The average shortest path length for this network would be computed as follows:

*   Shortest path between 0 and 1: 1
*   Shortest path between 0 and 2: 1 + 2 = 3
*   Shortest path between 0 and 3: 1 + 1 = 2
*   Shortest path between 1 and 2: 2
*   Shortest path between 1 and 3: 1
*   Shortest path between 2 and 3: 3

Sum of shortest paths: 1 + 3 + 2 + 2 + 1 + 3 = 12
Number of node pairs: 4 \* 3 / 2 = 6
Average shortest path: 12 / 6 = 2.0

Your function should return the minimum average shortest path achievable with at most `k` edges.
