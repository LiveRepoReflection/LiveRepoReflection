## Question: Network Partitioning for High Availability

**Problem Description:**

You are designing a distributed database system for a critical financial application. The system consists of `N` nodes, each identified by a unique integer from `0` to `N-1`.  Due to various reasons (network failures, security concerns, scheduled maintenance, etc.), the network may need to be partitioned into multiple isolated sub-networks.

Your task is to implement a function that determines the minimum number of nodes that need to be *additionally* configured to act as gateways between two *specific* subnetworks to guarantee data availability and consistency.

**Specifics:**

1.  **Network Representation:** The initial network topology is represented by an adjacency matrix `adj_matrix: Vec<Vec<bool>>`. `adj_matrix[i][j] == true` if there's a direct network link between node `i` and node `j`; otherwise, it's `false`. The matrix is symmetric, and `adj_matrix[i][i] == false` for all `i`.

2.  **Subnetworks:** You are given two sets of nodes, `subnetwork1: Vec<usize>` and `subnetwork2: Vec<usize>`, representing the two subnetworks that need to communicate.  These subnetworks are *guaranteed* to be completely disconnected in the initial network.  That is, there is *no* path between any node in `subnetwork1` and any node in `subnetwork2` using only the existing connections in `adj_matrix`.

3.  **Gateways:** To enable communication between the two subnetworks, you can configure additional nodes to act as gateways. A gateway node, once configured, can communicate directly with *any* node in *either* subnetwork.  You can choose *any* node from the *entire* network (including nodes already in either subnetwork) to be a gateway.

4.  **Goal:** Find the minimum number of gateway nodes required to ensure that *every* node in `subnetwork1` can communicate with *every* node in `subnetwork2`. Communication means that there is a path between those two nodes through the network, including the added gateways.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes in the network)
*   `1 <= subnetwork1.len() <= N`
*   `1 <= subnetwork2.len() <= N`
*   `subnetwork1` and `subnetwork2` contain distinct nodes.
*   Nodes in `subnetwork1` and `subnetwork2` are valid node IDs (0 to N-1).
*   The adjacency matrix accurately reflects the initial network topology.

**Optimization Requirements:**

*   Your solution should be reasonably efficient.  A naive brute-force approach might not pass all test cases, especially for larger networks. Consider algorithmic efficiency when selecting data structures and algorithms.

**Real-World Considerations:**

*   The choice of gateway nodes can impact network latency and security.  In this simplified problem, we only focus on minimizing the *number* of gateways, not their specific placement beyond the minimal connectivity requirement.

**Example:**

```
N = 5
adj_matrix = [
    [false, true, false, false, false],
    [true, false, true, false, false],
    [false, true, false, false, false],
    [false, false, false, false, true],
    [false, false, false, true, false],
]
subnetwork1 = [0, 1, 2]
subnetwork2 = [3, 4]

Minimum Gateway Nodes Required: 1
```

Explanation: By selecting *any* node in either `subnetwork1` or `subnetwork2` to be a gateway, every node in `subnetwork1` can communicate with every node in `subnetwork2`. For example, if node `0` is a gateway, it can directly communicate with all nodes in `subnetwork1` and `subnetwork2`, hence connecting the two subnetworks.

**Your Task:**

Implement the following function in Rust:

```rust
fn min_gateway_nodes(
    n: usize,
    adj_matrix: &Vec<Vec<bool>>,
    subnetwork1: &Vec<usize>,
    subnetwork2: &Vec<usize>,
) -> usize {
    // Your implementation here
}
```
