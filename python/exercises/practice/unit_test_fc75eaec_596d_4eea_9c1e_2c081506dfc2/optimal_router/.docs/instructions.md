## Problem: Optimal Multi-Hop Route Planner

**Description:**

You are tasked with designing an efficient route planner for a delivery service operating in a large, dynamically changing city. The city is represented as a weighted directed graph, where nodes represent delivery locations and edges represent roads connecting them. The weight of each edge represents the estimated travel time along that road. Due to real-time traffic conditions and road closures, the edge weights (travel times) are constantly being updated.

The delivery service needs to fulfill a series of delivery requests. Each request specifies a source location, a destination location, a maximum acceptable travel time, and a priority level.

Your route planner must find the optimal multi-hop route (sequence of roads) for each delivery request, subject to the following constraints:

1.  **Maximum Travel Time:** The total travel time of the route must not exceed the maximum acceptable travel time specified in the request.

2.  **Dynamic Updates:** The route planner must be able to efficiently handle frequent updates to the road network's edge weights. Recomputing the shortest path for every update is not feasible.

3.  **Priority-Based Optimization:** When multiple valid routes exist for a request, the route planner should prioritize routes that minimize the *number of hops* (number of roads traversed) while staying within the maximum travel time.  Minimizing hops reduces the risk of encountering unexpected delays along the route.

4.  **Real-Time Performance:** The route planner must be able to process delivery requests and respond with the optimal route within a strict time limit (e.g., 500ms) to avoid delays in the delivery schedule.

5.  **Scalability:** The city graph can be very large (thousands of nodes and edges), and the number of simultaneous delivery requests can be high. The solution should scale efficiently to handle this workload.

**Input:**

*   **City Graph:** Represented as a dictionary where keys are source nodes and values are dictionaries representing outgoing edges. Each outgoing edge dictionary contains the destination node and the current travel time. Example:
    ```python
    graph = {
        'A': {'B': 10, 'C': 15},
        'B': {'D': 12, 'E': 15},
        'C': {'F': 10},
        'D': {'F': 2, 'G': 1},
        'E': {'G': 9},
        'F': {'G': 5},
        'G': {}
    }
    ```
*   **Delivery Requests:** A list of dictionaries, each containing the following keys:
    *   `source`: The source location (node).
    *   `destination`: The destination location (node).
    *   `max_travel_time`: The maximum acceptable travel time for the route.
    *   `priority`: An integer representing the priority of the request (higher value = higher priority, though this doesn't affect the algorithm directly, it might affect the order in which you process requests).

*   **Edge Updates:** A stream of tuples, where each tuple contains:
    *   `source`: The source node of the edge.
    *   `destination`: The destination node of the edge.
    *   `new_travel_time`: The updated travel time for the edge.

**Output:**

For each delivery request, return a list of nodes representing the optimal route (including the source and destination). If no valid route exists within the maximum travel time, return an empty list.

**Constraints:**

*   The graph can contain cycles.
*   Edge weights (travel times) are non-negative integers.
*   The number of nodes in the graph can be up to 1000.
*   The number of edges in the graph can be up to 10000.
*   The number of delivery requests can be up to 100.
*   The number of edge updates can be up to 1000 per second.
*   The `max_travel_time` for each request can be up to 1000.
*   Each request must be processed within 500ms.

**Challenge:**

Design a route planner that efficiently finds the optimal route for each delivery request, considering both travel time and number of hops, while handling dynamic updates to the road network in real-time and scaling to handle a large workload.  Think about data structures and algorithms that can be precomputed and updated efficiently to meet the performance requirements. Consider exploring algorithms beyond standard shortest path algorithms like Dijkstra or A*, and investigate techniques for quickly adapting to edge weight changes.
