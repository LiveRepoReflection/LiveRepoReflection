## The Intergalactic Network Routing Problem

**Problem Description:**

The Intergalactic Federation is expanding its network of interconnected planets. Each planet hosts a server that can communicate with other planets' servers, forming a vast, complex network. The network's architecture is based on a series of interconnected subnets, each managed independently and utilizing different routing protocols. The overall goal is to ensure efficient and reliable communication between any two planets in the Federation, despite the heterogeneity and potential instability of the subnets.

You are tasked with designing and implementing a routing service that can determine the optimal path between any two planets in the Intergalactic Federation. The network is represented as a multi-layered graph, where each layer represents a subnet. Planets can belong to multiple subnets. Connections within each subnet have varying costs (representing latency, bandwidth limitations, security concerns, etc.) that can change dynamically. Moreover, transferring data between subnets incurs a significant cost due to protocol translation and security checks.

Specifically:

*   **Planets:** Represented by unique integer IDs.
*   **Subnets:** Represented by unique integer IDs.
*   **Network Structure:** A planet can belong to multiple subnets. A subnet contains a graph of planets interconnected by edges with associated costs.
*   **Subnet Connections:** There is no explicit edge between two subnets. The connection between subnets is defined only implicitly through the planets they share.
*   **Edge Costs:** Represented by positive floating-point numbers. Costs within a subnet can change dynamically through updates (see below).
*   **Subnet Transfer Cost:** Represented by a positive floating-point number, `transfer_cost`. This cost is incurred every time the routing path switches from one subnet to another.
*   **Optimal Path:** The path with the lowest total cost, considering both edge costs within subnets and the subnet transfer costs.

**Input:**

Your solution will receive the following inputs:

1.  **Initial Network Configuration:**
    *   A list of planets: `planets = [1, 2, 3, ..., N]`
    *   A list of subnets: `subnets = [101, 102, 103, ..., M]`
    *   A mapping of planets to their subnets: `planet_to_subnets = {planet_id: [subnet_id1, subnet_id2, ...], ...}`
    *   A mapping of subnets to their graph representation: `subnet_graphs = {subnet_id: {planet_id1: [(planet_id2, cost), (planet_id3, cost), ...], ...}, ...}` where the inner dictionary represents the adjacency list of the subnet graph. Note that subnet graphs are undirected.
    *   A subnet transfer cost: `transfer_cost = float`

2.  **Routing Requests:**
    *   A source planet ID: `source_planet = int`
    *   A destination planet ID: `destination_planet = int`

3.  **Dynamic Updates:**
    *   Periodically, the edge costs within subnets may change. Your system must handle these updates efficiently. Updates are provided as a list of tuples: `edge_updates = [(subnet_id, planet_id1, planet_id2, new_cost), ...]`

**Output:**

For each routing request, your solution should output the optimal path (a list of planet IDs, in order from source to destination) and the total cost of that path. If no path exists, return `None, float('inf')`.

**Constraints and Requirements:**

*   **Efficiency:** The network can be very large (thousands of planets and subnets). Your routing algorithm must be efficient, especially for frequent routing requests and dynamic updates. Consider pre-computation techniques where appropriate, but balance this with the cost of updating these pre-computed structures.
*   **Accuracy:** The returned path must be the *optimal* path (lowest total cost), considering both edge costs and subnet transfer costs.
*   **Dynamic Updates:** Your system must efficiently handle dynamic updates to edge costs. Recomputing the entire routing table after each update is not acceptable.
*   **Scalability:** Your solution should be designed to scale to even larger networks in the future. Consider modular design and potential for parallelization.
*   **Edge Cases:** Handle cases where the source and destination planets are the same, no path exists, planets or subnets are invalid, etc.
*   **Memory Usage:** Be mindful of memory usage, especially for large networks.

**Example:**

```python
planets = [1, 2, 3, 4, 5, 6]
subnets = [101, 102]
planet_to_subnets = {
    1: [101],
    2: [101, 102],
    3: [101],
    4: [102],
    5: [102],
    6: [102]
}
subnet_graphs = {
    101: {
        1: [(2, 1.0), (3, 2.0)],
        2: [(1, 1.0), (3, 1.5)],
        3: [(1, 2.0), (2, 1.5)]
    },
    102: {
        2: [(4, 2.5), (5, 3.0)],
        4: [(2, 2.5), (5, 1.0), (6, 4.0)],
        5: [(2, 3.0), (4, 1.0), (6, 2.0)],
        6: [(4, 4.0), (5, 2.0)]
    }
}
transfer_cost = 5.0

source_planet = 1
destination_planet = 6

# Expected Output (example):
# Path: [1, 2, 5, 6]
# Cost: 1.0 + 5.0 + 3.0 + 2.0 = 11.0
```
