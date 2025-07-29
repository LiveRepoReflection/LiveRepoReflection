## Question: Optimal Airport Placement for Disaster Relief

### Question Description

You are tasked with optimizing the placement of a new disaster relief airport within a large, geographically complex region. This region is represented as a weighted, undirected graph where:

*   Nodes represent cities.
*   Edges represent existing transportation routes (roads, railways, etc.) between cities.
*   Edge weights represent the time (in hours) it takes to travel between connected cities.

Following a major disaster, it's crucial to quickly distribute aid from the airport to all affected cities. Your goal is to determine the **optimal location** for the new airport to **minimize the maximum time** it takes to deliver aid to *any* city in the region.

**Constraints:**

1.  **Airport Placement:** The airport *must* be built in one of the existing cities (nodes) of the graph. You cannot build it in the middle of a road (edge).
2.  **Aid Delivery:** Aid is delivered from the airport to each city via the *fastest* route along the existing transportation network.
3.  **Objective:** Minimize the *maximum* delivery time to *any* city from the chosen airport location. This is the "minimax" problem: minimize the maximum.
4.  **Scale:** The graph can be very large (up to 10<sup>5</sup> nodes and 2 * 10<sup>5</sup> edges). The edge weights (travel times) are positive integers.
5.  **Efficiency:** Your solution must be efficient enough to handle large graphs within a reasonable time limit (e.g., a few seconds). Inefficient algorithms will time out.
6.  **Tie Breaking:** If multiple cities result in the same minimum maximum delivery time, return the city with the smallest node ID. Node IDs are integers from 0 to N-1, where N is the total number of cities.
7.  **Connectivity:** The graph is guaranteed to be connected. Every city is reachable from every other city.

**Input:**

*   `n`: The number of cities (nodes) in the region (0-indexed).
*   `edges`: A 2D array (or slice of slices in Go) representing the transportation network. Each element `edges[i]` is a slice `[city1, city2, time]` indicating a transportation route between `city1` and `city2` that takes `time` hours.

**Output:**

*   The ID of the city where the airport should be built to minimize the maximum aid delivery time to any city.

**Example:**

```
n = 4
edges = [[0, 1, 1], [0, 2, 5], [1, 2, 2], [1, 3, 10], [2, 3, 1]]

Optimal Airport Location: 2

Explanation:

- If the airport is at city 0: Max time = max(0, 1, 5, 15) = 15
- If the airport is at city 1: Max time = max(1, 0, 2, 3) = 3
- If the airport is at city 2: Max time = max(5, 2, 0, 1) = 5
- If the airport is at city 3: Max time = max(15, 3, 1, 0) = 15

City 1 has the smallest maximum time (3), so the best location is city 1.
```

**Clarifications:**

*   The travel time from a city to itself is 0.
*   The graph is undirected, meaning the travel time from city A to city B is the same as from city B to city A.
