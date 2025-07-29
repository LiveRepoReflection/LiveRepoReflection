## Problem: Optimal Public Transit Routing

**Description:**

A major metropolitan area is redesigning its public transit system. The city is represented as a graph where nodes are locations (bus stops, train stations, etc.) and edges represent direct transit connections between locations. Each transit connection has a *cost* (e.g., travel time, monetary fare) and a *capacity* (the maximum number of passengers that can use the connection at any given time).

You are tasked with designing an algorithm to determine the *optimal* route for passengers traveling between any two locations in the city, considering both cost and capacity constraints.  The city wants to minimize the *maximum utilization* of any single transit connection along the route. Maximum utilization is defined as the highest percentage of capacity used on any single edge in the chosen route.

More formally:

*   **Input:**
    *   A graph `G = (V, E)`, where:
        *   `V` is the set of locations (nodes). Each node is identified by a unique integer.
        *   `E` is the set of transit connections (edges). Each edge `e` is a tuple `(u, v, cost, capacity)`, where:
            *   `u` and `v` are the locations connected by the edge.
            *   `cost` is a non-negative integer representing the cost of using the connection.
            *   `capacity` is a positive integer representing the maximum number of passengers that can use the connection simultaneously.
    *   A source location `start_node` (an integer).
    *   A destination location `end_node` (an integer).
    *   A number of passengers `num_passengers` (a positive integer).

*   **Output:**
    *   A list of nodes representing the optimal route from `start_node` to `end_node`.
    *   Return an empty list if no route exists that can accommodate the number of passengers.
    *   If multiple routes have the same minimum maximum utilization, choose the route with the lowest total cost.

*   **Constraints:**
    *   The graph can be large (up to 10,000 nodes and 50,000 edges).
    *   The cost and capacity values can be large (up to 1,000,000).
    *   You must find a route that can accommodate *all* passengers.  If `num_passengers` exceeds the capacity of any edge in a potential route, that route is invalid.
    *   The algorithm must be efficient. Naive solutions will likely time out on larger test cases.
    *   The graph may not be fully connected. There might be no path between the start and end nodes.
    *   The graph is directed.

*   **Optimization Requirement:**
    *   Minimize the *maximum utilization* of any single edge along the chosen route.  Utilization is calculated as `num_passengers / capacity` for each edge.

**Example:**

```
Graph G:
Edges: [(0, 1, 10, 50), (0, 2, 15, 30), (1, 2, 5, 20), (1, 3, 12, 40), (2, 3, 8, 60)]
start_node = 0
end_node = 3
num_passengers = 25

Possible Routes:
1.  0 -> 1 -> 3:
    *   Utilization: (25/50, 25/40) = (0.5, 0.625)
    *   Max Utilization: 0.625
    *   Total Cost: 10 + 12 = 22
2.  0 -> 2 -> 3:
    *   Utilization: (25/30, 25/60) = (0.833, 0.417)
    *   Max Utilization: 0.833
    *   Total Cost: 15 + 8 = 23
3.  0 -> 1 -> 2 -> 3:
    *   Utilization: (25/50, 25/20, 25/60) = (0.5, 1.25, 0.417)
    *   Max Utilization: 1.25 (Invalid because 25 > 20)

Optimal Route: [0, 1, 3] (Route 1 has the lowest maximum utilization and can accommodate all passengers)
```

This problem requires a combination of graph traversal, optimization, and careful handling of constraints to find the best possible route. Good luck!
