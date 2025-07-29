## Question: Optimized Intermodal Route Planning

**Problem Description:**

You are tasked with designing an efficient route planning system for intermodal transportation. The system needs to determine the fastest route between two locations, considering various modes of transport (e.g., truck, train, ship, airplane) and transfer points between them. Each mode has different costs (time) associated with traversing a unit of distance, and transferring between modes also incurs a cost (transfer time).

The transportation network can be modeled as a directed graph.

*   **Nodes:** Represent locations (cities, ports, airports, train stations, warehouses, etc.). Each location has a unique ID.
*   **Edges:** Represent transportation links between locations. Each edge is characterized by:
    *   `source`: The ID of the starting location.
    *   `destination`: The ID of the ending location.
    *   `mode`: The mode of transport used for this link (e.g., "truck", "train", "ship", "airplane").
    *   `distance`: The distance of the link.
    *   `cost_per_unit_distance`: The cost (time) per unit distance for the specified mode.

You are also given a list of transfer points, each of which specifies:

*   `location_id`: The ID of the location where the transfer occurs.
*   `from_mode`: The mode of transport being transferred from.
*   `to_mode`: The mode of transport being transferred to.
*   `transfer_time`: The time (cost) incurred for performing this specific transfer.

**Input:**

1.  A list of locations, each with a unique ID (integer).
2.  A list of edges represented as tuples: `(source, destination, mode, distance, cost_per_unit_distance)`.
3.  A list of transfer points represented as tuples: `(location_id, from_mode, to_mode, transfer_time)`.
4.  A starting location ID.
5.  A destination location ID.

**Output:**

The minimum time (cost) required to travel from the starting location to the destination location, considering all possible intermodal routes and transfers. Return -1 if no route exists.

**Constraints:**

*   The number of locations can be up to 10,000.
*   The number of edges can be up to 100,000.
*   The number of transfer points can be up to 5,000.
*   Location IDs are non-negative integers.
*   Distances and costs are positive floating-point numbers.
*   Transfer times are non-negative floating-point numbers.
*   The graph may contain cycles.
*   Multiple edges may exist between two locations, possibly with different modes of transport.

**Optimization Requirements:**

Your solution must be highly optimized for speed. Naive approaches (e.g., brute-force search) will likely time out. Consider using efficient graph algorithms and data structures. The efficiency of your implementation, both in terms of time and memory usage, will be critical for passing the test cases.

**Edge Cases:**

*   The starting and destination locations are the same.
*   There is no path between the starting and destination locations.
*   The graph is disconnected.
*   Transfers are only possible at specific locations and between specific modes.

**Example:**

Let's say you have locations A, B, and C.

*   Edge: A -> B, mode: truck, distance: 10, cost_per_unit_distance: 1
*   Edge: B -> C, mode: train, distance: 20, cost_per_unit_distance: 0.5
*   Transfer: B, truck -> train, transfer_time: 2

A possible route from A to C would be: truck from A to B, transfer from truck to train at B, train from B to C. The total cost would be (10 * 1) + 2 + (20 * 0.5) = 22. Your program should find the *minimum* such cost.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

1.  **Correctness:** The solution must produce the correct minimum time for all test cases.
2.  **Efficiency:** The solution must execute within a reasonable time limit (typically a few seconds).
3.  **Code Quality:** The code should be well-structured, readable, and maintainable. Consider the use of appropriate data structures and algorithms.

This problem requires a deep understanding of graph algorithms, optimization techniques, and careful handling of edge cases. Good luck!
