## Project Name

```
optimal-network-deployment
```

## Question Description

You are tasked with designing a robust and cost-effective communication network for a sprawling smart city. The city is represented as a graph where nodes represent buildings and edges represent potential communication links between them. Each building has a specific data processing requirement (in terms of bandwidth and latency) and a cost associated with installing network infrastructure.

Your goal is to select a subset of buildings to host network servers and deploy communication links to connect *all* buildings in the city to at least one server, directly or indirectly. The network must meet certain stringent requirements:

*   **Connectivity**: Every building must be able to communicate with at least one server.
*   **Latency**: The maximum latency between any building and its nearest server must be below a certain threshold. Latency is calculated as the sum of edge weights (representing communication delay) along the shortest path.
*   **Bandwidth**: Each link needs to support the total bandwidth requirement of all buildings which the shortest path to any server goes through that link. The chosen link has a maximum bandwidth limit.
*   **Budget**: The total cost of installing servers and deploying links must be within a given budget.

Formally, you are given:

*   `n`: The number of buildings in the city.
*   `edges`: A list of tuples `(u, v, weight, bandwidth_limit)`, where `u` and `v` are building indices (0-indexed), `weight` is the latency of the link between `u` and `v`, and `bandwidth_limit` is the maximum bandwidth that the link can support.
*   `building_data`: A list of tuples `(processing_requirement, installation_cost)` for each building, where `processing_requirement` is the bandwidth requirement of that building and `installation_cost` is the cost of installing a server in that building.
*   `max_latency`: The maximum allowable latency between any building and its closest server.
*   `total_budget`: The maximum allowable cost for the network deployment.

Your task is to write a function that determines the **minimum number of servers** required to meet all connectivity, latency, bandwidth and budget requirements. If it's impossible to meet all requirements within the budget, return `-1`.

**Constraints:**

*   1 <= `n` <= 100
*   1 <= number of `edges` <= n * (n - 1) / 2
*   1 <= `weight` <= 100
*   1 <= `bandwidth_limit` <= 1000
*   1 <= `processing_requirement` <= 50
*   1 <= `installation_cost` <= 500
*   1 <= `max_latency` <= 500
*   1 <= `total_budget` <= 50000

**Optimization Requirement:**

The solution should be reasonably efficient. Naive brute-force solutions that explore all possible server placements are unlikely to pass all test cases within the time limit. Consider using algorithmic techniques such as dynamic programming, graph algorithms (Dijkstra, Floyd-Warshall), or approximation algorithms to improve performance.
