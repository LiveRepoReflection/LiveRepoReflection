## Question: Optimal Traffic Routing with Dynamic Tolls

**Problem Description:**

A major metropolitan area is implementing a dynamic tolling system to manage traffic flow across its network of roads. You are tasked with designing an algorithm to determine the *optimal* route between two points in the road network, considering real-time traffic conditions and dynamically adjusted toll prices.

The road network is represented as a directed graph. Nodes represent intersections or key locations, and edges represent road segments connecting these locations. Each road segment has the following attributes:

*   **`length`**: The length of the road segment in kilometers (double).
*   **`baseTravelTime`**: The estimated travel time in minutes under ideal (free-flow) conditions (double).
*   **`currentTrafficFactor`**: A multiplicative factor representing current traffic congestion. A factor of 1.0 indicates free-flow conditions. Higher values indicate increased congestion and proportionally increase travel time (double).
*   **`tollPrice`**: The current toll price for using this road segment in currency units (double). The toll price is dynamically adjusted based on traffic volume.

Given a starting node `startNode`, a destination node `destinationNode`, and a maximum acceptable travel time `maxTravelTime`, your algorithm must find the route between `startNode` and `destinationNode` that minimizes the total *cost*, which is the sum of the total travel time (in minutes) and the total toll price (in currency units).

**Constraints and Edge Cases:**

1.  **Large Graph:** The road network can be very large (thousands of nodes and edges). Efficient algorithms are crucial.
2.  **Dynamic Tolls:** Toll prices can change frequently (e.g., every few seconds). While your algorithm does not need to react in real-time to every price change, it should be designed to be re-run efficiently to adapt to updated toll information.
3.  **Traffic Factor Range:** The `currentTrafficFactor` can range from 1.0 (free-flow) to 10.0 (severe congestion).
4.  **Maximum Travel Time:** The solution must find a route that adheres to `maxTravelTime`. If no such route exists, return an appropriate indicator (e.g., null, empty list, or a special error code).
5.  **Negative Cycles:** The graph should *not* contain negative cycles based on the cost function (travel time + toll). However, regular cycles are permitted.
6.  **Disconnected Graph:** The graph might not be fully connected. There might not be a route between the start and destination nodes.
7.  **Floating-Point Precision:** Be mindful of potential floating-point precision issues when calculating travel times and costs.
8.  **Multiple Optimal Routes:** If multiple routes have the same minimum cost, any of them is considered a valid solution.
9.  **Time Limit:** Your solution needs to complete within a strict time limit (e.g., 5 seconds) for large graphs.
10. **Memory Limit:** Your solution needs to fit within a strict memory limit (e.g., 1GB).

**Input:**

*   A representation of the road network graph (e.g., an adjacency list or adjacency matrix).
*   `startNode`: The starting node.
*   `destinationNode`: The destination node.
*   `maxTravelTime`: The maximum acceptable travel time in minutes (double).

**Output:**

*   A list of nodes representing the optimal route from `startNode` to `destinationNode` that minimizes the total cost (travel time + toll price) while respecting the `maxTravelTime` constraint.
*   If no route exists that satisfies the `maxTravelTime` constraint, return null or an empty list (or an error code).

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:** Does it find the optimal route or correctly identify when no route exists?
*   **Efficiency:** How quickly does it find the solution, especially for large graphs?
*   **Memory Usage:** How much memory does it consume?
*   **Code Clarity:** Is the code well-structured, readable, and maintainable?
*   **Handling Edge Cases:** Does it handle all the specified constraints and edge cases correctly?

This problem requires a combination of graph algorithms, optimization techniques, and careful consideration of constraints to achieve a performant and correct solution. Good luck!
