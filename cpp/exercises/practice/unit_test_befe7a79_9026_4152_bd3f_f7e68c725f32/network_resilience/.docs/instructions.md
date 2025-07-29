Okay, I'm ready. Here is your hard-level C++ coding problem:

**Problem Title: Network Partitioning for Maximum Resilience**

**Problem Description:**

You are tasked with designing a resilient communication network for a distributed system. The network consists of `N` nodes (numbered from 0 to N-1) and `M` bidirectional communication links. Each link connects two nodes and has an associated cost representing the difficulty or risk involved in maintaining that link.

Due to potential failures and external attacks, the network may need to be partitioned into multiple disjoint sub-networks. The resilience of a sub-network is defined as the minimum cost of a link within that sub-network.  If a sub-network contains no links, its resilience is considered to be positive infinity.

The overall resilience of the partitioned network is the *minimum* resilience across all sub-networks.

Your goal is to find the *maximum possible* overall resilience that can be achieved by partitioning the network. You are allowed to partition the network into any number of disjoint sub-networks, or even leave the network unpartitioned (one single sub-network).

**Input:**

*   `N`: An integer representing the number of nodes in the network. (1 <= N <= 10<sup>5</sup>)
*   `edges`: A vector of tuples, where each tuple `(u, v, cost)` represents a bidirectional communication link between node `u` and node `v` with cost `cost`. (0 <= u, v < N, 1 <= cost <= 10<sup>9</sup>, 0 <= M <= 2 * 10<sup>5</sup>)  There will be no duplicate edges (u,v) and (v,u).

**Output:**

*   An integer representing the maximum possible overall resilience that can be achieved by partitioning the network.

**Constraints and Considerations:**

*   **Efficiency:**  The solution must be efficient enough to handle large networks (up to 10<sup>5</sup> nodes and 2 * 10<sup>5</sup> edges) within a reasonable time limit (e.g., a few seconds). Inefficient solutions (e.g., brute-force approaches that explore all possible partitions) will likely time out.
*   **Connectivity:** The original network is not necessarily fully connected.
*   **Edge Cases:**  Handle cases where the network has no edges or consists of only a few nodes.
*   **Integer Overflow:** Be mindful of potential integer overflows when dealing with large costs.
*   **Multiple Optimal Solutions:** There might be multiple ways to partition the network that achieve the maximum overall resilience. Your solution only needs to find the maximum resilience value.
*   **Disconnected Subnetworks:** Consider subnetworks with no links in them. They have infinite resilience.
*   **Unpartitioned Graph:** Consider the case when the graph is not partitioned at all.
*   **Assume valid input:** You do not need to error check for invalid input such as negative N, or node indices out of range.
