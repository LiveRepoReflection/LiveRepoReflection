## Project Name

`OptimalRoutePlanner`

## Question Description

You are developing a route planning service for a delivery company that operates in a large city. The city is represented as a directed graph where nodes are delivery locations and edges represent roads between locations. Each road has a travel time (in minutes) and a cost (in currency units) associated with it.

Given a set of delivery orders with deadlines, your task is to find the optimal routes for each delivery order to minimize the total cost, while ensuring all deliveries are completed before their deadlines. You have a fleet of delivery vehicles, each capable of handling one delivery order at a time.

**Input:**

*   **City Graph:** A directed graph represented as an adjacency list. Each key in the list is the id of one delivery location. Each value in the list is a list of tuples, where each tuple represents a directed edge to another location. Each tuple consists of: (destination\_node\_id, travel\_time, cost). For example:

    ```python
    city_graph = {
        'A': [('B', 10, 5), ('C', 15, 7)],
        'B': [('D', 12, 6), ('E', 8, 4)],
        'C': [('F', 10, 5)],
        'D': [],
        'E': [('F', 7, 3)],
        'F': []
    }
    ```

*   **Delivery Orders:** A list of delivery orders. Each order is a tuple: (start\_node\_id, end\_node\_id, deadline). The deadline is the latest time (in minutes) the delivery can be completed, starting from time 0. Example:

    ```python
    delivery_orders = [
        ('A', 'F', 40),
        ('B', 'F', 30),
        ('C', 'D', 50) # No path from C to D
    ]
    ```

**Constraints:**

1.  **Large City Graph:** The city graph can contain up to 1000 nodes and 5000 edges.
2.  **Numerous Delivery Orders:** There can be up to 100 delivery orders.
3.  **Time Limit:** Your solution must complete within 2 seconds for all test cases.
4.  **Non-Negative Values:** Travel times and costs are non-negative integers.
5.  **Disconnected Graph:** The city graph might be disconnected. Some delivery orders might not be feasible (no path exists within the deadline).
6.  **Optimization Goal:** Minimize the total cost of all deliveries that can be completed within their deadlines.
7.  **Single Vehicle:** Each delivery order needs its own vehicle.
8.  **Starting Time:** Each vehicle starts at time zero.
9.  **Feasibility Requirement:** If a delivery order cannot be completed within its deadline, it should not be included in the total cost calculation.
10. **Path Existence:** If no path exists between the start and end nodes, the delivery order is considered infeasible.

**Output:**

An integer representing the minimum total cost to complete all feasible delivery orders within their deadlines. If no delivery order is feasible, return 0.

**Example:**

Using the `city_graph` and `delivery_orders` defined above, the optimal solution is:

*   Order 1 (A to F): Route A -> C -> F (cost 7 + 5 = 12, time 15 + 10 = 25 <= 40)
*   Order 2 (B to F): Route B -> E -> F (cost 4 + 3 = 7, time 8 + 7 = 15 <= 30)
*   Order 3 (C to D): No path exists.

Total cost: 12 + 7 = 19

**Challenge:**

This problem requires a combination of graph traversal algorithms (e.g., Dijkstra's, A\*) to find the shortest paths, along with careful consideration of deadlines and optimization to minimize the overall cost. The scale of the graph and number of orders necessitates efficient algorithms and data structures. Multiple valid approaches might exist, but the focus should be on achieving the lowest possible cost within the given time limit.
