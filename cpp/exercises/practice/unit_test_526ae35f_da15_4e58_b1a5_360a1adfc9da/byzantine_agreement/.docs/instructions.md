## The Byzantine Agreement Protocol Simulator

**Question Description:**

You are tasked with building a simulator for a simplified version of the Byzantine Agreement protocol. This protocol is designed to allow a group of nodes in a distributed system to reach a consensus on a single value, even if some of the nodes are faulty (Byzantine).

**Simplified Protocol:**

1.  **The Leader:** One node is designated as the leader. The leader proposes a value (either 0 or 1) to all other nodes.
2.  **The Lieutenants:** Each other node (lieutenant) receives the value from the leader.
3.  **Relaying:** Each lieutenant then relays the value it received to all other lieutenants.
4.  **Majority Vote:** Each lieutenant now has a set of values received from all other lieutenants (including possibly from itself). It takes a majority vote on these values. If the majority is 0, it decides on 0. If the majority is 1, it decides on 1. If there is a tie, it decides on 0.

**Faulty Nodes:**

*   Faulty nodes (both the leader and the lieutenants) can behave arbitrarily. They might send different values to different nodes, or not send any value at all.

**Your Task:**

Write a function `simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value)` that simulates this protocol and returns the number of nodes that decide on 1.

**Input:**

*   `num_nodes`: An integer representing the total number of nodes in the system (including the leader). Nodes are numbered from 0 to `num_nodes - 1`.
*   `faulty_nodes`: A set of integers representing the IDs of the faulty nodes.
*   `leader_id`: An integer representing the ID of the leader node.
*   `proposed_value`: The value (0 or 1) the leader *should* propose (but might not, if it's faulty).

**Constraints:**

*   `1 <= num_nodes <= 1000`
*   `0 <= faulty_nodes.size() <= num_nodes`
*   `0 <= leader_id < num_nodes`
*   `proposed_value` is either 0 or 1.
*   The time complexity of your solution must be at most O(N^2), where N is the number of nodes.

**Output:**

*   An integer representing the number of nodes that decide on 1.

**Example:**

```cpp
int num_nodes = 4;
std::set<int> faulty_nodes = {0}; // Node 0 is faulty (the leader)
int leader_id = 0;
int proposed_value = 1; // The leader should propose 1

int agreed_ones = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
// agreed_ones could be anything between 0 and 3, depending on the leader's behavior.
```

**Challenge:**

*   Consider how faulty nodes can strategically send conflicting information to manipulate the outcome of the vote.
*   Optimize your solution for efficiency, especially when dealing with a larger number of nodes.
*   Think carefully about edge cases and how to handle them gracefully. For example, what happens if all nodes are faulty?
*   You need to simulate the behavior of the nodes based on whether they are faulty or not. Faulty nodes can send arbitrary messages.
*   Assume that the network is fully connected, meaning that every node can directly communicate with every other node.
