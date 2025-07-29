## Project Name

**Decentralized Social Network Graph Analytics**

## Question Description

You are tasked with building a system to analyze a large, decentralized social network represented as a graph. Due to the decentralized nature, the graph data is fragmented and stored across multiple independent nodes (servers). Your goal is to perform complex graph analytics operations, specifically, computing the approximate PageRank for all users in the network, considering the constraints of distributed data and limited inter-node communication.

**Graph Representation:**

*   The social network consists of `N` users, uniquely identified by integers from `0` to `N-1`.
*   The network's connections (friendships, follows, etc.) are represented as a directed graph. A directed edge from user `u` to user `v` indicates that user `u` "follows" or "influences" user `v`.
*   The graph data is partitioned across `K` nodes. Each node stores a subset of the users and their outgoing edges (who they follow). A user and their outgoing edges reside entirely on a single node.
*   You are given a list of nodes, with each node described by:

    *   A list of user IDs that the node contains.
    *   A dictionary representing the outgoing edges for each user on that node. For example, `{user_id: [followed_user_id1, followed_user_id2, ...], ...}`.  If a user has no outgoing edges, they will not appear as a key in the dictionary.
*   Nodes can only communicate by sending messages to each other. Message size is limited, so minimize the data transferred.

**PageRank Approximation:**

Implement an iterative PageRank algorithm to approximate the PageRank score for each user. Due to the scale and distributed nature, achieving perfect convergence is impractical. Aim for a reasonable approximation within a limited number of iterations.

**Specific Requirements and Constraints:**

1.  **Distributed Computation:** The PageRank calculation must be performed in a distributed manner, leveraging the data stored on each node.
2.  **Limited Communication:** Minimize the amount of data transferred between nodes. Communication is costly, and large messages are prohibited. Specifically, assume each node has a maximum message size of O(sqrt(N)), where N is the total number of users. Violating this constraint will result in penalty.
3.  **Partial Data:** Each node only has information about its local users and their *outgoing* edges. Nodes do not know about incoming edges directly.
4.  **Damping Factor:** Use a damping factor (d) of 0.85.
5.  **Convergence:** Due to the distributed and approximate nature, a strict convergence check is not required. Instead, run the PageRank algorithm for a fixed number of iterations (e.g., 20-50 iterations).
6.  **Initial PageRank:** Initialize all users with a PageRank of `1/N`.
7.  **Handling Dangling Nodes:** Address the issue of "dangling nodes" (users with no outgoing edges) correctly.  Their PageRank mass must be distributed properly.
8.  **Memory Efficiency:** The solution should be memory-efficient, especially on individual nodes. Avoid loading the entire graph structure into a single node's memory.
9.  **Edge Cases:** Handle cases where some nodes might contain no users, or where the graph is disconnected.
10. **Time Complexity:** Aim for the best possible runtime complexity given the constraints. Naive solutions will timeout. Think about efficient ways to aggregate and distribute PageRank scores.

**Input:**

*   `K`: The number of nodes.
*   `nodes`: A list of dictionaries, where each dictionary represents a node. Each node dictionary has the following keys:
    *   `users`: A list of integers representing the user IDs stored on the node.
    *   `edges`: A dictionary where keys are user IDs on the node and values are lists of user IDs that the key user follows.
*   `N`: The total number of users in the network.
*   `iterations`: The number of PageRank iterations to perform.

**Output:**

*   A dictionary where keys are user IDs (integers from 0 to N-1) and values are their approximate PageRank scores (floating-point numbers).  The PageRank scores should sum approximately to 1.

**Example:**

```python
K = 2
nodes = [
    {'users': [0, 1], 'edges': {0: [1], 1: [0, 2]}},
    {'users': [2, 3], 'edges': {2: [3], 3: []}}
]
N = 4
iterations = 20

# Expected Output (approximate):
# {0: 0.22, 1: 0.22, 2: 0.22, 3: 0.34} (scores will vary slightly)
```

**Judging Criteria:**

*   Correctness: The PageRank scores must be reasonably accurate approximations of the true PageRank.
*   Efficiency: The solution must complete within a reasonable time limit (e.g., 1-2 minutes for large graphs).
*   Communication Cost: Solutions that minimize inter-node communication will be favored.
*   Memory Usage: The solution must be memory-efficient and not exhaust the available memory on individual nodes.
*   Handling of Edge Cases: The solution must handle all edge cases gracefully.
*   Code Clarity and Structure: The code should be well-structured, readable, and maintainable.
