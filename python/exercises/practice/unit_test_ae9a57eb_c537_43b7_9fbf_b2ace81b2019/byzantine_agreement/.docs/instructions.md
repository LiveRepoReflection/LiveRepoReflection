## The Byzantine Agreement Protocol Simulation

### Question Description

You are tasked with simulating a simplified version of the Byzantine Agreement protocol. Imagine a network of `N` nodes, where `N` is always an odd number. These nodes need to agree on a single binary value (0 or 1). However, some nodes are faulty (Byzantine), meaning they can send conflicting or incorrect information to different nodes. The goal is to design an algorithm that allows the loyal (non-faulty) nodes to reach a consensus on the correct value, even in the presence of faulty nodes.

**Simplified Protocol:**

1.  **Leader Election:** One node is pre-designated as the leader.
2.  **Leader Proposal:** The leader proposes a value (0 or 1) to all other nodes.
3.  **Value Relaying:** Each node (including the leader, if it's loyal) relays the value it received from the leader to all other nodes. If a faulty node is relaying, it can send different values to different nodes.
4.  **Majority Vote:** Each node tallies the values it received from all other nodes. The value with the majority is the decision of that node.

**Constraints:**

*   The number of faulty nodes, `F`, is strictly less than `(N - 1) / 2`. This ensures that loyal nodes will always form a majority.
*   The simulation should handle a large number of nodes (up to 10,000) and a significant proportion of faulty nodes (up to the allowed maximum `F`).
*   The solution must be computationally efficient. Inefficient solutions may time out.
*   Input is provided as an adjacency list representing the network, the leader node, the leader's proposed value, and the set of faulty nodes.
*   All nodes are identified by unique integer IDs from 0 to N-1.

**Input:**

*   `N`: The total number of nodes in the network.
*   `leader`: The ID of the leader node.
*   `proposed_value`: The binary value (0 or 1) proposed by the leader.
*   `faulty_nodes`: A set of node IDs that are faulty.
*   `network`: A list of lists representing the adjacency list of the network. `network[i]` contains a list of node IDs that node `i` can send messages to.

**Output:**

*   A dictionary where the key is the node ID and the value is the final decision (0 or 1) reached by that node.

**Example:**

```
N = 5
leader = 0
proposed_value = 1
faulty_nodes = {1}
network = [
    [1, 2, 3, 4], # Node 0 can send to 1, 2, 3, 4
    [0, 2, 3, 4], # Node 1 can send to 0, 2, 3, 4
    [0, 1, 3, 4], # Node 2 can send to 0, 1, 3, 4
    [0, 1, 2, 4], # Node 3 can send to 0, 1, 2, 4
    [0, 1, 2, 3]  # Node 4 can send to 0, 1, 2, 3
]

# Expected output (can vary due to faulty node behavior):
# {0: 1, 1: 1, 2: 1, 3: 1, 4: 1} (or some decisions could be 0)
```

**Requirements:**

*   Your solution must handle the possibility of faulty nodes sending different values to different nodes during the relaying phase. A faulty node should be able to propose different values.
*   Your solution must be efficient enough to handle large networks with a significant number of faulty nodes without timing out. Consider the complexity of your algorithm.
*   Your solution must be robust and handle various edge cases, such as an empty network, a leader being faulty, or a network where a node cannot reach all other nodes.
*   You are free to choose the method a faulty node sends different values.

This problem challenges you to implement a distributed system simulation that addresses the fundamental problem of achieving consensus in the presence of unreliable actors. Good luck!
