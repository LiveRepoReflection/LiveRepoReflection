## Project Name

`NetworkPartitioning`

## Question Description

You are given a representation of a large communication network. The network consists of `N` nodes, labeled from `0` to `N-1`, and `M` undirected edges connecting these nodes. Each node represents a server, and each edge represents a direct communication link between two servers.

Due to a recent cyberattack, some of the communication links in the network have become unreliable. You are given a list of `K` edges that are considered "compromised". These compromised edges are prone to failure and should be avoided if possible.

Your task is to determine the minimum number of additional servers (nodes) that need to be *added* to the network and connected in such a way that allows all the original servers to communicate, without relying on any of the compromised edges.

You can add new servers and connect them to any number of existing or newly added servers. The goal is to minimize the number of added servers.

More formally:

1.  **Input:**
    *   `N`: The number of original servers in the network (indexed from 0 to N-1).
    *   `M`: The total number of edges in the initial network.
    *   `edges`: A vector of pairs representing the initial edges in the network. Each pair `(u, v)` represents an undirected edge between server `u` and server `v`.
    *   `K`: The number of compromised edges.
    *   `compromised_edges`: A vector of pairs representing the compromised edges. Each pair `(u, v)` represents a compromised undirected edge between server `u` and server `v`.

2.  **Output:**
    *   The minimum number of additional servers required to ensure all original servers can communicate without using any compromised edges.

**Constraints:**

*   `1 <= N <= 10^5`
*   `0 <= M <= min(2 * 10^5, N * (N - 1) / 2)`
*   `0 <= K <= M`
*   `0 <= u, v < N` for all edges.
*   There are no duplicate edges in `edges` or `compromised_edges`.
*   A compromised edge can be also in edges.

**Efficiency Requirements:**

Your solution must be efficient enough to handle large networks. Aim for a solution with a time complexity of O(N + M), or similar, by using appropriate data structures and algorithms. Consider potential bottlenecks in your code and optimize accordingly.

**Example:**

```
N = 6
M = 7
edges = {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}, {0, 5}, {1, 4}}
K = 2
compromised_edges = {{1, 4}, {2, 3}}

Output: 0
```

In the above example, even after removing the compromised edges, all nodes are still connected through the path `0 - 1 - 2 - 3 - 4 - 5 - 0`

```
N = 5
M = 3
edges = {{0, 1}, {2, 3}, {3, 4}}
K = 1
compromised_edges = {{2, 3}}

Output: 1
```

In the above example, after removing the compromised edge {2,3}, we have two components {0,1} and {2,3,4}. We can add a new server and connect it to one server from each component. This requires us to add 1 server. For example, we can add server 5 and connect it to server 0 and server 2, which will ensure all servers are connected.

**System Design Aspects:**

Consider how your solution would scale to handle extremely large networks with millions of nodes and edges. Are there any design considerations that would improve the robustness and performance of your solution in a real-world distributed system? (This doesn't have to be implemented, just considered in your approach).
