## Problem: Decentralized Social Network Analysis

### Question Description

You are tasked with analyzing a decentralized social network built on a peer-to-peer (P2P) architecture. The network consists of nodes (users) and directed edges (follows).  Each node maintains only a partial view of the network, storing information about its immediate neighbors and a limited number of randomly selected "distant" nodes.  The network is constantly evolving, with nodes joining, leaving, and changing their connections.

Given a snapshot of this decentralized network, you need to implement a system to efficiently answer reachability queries: "Can user A reach user B within a specified number of hops?"  Due to the distributed nature and limited visibility of each node, you need to devise a strategy that balances accuracy with minimal network traversal.

**Data Representation:**

Each node in the network is represented by a unique integer ID. Your system will receive the network data in the following format:

*   **Node Data:** A list of tuples, where each tuple represents a node and its knowledge of the network. The tuple has the form `(node_id, neighbor_list, distant_node_list)`.
    *   `node_id`: The unique integer ID of the node.
    *   `neighbor_list`: A list of integer IDs representing the nodes that `node_id` directly follows.
    *   `distant_node_list`: A list of integer IDs representing a limited number of randomly selected distant nodes that `node_id` knows about.

**Reachability Query:**

A reachability query will be given as a tuple `(start_node, end_node, max_hops)`. Your system needs to determine if there exists a path from `start_node` to `end_node` with at most `max_hops`.

**Constraints and Requirements:**

1.  **Decentralized Knowledge:** You cannot assume that any single node has complete knowledge of the entire network. Your solution must work with the partial view provided by each node.
2.  **Scalability:** The network can be large (millions of nodes). Your solution should be designed to scale efficiently.  Avoid algorithms with time complexity that grows exponentially with the network size.
3.  **Accuracy vs. Efficiency Trade-off:**  A perfectly accurate reachability determination may require traversing a significant portion of the network, which is undesirable.  Your solution should aim for a high degree of accuracy while minimizing the number of nodes visited and the overall execution time. False positives are acceptable, but false negatives should be minimized.
4.  **Dynamic Network:** While you are analyzing a snapshot, consider that the underlying network is dynamic. Your data structures and algorithms should be adaptable to handle future updates (node additions, removals, and connection changes) with reasonable overhead.
5.  **Memory Limit:** The system has a limited memory. Avoid storing the entire network structure in a single centralized data structure if possible.

**Example:**

```python
node_data = [
    (1, [2, 3], [5]),  # Node 1 follows 2 and 3, knows about 5
    (2, [4], [6]),  # Node 2 follows 4, knows about 6
    (3, [4], [7]),  # Node 3 follows 4, knows about 7
    (4, [], [8]),  # Node 4 follows nobody, knows about 8
    (5, [6], [9]),  # Node 5 follows 6, knows about 9
    (6, [], [10]), # Node 6 follows nobody, knows about 10
    (7, [], [11]), # Node 7 follows nobody, knows about 11
    (8, [], [12]), # Node 8 follows nobody, knows about 12
]

# Query: Can node 1 reach node 4 within 3 hops?
query = (1, 4, 3)

# Expected Output: True (1 -> 2 -> 4 or 1 -> 3 -> 4)

# Query: Can node 1 reach node 10 within 4 hops?
query = (1, 10, 4)

# Possible path, 1->5->6->10, so expected output = True
```

**Deliverables:**

Implement a function `is_reachable(node_data, start_node, end_node, max_hops)` that takes the network data, start node, end node, and maximum hops as input, and returns `True` if `end_node` is reachable from `start_node` within `max_hops`, and `False` otherwise.  Your solution should prioritize scalability, accuracy, and efficiency, considering the constraints of a decentralized, dynamic network.
