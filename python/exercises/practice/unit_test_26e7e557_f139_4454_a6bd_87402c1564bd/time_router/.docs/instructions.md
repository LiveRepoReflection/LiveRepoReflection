Okay, here's a challenging Python coding problem designed to be at the LeetCode Hard level, incorporating several of the elements you requested.

**Problem Title:  Optimal Route Planner with Time-Dependent Congestion**

**Problem Description:**

You are tasked with designing an optimal route planner for a delivery service operating in a large city.  The city is represented as a directed graph where nodes represent intersections and edges represent road segments. Each road segment has a *base travel time* and a *time-dependent congestion factor*.

Specifically:

*   **Graph Representation:** The city is represented as a dictionary (or adjacency list) where keys are intersection IDs (integers) and values are lists of tuples.  Each tuple in the list represents a directed road segment originating from that intersection. A tuple has the form `(destination_intersection, base_travel_time, congestion_profile)`.

*   **Base Travel Time:** `base_travel_time` is a positive integer representing the minimum time (in minutes) to traverse the road segment under ideal (no congestion) conditions.

*   **Congestion Profile:** `congestion_profile` is a list of `(time_window_start, time_window_end, congestion_factor)` tuples.  Each tuple defines a time window (in minutes since the start of the day) and a corresponding `congestion_factor`.  The congestion factor is a positive floating-point number.  If the current time falls within a time window, the actual travel time for that road segment is `base_travel_time * congestion_factor`. If the current time does not fall into any defined time windows, the travel time is just `base_travel_time`. Time windows can overlap.

*   **Time:** Time is represented as an integer, indicating minutes since the start of the day (0 = midnight). Time rolls over at the end of the day (1440 minutes = midnight again).

*   **Objective:** Given a starting intersection `start_intersection`, a destination intersection `end_intersection`, and a starting time `start_time`, find the *minimum travel time* required to reach the destination, considering the time-dependent congestion.

**Constraints and Requirements:**

1.  **Graph Size:** The city graph can be very large (up to 10,000 intersections and 50,000 road segments).
2.  **Congestion Profiles:** Each road segment can have a complex congestion profile with multiple time windows (up to 100).
3.  **Time Complexity:** The solution must be efficient. A naive approach of simply exploring all possible paths will likely time out.  Consider using appropriate graph algorithms and data structures.  Aim for something better than O(V\*E) if possible, where V and E are the number of Vertices and Edges, respectively. Consider heuristics to help guide your search.
4.  **Edge Cases:**
    *   Handle cases where no path exists between the start and end intersections.
    *   Handle cases where the `start_intersection` or `end_intersection` is not a valid intersection in the graph.
    *   Ensure that the time calculations wrap around correctly at the end of the day.
    *   Handle cases of overlapping time windows in the congestion profile. The largest congestion factor should be applied for overlapping windows.
5.  **Optimization:** The primary goal is to minimize travel time. Memory usage is also a consideration, but less critical than speed.
6.  **Real-World Scenario:** This problem models a realistic scenario of route planning in urban environments where traffic patterns vary throughout the day.
7.  **Multiple Valid Approaches:** Dijkstra's algorithm with modifications to handle time-dependent edge weights is a possible approach. A\* search with a suitable heuristic might be even more efficient in some cases. Explore different approaches and analyze their trade-offs.

**Input:**

*   `graph`: A dictionary representing the city graph as described above.
*   `start_intersection`: An integer representing the starting intersection.
*   `end_intersection`: An integer representing the destination intersection.
*   `start_time`: An integer representing the starting time (minutes since midnight).

**Output:**

*   An integer representing the minimum travel time (in minutes) to reach the destination. Return -1 if no path exists.

Good luck!
