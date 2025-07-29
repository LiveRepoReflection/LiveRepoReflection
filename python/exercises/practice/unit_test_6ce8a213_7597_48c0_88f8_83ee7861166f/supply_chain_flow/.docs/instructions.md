## Problem: Decentralized Supply Chain Optimization

**Question Description:**

Imagine a decentralized supply chain network operating on a blockchain. This network consists of `n` nodes, each representing a different entity like a manufacturer, distributor, retailer, or consumer. Each node `i` has a limited storage capacity `capacity[i]` and a production/consumption rate `rate[i]`. A positive `rate[i]` indicates production, while a negative `rate[i]` indicates consumption.

The network topology is represented by a directed graph where edges `(u, v, weight)` indicate a possible transportation route from node `u` to node `v` with a transportation cost `weight`. There can be multiple edges between two nodes with differing weights, representing different transportation methods.

The goal is to design a system that efficiently distributes goods across the network to satisfy the demand at each node, minimizing the total transportation cost. However, due to the decentralized nature of the network, each node independently decides how much to send to its neighbors.

Your task is to implement an algorithm that finds the *optimal* flow distribution across the network, minimizing total transportation cost, subject to the following constraints:

1.  **Capacity Constraints:** The total amount of goods stored at any node `i` at any time *cannot* exceed `capacity[i]`. The initial storage at each node is assumed to be zero.
2.  **Flow Conservation:** For each node `i`, the net flow (inflow - outflow) plus the node's production/consumption rate `rate[i]` should be zero in steady state.
3.  **Non-negative Flow:** The flow along each edge must be non-negative.
4.  **Decentralized Decision-Making:** You do not have global knowledge of the supply chain or the node's decisions. You can only gather information by sending requests to a node, and each node will provide the cost and capacity information. Each node will try to minimize its cost of sending to neighbors.
5.  **Time Limit:** A solution must be found within a specific time limit (e.g., 60 seconds).
6.  **Scalability:** The algorithm should scale reasonably well with the number of nodes and edges in the network.
7.  **Cost Minimization:** The primary objective is to minimize the total cost of transportation across the entire network.

**Input:**

*   `n`: The number of nodes in the network. Nodes are numbered from 0 to `n-1`.
*   `capacity`: A list of integers of size `n`, where `capacity[i]` represents the storage capacity of node `i`.
*   `rate`: A list of integers of size `n`, where `rate[i]` represents the production/consumption rate of node `i`.
*   `edges`: A list of tuples `(u, v, weight)`, where `u` and `v` are the source and destination nodes respectively, and `weight` is the transportation cost per unit of goods. There can be multiple edges between two nodes with different weights.
*   `node_information_request(node_id)`: A function that allows you to request information from a specific node. It takes the `node_id` as input and returns a dictionary containing the following information:

    ```python
    {
        "capacity": capacity[node_id],
        "rate": rate[node_id],
        "outgoing_edges": [(neighbor_node_id, weight), ...] # List of tuples representing outgoing edges and their weights
    }
    ```

**Output:**

A dictionary representing the flow across each edge. The keys of the dictionary are tuples `(u, v, weight)` representing the edge, and the values are the flow along that edge.  If no feasible solution exists, return an empty dictionary `{}`.

**Example:**

```
n = 3
capacity = [100, 100, 100]
rate = [50, -25, -25]
edges = [(0, 1, 1), (0, 2, 2), (1, 2, 1)]

#Assumed call
node_information_request(0) # {"capacity": 100, "rate": 50, "outgoing_edges": [(1, 1), (2, 2)]}
node_information_request(1) # {"capacity": 100, "rate": -25, "outgoing_edges": [(2, 1)]}
node_information_request(2) # {"capacity": 100, "rate": -25, "outgoing_edges": []}

# Possible Optimal Output (not necessarily the only one)
# {(0, 1, 1): 25, (0, 2, 2): 25, (1, 2, 1): 0} # Total Cost: 25 * 1 + 25 * 2 + 0 * 1 = 75
```

**Constraints:**

*   `1 <= n <= 100`
*   `0 <= capacity[i] <= 1000`
*   `-500 <= rate[i] <= 500`
*   `0 <= weight <= 100`
*   The sum of `rate` must be 0 (total production equals total consumption).

**Judging Criteria:**

*   Correctness: The solution must satisfy all the constraints.
*   Cost Minimization: The solution should minimize the total transportation cost.  Solutions will be compared based on their cost, with lower costs being preferred.
*   Time Limit: The solution must run within the time limit.
*   Scalability: The solution should handle larger networks reasonably well.

This problem requires a combination of graph algorithms, optimization techniques, and careful consideration of the decentralized nature of the network. Good luck!
