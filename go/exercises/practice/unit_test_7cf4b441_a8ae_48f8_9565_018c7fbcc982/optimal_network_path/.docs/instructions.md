Okay, here's a challenging Go coding problem designed for a high-level programming competition, aiming for "LeetCode Hard" difficulty.

**Project Name:** `OptimalNetworkPath`

**Question Description:**

A large telecommunications company, "GlobalConnect," is designing a new fiber optic network to connect `N` cities across a country.  Each city is represented by a unique integer ID from `0` to `N-1`.  The company has surveyed potential routes and gathered data on the cost (in millions of dollars) and latency (in milliseconds) of laying fiber optic cables directly between pairs of cities.

You are given the following inputs:

*   `N`: An integer representing the number of cities in the network.
*   `edges`: A slice of slices of integers, where each inner slice `[city1, city2, cost, latency]` represents a possible direct connection between `city1` and `city2` with the given `cost` and `latency`. Note that the connections are bidirectional. It is possible to have multiple edges between the same pair of cities, each with different cost and latency.
*   `source`: An integer representing the starting city for data transmission.
*   `destination`: An integer representing the target city for data transmission.
*   `maxCost`: An integer representing the maximum budget GlobalConnect is willing to spend on the path.
*   `maxLatency`: An integer representing the maximum latency allowed for the path.

GlobalConnect wants to find the **optimal path** from the `source` city to the `destination` city, subject to the following constraints:

1.  The total cost of the path must not exceed `maxCost`.
2.  The total latency of the path must not exceed `maxLatency`.
3.  The path must be a simple path (no cycles).

The "optimal path" is defined as the path with the **minimum number of hops (edges)** that satisfies the cost and latency constraints.

Your task is to write a function that returns the minimum number of hops required to travel from the `source` city to the `destination` city, satisfying the constraints. If no such path exists, return `-1`.

**Constraints and Considerations:**

*   `1 <= N <= 100`
*   `0 <= edges.length <= N * (N - 1) / 2` (There can be at most all the undirected edges).
*   `0 <= city1, city2 < N`
*   `1 <= cost <= 100`
*   `1 <= latency <= 50`
*   `0 <= source, destination < N`
*   `0 <= maxCost <= 10000`
*   `0 <= maxLatency <= 5000`
*   There might be multiple edges between two cities with different cost and latency.
*   The graph might not be fully connected.
*   The solution needs to be efficient enough to handle the constraints, especially with potentially large `maxCost` and `maxLatency` values.  Brute-force solutions will likely time out.
*   Consider the case where the `source` and `destination` are the same city.

Good luck!
