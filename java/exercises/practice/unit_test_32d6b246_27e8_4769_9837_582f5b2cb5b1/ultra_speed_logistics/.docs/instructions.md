## The Ultra-Fast Logistics Network

### Question Description

A global logistics company, "UltraSpeed Logistics," is designing the next-generation routing system for its delivery network. Their goal is to minimize delivery times while considering various real-world constraints.

The delivery network is represented as a directed graph. Each node in the graph represents a distribution center, and each directed edge represents a possible route between two distribution centers. Each route has a "travel time" associated with it, representing the time (in minutes) it takes to traverse that route.

You are tasked with implementing a system that, given the network and a set of delivery requests, finds the *k* most efficient routes for each request.

**Specifics:**

1.  **Graph Representation:** The delivery network is provided as a list of edges. Each edge is a tuple `(source, destination, travel_time)`, where `source` and `destination` are integer IDs representing distribution centers, and `travel_time` is an integer representing the travel time in minutes. Assume that node IDs are non-negative integers. The graph may not be fully connected.

2.  **Delivery Requests:** A delivery request is a tuple `(start_node, end_node, deadline)`. `start_node` is the ID of the origin distribution center, `end_node` is the ID of the destination distribution center, and `deadline` is the maximum allowed delivery time (in minutes).

3.  **Efficiency Metric:** The efficiency of a route is primarily determined by its travel time. However, routes with travel times exceeding the `deadline` are considered invalid and should not be included in the top *k* results. If multiple routes have the same travel time, prioritize routes with fewer hops (edges).

4.  **K-Shortest Paths with Deadline Constraint:** For each delivery request, find the *k* shortest paths from the `start_node` to the `end_node` that meet the `deadline` constraint. If fewer than *k* valid paths exist, return all valid paths.

5.  **Real-world Constraints:**
    *   **Traffic Peaks:** Certain edges have "peak hours" where the `travel_time` increases. You are given a list of "traffic events." Each event is a tuple `(source, destination, start_time, end_time, increase_percentage)`. If a delivery route traverses the edge `(source, destination)` during the time interval `[start_time, end_time]` (inclusive), the `travel_time` for that edge is increased by `increase_percentage` (e.g., 10% increase means multiplying the `travel_time` by 1.10). You should assume that `start_time` and `end_time` are relative to the start of the request. If an edge is traversed multiple times during peak hours, only the first peak hours which the edge is traversed should be taken into account.
    *   **Dynamic rerouting:** You should consider the traffic when finding the K shortest paths. Assume that the agent will reroute his path after each hub, thus only the first traffic jam is taken into account.
    *   **Limited Cache:** You should design your solution in such a way that caches the data structures required. However, the cache size is strictly limited. Exceeding this limit may cause system crash.

6.  **Output:** For each delivery request, return a list of the *k* most efficient routes. Each route should be represented as a list of node IDs, starting with the `start_node` and ending with the `end_node`. The routes should be sorted by increasing travel time (considering peak hours), and for routes with the same travel time, by increasing number of hops.

**Input:**

*   `edges`: A list of tuples `(source, destination, travel_time)` representing the delivery network.
*   `requests`: A list of tuples `(start_node, end_node, deadline)` representing the delivery requests.
*   `traffic_events`: A list of tuples `(source, destination, start_time, end_time, increase_percentage)` representing the traffic events.
*   `k`: The number of shortest paths to find for each request.
*   `cache_limit`: The maximum cache limit.

**Constraints:**

*   1 <= Number of nodes in the graph <= 1000
*   1 <= Number of edges in the graph <= 5000
*   1 <= `travel_time` <= 100
*   1 <= Number of requests <= 100
*   1 <= `deadline` <= 1000
*   1 <= `k` <= 10
*   0 <= `start_time`, `end_time` <= 1000
*   1 <= `increase_percentage` <= 100
*   `cache_limit` is in terms of memory used, and will be revealed via runtime failure if exceeded.

**Example:**

```java
edges = [(0, 1, 50), (0, 2, 75), (1, 2, 25), (2, 3, 100), (1,3,200)]
requests = [(0, 3, 300)]
traffic_events = [(0, 1, 50, 100, 20), (1, 2, 0, 200, 50)]
k = 2
cache_limit = 1024 * 1024 // 1MB

// Expected Output:
// [[0, 1, 2, 3], [0, 2, 3]]
// Explanation:
// Path 1: 0 -> 1 -> 2 -> 3: 50*1.2 + 25*1.5 + 100 = 60 + 37.5 + 100 = 197.5
// Path 2: 0 -> 2 -> 3: 75 + 100 = 175
// Path 2 is shorter than path 1.
```

**Challenge:**

*   Design an efficient algorithm to find the *k* shortest paths with the deadline constraint, considering the dynamic travel times due to traffic.
*   Optimize your solution to handle large graphs and numerous requests within a reasonable time limit.
*   Consider the trade-offs between different algorithmic approaches (e.g., Dijkstra's algorithm, A\* search, Yen's algorithm).
*   Implement your solution in Java, paying close attention to memory usage and avoiding unnecessary object creation.
*   Handle all edge cases and ensure the correctness of your solution.
*   Implement caching to improve performance, but stay within the `cache_limit`.

This problem requires a deep understanding of graph algorithms, data structures, and optimization techniques. Good luck!
