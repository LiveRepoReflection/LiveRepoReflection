## Project Name

```
NetworkReliability
```

## Question Description

You are designing a critical communication network consisting of `n` nodes. Each node represents a server, and the connections between nodes represent communication links. Due to security vulnerabilities and hardware failures, these links are not perfectly reliable. Each link between two nodes `u` and `v` has a probability `p(u, v)` of being operational at any given time. If a link is not operational, no communication can occur between the two nodes it connects.

The network topology is given as a set of bidirectional edges (undirected graph). The goal is to determine the probability that all nodes in the network can communicate with each other, meaning that there exists a path (sequence of operational links) between any two nodes. In other words, the network must be a single connected component consisting of operational links.

More formally:

*   **Input:**
    *   `n`: The number of nodes in the network, numbered from 0 to `n-1`.
    *   `edges`: A vector of tuples, where each tuple `(u, v, p)` represents an edge between nodes `u` and `v` with operational probability `p`. `0 <= u, v < n`, and `0 <= p <= 1`.
*   **Output:**
    *   The probability that the network is fully connected, meaning there exists a path between any two nodes using operational links.

**Constraints:**

*   `1 <= n <= 10`
*   `0 <= edges.size() <= n*(n-1)/2`
*   All edge probabilities `p` are given to 6 decimal places of precision.
*   The graph represented by `edges` is simple (no self-loops, no duplicate edges).
*   The graph represented by `edges` is undirected. If `(u, v, p)` exists, there isn't also `(v, u, p)`.

**Optimization Requirements:**

*   Due to the small constraint of `n <= 10`, brute-force approaches are theoretically possible. However, naive brute-force solutions will likely exceed the time limit. Solutions should aim for computational efficiency by avoiding redundant calculations.

**Example:**

```
n = 3
edges = {(0, 1, 0.9), (1, 2, 0.8), (0, 2, 0.7)}
```

The possible operational states and their probabilities are:

*   All edges operational: `0.9 * 0.8 * 0.7 = 0.504`
*   (0, 1) and (1, 2) operational, (0, 2) failed: `0.9 * 0.8 * (1 - 0.7) = 0.216`
*   (0, 1) and (0, 2) operational, (1, 2) failed: `0.9 * (1 - 0.8) * 0.7 = 0.126`
*   (1, 2) and (0, 2) operational, (0, 1) failed: `(1 - 0.9) * 0.8 * 0.7 = 0.056`

The network is connected in all these cases. Therefore, the probability that the network is fully connected is `0.504 + 0.216 + 0.126 + 0.056 = 0.902`.

**Edge Cases to Consider:**

*   Empty graph (no edges).
*   Graph with a single node.
*   Disconnected graph.
*   Edges with probability 0 or 1.

**Judging Criteria:**

*   Correctness: The solution must accurately compute the probability.
*   Efficiency: The solution must execute within the time limit.
*   Code Clarity: The code should be well-structured and readable.

Good luck building a reliable network!
