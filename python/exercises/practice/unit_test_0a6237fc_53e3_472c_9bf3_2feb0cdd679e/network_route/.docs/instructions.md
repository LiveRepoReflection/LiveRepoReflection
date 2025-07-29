## Question: Network Packet Routing Optimization

**Problem Description:**

You are tasked with designing an efficient packet routing algorithm for a large-scale communication network. The network consists of `N` nodes, where each node has a unique ID from `0` to `N-1`. The network topology is represented as a weighted, undirected graph. The weights on the edges represent the latency (in milliseconds) between two directly connected nodes.

Given a set of `K` packets that need to be routed, your goal is to minimize the average latency for all packets. Each packet has a source node (`src_node`) and a destination node (`dest_node`).  Packets can be routed independently.

**Constraints and Considerations:**

1.  **Large Network:** `N` can be as large as 10,000. The number of edges `M` in the graph can be up to 50,000.

2.  **Number of Packets:** `K` can be as large as 1,000.

3.  **Edge Weights:** Edge weights (latency) are positive integers and can be up to 1,000.

4.  **Dynamic Network:** The network topology (edges and weights) might change slightly between routing different sets of packets. These changes are infrequent but must be accounted for. You will receive a new graph representation before routing each set of `K` packets.

5.  **Optimization Requirement:** Your algorithm should minimize the *average* latency across all `K` packets. A naive shortest-path algorithm (like Dijkstra's) might not be optimal if it leads to congestion on certain edges.

6.  **Congestion Aware Routing:**  You need to incorporate a mechanism to avoid over-utilization of certain edges.  One potential approach is to introduce a "congestion penalty" to the edge weights based on the current number of packets using that edge.

7.  **Time Limit:** Your solution must complete within a strict time limit (e.g., 10 seconds) for each set of `K` packets. This necessitates efficient algorithms and data structures.

8.  **Packet Serialization:**  Assume that packets can be split and recombined at nodes, so the order of transmission of packets over an edge does not matter.  You only need to consider the *number* of packets using a particular edge.

9. **Initial State:** Initially, no packets are routed. Your congestion calculation must account for this.

**Input Format:**

The input will be provided in the following format:

*   `N`: The number of nodes in the network.
*   `M`: The number of edges in the network.
*   `edges`: A list of `M` tuples, where each tuple represents an edge: `(node1, node2, latency)`. Nodes are identified by their IDs (0 to N-1).
*   `K`: The number of packets to route.
*   `packets`: A list of `K` tuples, where each tuple represents a packet: `(src_node, dest_node)`.

**Output Format:**

Your program should output a single floating-point number, representing the *minimum average latency* for routing all `K` packets, rounded to six decimal places. For each packet, determine the route that contributes to the lowest total average latency.

**Example:**

```
N = 4
M = 4
edges = [(0, 1, 10), (1, 2, 10), (0, 3, 1), (3, 2, 10)]
K = 2
packets = [(0, 2), (1,3)]
```

In this example, with N=4, nodes are 0,1,2,3.
Edges are 0-1 with 10ms, 1-2 with 10ms, 0-3 with 1ms and 3-2 with 10ms.
There are K=2 packets to route.
First packet is from 0 to 2.
Second packet is from 1 to 3.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

*   **Correctness:** The average latency must be calculated correctly.
*   **Efficiency:** The solution must complete within the time limit for large inputs.
*   **Optimization:** The solution should minimize the average latency as much as possible. Solutions that significantly outperform others will be ranked higher.
*   **Congestion Avoidance:** Solutions that effectively avoid congestion will be preferred.

**This problem requires a sophisticated approach that combines graph algorithms, dynamic programming, and potentially some form of iterative optimization or simulation to find the best routing strategy under congestion constraints.** Good luck!
