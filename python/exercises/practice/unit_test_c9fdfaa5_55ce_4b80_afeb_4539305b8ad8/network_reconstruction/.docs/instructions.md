## Question: Optimal Network Reconstruction

### Question Description

You are tasked with reconstructing a network of interconnected servers based on limited information. The network consists of `n` servers, labeled from `0` to `n-1`. The connections between servers are bidirectional.

You are given a set of observed network latency measurements. Each measurement is a tuple `(u, v, latency)`, where `u` and `v` are server labels and `latency` is the measured latency between them.

However, the measurements are incomplete and potentially noisy:

1.  **Incomplete Data:** Not all server pairs have latency measurements. If a pair `(u, v)` doesn't appear in the input, it doesn't necessarily mean they are not connected; it simply means you don't have a direct measurement.
2.  **Noisy Data:** The latency values might not perfectly reflect the actual shortest path latency in the network due to network congestion or measurement errors.
3.  **Connectivity Assumption:** The network is assumed to be connected, meaning there is at least one path between any two servers.

Your goal is to reconstruct a network represented as an adjacency list, minimizing the overall "discrepancy" between the reconstructed network's shortest path latencies and the observed latencies.

**Input:**

*   `n`: An integer representing the number of servers (1 <= `n` <= 100).
*   `measurements`: A list of tuples `(u, v, latency)`, where `u` and `v` are server labels (0 <= `u`, `v` < `n`, `u` != `v`) and `latency` is a floating-point number (0.0 < `latency` <= 100.0). Measurements are bidirectional - if (u, v, latency) is provided, assume (v, u, latency) is also observed.

**Output:**

*   `adj_list`: A list of lists representing the reconstructed network's adjacency list. `adj_list[i]` should be a list of tuples `(neighbor, latency)` representing the neighbors of server `i` and the latency to reach them. The neighbors should be sorted by server label.

**Objective Function:**

The goal is to minimize the following discrepancy score:

`Discrepancy = sum((shortest_path_latency(u, v) - observed_latency(u, v))^2)`

where:

*   `shortest_path_latency(u, v)` is the shortest path latency between servers `u` and `v` in the reconstructed network. Use Dijkstra's algorithm to compute this.
*   `observed_latency(u, v)` is the latency between servers `u` and `v` from the input measurements. If there is no direct measurement for `(u, v)`, set `observed_latency(u, v)` to infinity.

**Constraints:**

1.  You can add edges that are not present in the measurements.
2.  You can remove edges that are present in the measurements if it reduces the discrepancy.
3.  The reconstructed network *must* be connected. If your reconstruction results in a disconnected graph, return an empty list (`[]`).
4.  There might be multiple optimal solutions. Return any one of them.
5.  Your solution's execution time should be reasonable (under 10 seconds).

**Example:**

```python
n = 3
measurements = [(0, 1, 1.0), (1, 2, 2.0)]

# Possible optimal output (one of many):
adj_list = [
    [(1, 1.0)],
    [(0, 1.0), (2, 2.0)],
    [(1, 2.0)]
]
```

In the above example, the shortest path latency between 0 and 2 is 1.0 + 2.0 = 3.0. There is no direct measurement for the edge (0,2), so the observed latency is infinity.

**Note:** This problem does not have a single correct answer. The judge will evaluate the quality of your solution based on how well it minimizes the discrepancy score. The more tests your solution passes within the time limit, the higher you will be ranked.
