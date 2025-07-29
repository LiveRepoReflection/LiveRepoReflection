## Problem: Optimal Evacuation Route Planning

**Question Description:**

A major earthquake has struck a densely populated city. Buildings are collapsing, roads are blocked, and communication infrastructure is severely damaged. You are tasked with designing an optimal evacuation plan to minimize the total evacuation time for all residents.

The city can be represented as a weighted, undirected graph. Nodes in the graph represent locations (intersections, landmarks, etc.), and edges represent roads connecting these locations. Each edge has a weight representing the time it takes to traverse that road (due to distance, debris, traffic, etc.).

There are multiple evacuation centers scattered throughout the city. Each evacuation center has a limited capacity, representing the maximum number of people it can accommodate.

Each location in the city has a certain number of residents who need to be evacuated.

Your goal is to determine the optimal evacuation route for each location's residents to an evacuation center such that:

1.  **Every resident is evacuated:** All residents from every location must be assigned to an evacuation center.
2.  **Evacuation center capacity is not exceeded:** The total number of residents assigned to any evacuation center must not exceed its capacity.
3.  **Total evacuation time is minimized:** The sum of the shortest path distances from each location to its assigned evacuation center, multiplied by the number of residents at that location, must be minimized.

**Input:**

*   `locations`: A list of tuples, where each tuple represents a location `(location_id, resident_count)`. `location_id` is a unique integer identifying the location, and `resident_count` is the number of residents at that location.
*   `evacuation_centers`: A list of tuples, where each tuple represents an evacuation center `(center_id, capacity)`. `center_id` is a unique integer identifying the evacuation center, and `capacity` is the maximum number of residents the center can accommodate.
*   `roads`: A list of tuples, where each tuple represents a road `(location_id_1, location_id_2, travel_time)`. `location_id_1` and `location_id_2` are the IDs of the locations connected by the road, and `travel_time` is the time it takes to travel along that road. The graph is undirected.

**Output:**

*   A dictionary where the keys are `location_id` and the values are the `center_id` to which residents of each location are assigned.

**Constraints and Considerations:**

*   The graph can be large (thousands of locations and roads).
*   The number of evacuation centers can be limited (e.g., 5-10).
*   Finding the shortest paths between all location-evacuation center pairs is a potentially time-consuming operation.  Consider efficient shortest path algorithms.
*   The sum of all residents may exceed the total capacity of all evacuation centers. In this case, return `None` (evacuation is impossible).
*   There may be multiple optimal solutions. Any optimal solution is acceptable.
*   Consider edge cases such as disconnected graphs, locations with no residents, or evacuation centers with zero capacity.
*   Memory usage should be considered, especially when dealing with large graphs.
*   The solution should be as efficient as possible in terms of time complexity. Solutions that time out will not be accepted. The emphasis is on finding the most efficient algorithm and data structures to solve this problem.

**Example:**

```python
locations = [(1, 100), (2, 50), (3, 75)]
evacuation_centers = [(4, 150), (5, 100)]
roads = [(1, 2, 10), (2, 3, 5), (1, 4, 15), (2, 4, 12), (3, 5, 8), (4, 5, 20)]

# Possible optimal output (not necessarily unique):
# {1: 4, 2: 4, 3: 5}
```

**Grading:**

The solution will be evaluated based on:

1.  **Correctness:** Does the solution correctly assign residents to evacuation centers while respecting capacity constraints and evacuating all residents (if possible)?
2.  **Optimality:** How close is the solution to the optimal total evacuation time? Solutions that are significantly suboptimal will receive fewer points.
3.  **Efficiency:** How well does the solution scale with the size of the city graph and the number of residents? Solutions with poor time complexity will time out or receive fewer points.
4.  **Handling Edge Cases:** Does the solution correctly handle various edge cases and invalid inputs?
