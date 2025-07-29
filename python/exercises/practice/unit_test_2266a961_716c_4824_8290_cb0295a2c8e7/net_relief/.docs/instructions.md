Okay, here's a challenging problem designed to test a strong understanding of graph algorithms, data structures, and optimization techniques.

## Project Name

`NetworkCongestionMitigation`

## Question Description

You are tasked with designing a system to mitigate network congestion in a large-scale data center. The data center network can be represented as a directed graph where:

*   Nodes represent servers.
*   Edges represent network connections between servers. Each edge has a *capacity* (maximum bandwidth) and a *current utilization* (amount of bandwidth currently being used).

Due to unforeseen circumstances, a subset of servers (the "affected servers") are experiencing a surge in traffic. This surge is causing congestion in the network, potentially leading to performance degradation and service disruptions.

Your goal is to design an algorithm that efficiently reroutes traffic to alleviate congestion around the affected servers. To achieve this, you must:

1.  **Identify Congested Edges:** An edge is considered congested if its current utilization exceeds a given *congestion threshold* (a percentage of its capacity).
2.  **Reroute Traffic:** For each affected server, determine a new route to all other servers it needs to communicate with. The new route must avoid congested edges as much as possible.
3.  **Minimize Impact:** The rerouting should minimize the overall increase in path lengths (number of hops) compared to the original routes. This is to prevent introducing excessive latency.
4.  **Capacity Constraints:** Ensure that the rerouted traffic does not exceed the capacity of any edge.
5.  **Fairness:** Distribute the rerouted traffic as evenly as possible across available paths to avoid creating new congestion hotspots.

**Input:**

*   `graph`: A dictionary representing the network graph. Keys are server IDs (integers). Values are dictionaries representing outgoing edges. Each outgoing edge dictionary has the format: `{destination_server_id: {"capacity": int, "utilization": int}}`.
*   `affected_servers`: A list of server IDs (integers) that are experiencing traffic surges.
*   `congestion_threshold`: A float between 0 and 1 representing the percentage of capacity that, when exceeded by utilization, indicates congestion.
*   `communication_matrix`: A dictionary where keys are affected server IDs and values are sets of server IDs that the affected server needs to communicate with.
*   `weights`: A dictionary where keys are tuples of source and destination server IDs `(source_server_id, destination_server_id)` and values are traffic weights (integers) indicating the amount of traffic that needs to be routed between the two servers.

**Output:**

A dictionary representing the proposed changes to the network. The keys are edge tuples `(source_server_id, destination_server_id)`. Values are the *change* in utilization on that edge (positive for increased utilization, negative for decreased). The returned dictionary should only include edges where the utilization changes.

**Constraints:**

*   The graph can be large (up to 10,000 nodes and 50,000 edges).
*   The number of affected servers can be up to 100.
*   The algorithm must run within a reasonable time limit (e.g., 5 minutes).
*   The solution should be as close to optimal as possible in terms of minimizing the increase in path lengths.
*   The input graph is guaranteed to be connected (there is a path between any two servers).
*   The traffic weights are positive integers.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The algorithm must correctly identify congested edges and reroute traffic without violating capacity constraints.
*   **Efficiency:** The algorithm must run within the time limit, even for large graphs.
*   **Optimality:** The algorithm should minimize the overall increase in path lengths.
*   **Fairness:** The traffic should be distributed as evenly as possible across available paths.
*   **Readability:** The code should be well-structured and easy to understand.

**Hints:**

*   Consider using Dijkstra's algorithm or A\* search to find alternative paths.
*   Think about how to represent the graph in a way that allows for efficient updates to edge capacities and utilizations.
*   Explore the use of flow networks and max-flow algorithms for traffic distribution.
*   Prioritize rerouting traffic from the most congested edges first.
*   Consider using heuristics to guide the search for alternative paths.

This problem requires a combination of algorithmic knowledge, data structure design, and optimization techniques. Good luck!
