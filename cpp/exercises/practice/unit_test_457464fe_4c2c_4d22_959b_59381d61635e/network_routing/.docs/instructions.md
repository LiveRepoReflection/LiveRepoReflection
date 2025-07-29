## Project Name

`OptimalNetworkRouting`

## Question Description

A large telecommunications company, "GlobalConnect," is responsible for managing a vast network of fiber optic cables connecting numerous cities across the globe. The network is represented as a weighted undirected graph, where cities are nodes and cables are edges with associated costs (representing latency and bandwidth limitations).

GlobalConnect has a massive amount of data that needs to be transferred between different data centers located in various cities within the network.  Due to the sheer volume of data, multiple data transfers need to occur concurrently. Each data transfer is defined by a source city, a destination city, and the amount of data to be transferred.

GlobalConnect needs to optimize the routing of these data transfers to minimize the overall network congestion and cost. Network congestion is defined as the maximum "load" on any single cable in the network, where "load" is the sum of data flowing through that cable. The cost is the sum of costs of the cables used for data transfers.

You are tasked with designing an algorithm to determine the optimal routing for these concurrent data transfers.

**Specifics:**

*   **Input:**
    *   A graph represented as an adjacency list where each key is a city (string) and the value is a list of pairs. Each pair contains a neighboring city (string) and the cost (integer) of the cable connecting them.
    *   A list of data transfers. Each data transfer is a tuple containing the source city (string), the destination city (string), and the amount of data (integer) to be transferred.
*   **Output:**
    *   The minimum possible sum of network congestion and cost, given the optimal routing of all data transfers. You should aim for minimizing network congestion primarily, and cost secondarily if multiple routings have the same minimum congestion.

**Constraints:**

*   The number of cities (nodes) in the graph can be up to 100.
*   The number of cables (edges) in the graph can be up to 500.
*   The cost of each cable is a positive integer between 1 and 100.
*   The number of data transfers can be up to 20.
*   The amount of data to be transferred for each transfer is a positive integer between 1 and 50.
*   The graph is guaranteed to be connected.
*   There might be multiple cables between the same cities with different costs.

**Optimization Requirements:**

*   Your solution should aim for optimal routing. A heuristic approach with reasonable performance is acceptable if finding the true optimal solution is computationally infeasible within a reasonable time limit (e.g., 5 seconds).
*   Consider the trade-offs between different routing algorithms (e.g., Dijkstra, Bellman-Ford, Floyd-Warshall) and their impact on performance, especially given the need to handle multiple concurrent data transfers.
*   Efficient data structures and algorithms are crucial for handling large inputs within the time constraints.

**Edge Cases:**

*   Handle cases where there is no path between a source and destination city for a given data transfer. In such cases, the overall score should be considered as infinitely high (e.g., return `std::numeric_limits<double>::infinity()`).
*   Consider cases where multiple optimal routes exist for a given data transfer. Your algorithm should consistently choose one of these optimal routes.
*   Handle cases where the graph contains cycles.

**System Design Aspects:**

*   Think about how your solution scales as the number of cities and data transfers increases. Consider the computational complexity of your chosen algorithms.
*   Consider how you would handle a real-world scenario where the network topology and data transfer requirements change dynamically over time. Could your algorithm be adapted to handle these changes efficiently?

**Multiple Valid Approaches:**

*   A possible approach could involve using a multi-commodity flow algorithm, but this might be computationally expensive.
*   Another approach could involve finding the shortest path for each data transfer individually and then iteratively refining the routes to reduce network congestion.
*   A heuristic approach using simulated annealing or genetic algorithms could also be considered.

The goal is to design a robust and efficient algorithm that minimizes network congestion and cost for routing concurrent data transfers in a complex telecommunications network. The problem demands a deep understanding of graph algorithms, optimization techniques, and system design principles.
