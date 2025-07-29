## Project Name

```
Intergalactic Trade Route Optimization
```

## Question Description

You are a strategic planner for a vast interstellar trading corporation, "Galactic Commerce Unlimited" (GCU). GCU controls a network of trading posts across multiple star systems. Each star system is represented as a node in a graph, and trade routes between systems are represented as edges. Each trade route has a specific capacity for goods and incurs a certain travel time.

However, the galaxy is not static. New star systems are being discovered, and existing trade routes are being upgraded or degraded due to various cosmic events. Moreover, the demand for goods in each star system fluctuates based on the current galactic market trends.

Your task is to design a system that, given the current state of the GCU trade network, can efficiently determine the maximum amount of goods that can be transported between any two specified star systems within a given time limit. The system must also be able to adapt to network changes and demand shifts in a timely manner.

**Specific Requirements:**

1.  **Network Representation:** The trade network is represented as a directed graph. Each node represents a star system and has a unique ID (integer). Each edge represents a trade route between two star systems, having a *capacity* (maximum amount of goods that can be transported) and a *travel time*.

2.  **Trade Route Optimization:** Implement an algorithm to find the maximum flow of goods between any two given star systems, subject to a *maximum allowed travel time*. The total travel time for a given flow path cannot exceed this limit.

3.  **Dynamic Network Updates:** The system must handle the following network updates:

    *   **Adding a new star system:** A new node is added to the graph.
    *   **Removing a star system:** An existing node is removed from the graph. All edges connected to this node are also removed.
    *   **Adding a new trade route:** A new edge is added to the graph with a specified capacity and travel time.
    *   **Removing a trade route:** An existing edge is removed from the graph.
    *   **Updating trade route capacity:** The capacity of an existing edge is updated.
    *   **Updating trade route travel time:** The travel time of an existing edge is updated.

4.  **Dynamic Demand Updates:** Each star system has a *demand* value, representing the net demand for goods in that system. These demand values can change dynamically. While not directly used in the max flow calculation, these values should be stored and accessible.

5.  **Efficiency:** The max flow algorithm should be efficient, with a time complexity that allows it to handle large networks (thousands of star systems and trade routes) and respond to queries and updates in a reasonable time. Consider using appropriate data structures and algorithms to optimize performance.

6.  **Edge Cases:** Consider various edge cases, such as:

    *   Disconnected networks (no path between the source and destination).
    *   Zero-capacity trade routes.
    *   Negative travel times (invalid input, should be handled gracefully).
    *   Source and destination are the same.
    *   No path exists within the specified time limit.

7.  **Scalability:** Assume the system might eventually need to handle millions of star systems and trade routes. Consider the long-term scalability implications of your design.

**Input:**

The input consists of:

*   A list of star systems, each with a unique integer ID and a demand value.
*   A list of trade routes, each connecting two star systems with a capacity and travel time.
*   A series of queries, each specifying a source star system ID, a destination star system ID, and a maximum allowed travel time.
*   A series of update operations (adding/removing star systems/trade routes, updating capacity/travel time, updating demand).

**Output:**

For each query, output the maximum amount of goods that can be transported from the source to the destination star system within the given time limit.

**Constraints:**

*   Number of star systems: Up to 1000
*   Number of trade routes: Up to 5000
*   Star system IDs: Positive integers.
*   Capacity: Positive integers.
*   Travel time: Non-negative integers.
*   Demand: Integers.
*   Maximum allowed travel time: Non-negative integers.
*   The solution must be implemented in Python.
*   The code must be well-structured, readable, and documented.

**Note:** This problem requires a solid understanding of graph algorithms, data structures, and optimization techniques. A well-designed solution should be able to handle a large number of queries and updates efficiently. The focus should be on algorithmic correctness and performance optimization.
