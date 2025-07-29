## Project Name

`CityTrafficOptimization`

## Question Description

You are a city planner tasked with optimizing traffic flow in a complex urban environment. The city can be represented as a directed graph where intersections are nodes and roads are directed edges with associated costs (travel time). Due to budget constraints, you can only install a limited number of smart traffic lights.

Your goal is to minimize the average travel time between several critical locations in the city by strategically placing these smart traffic lights. These smart traffic lights can dynamically adjust the green light duration based on real-time traffic conditions, effectively reducing the travel time of the road segment they control by a certain percentage.

**Specifics:**

1.  **City Representation:** The city is represented as a directed graph. Each node represents an intersection, and each directed edge represents a road segment connecting two intersections.
2.  **Road Travel Time:** Each road segment (edge) has a fixed travel time, which represents the time it takes to traverse the road under normal conditions.
3.  **Critical Locations:** You are given a set of `k` critical locations within the city (nodes in the graph).
4.  **Smart Traffic Lights:** You have a limited number, `n`, of smart traffic lights to install. Each traffic light can be installed on a road segment (edge).
5.  **Travel Time Reduction:** Installing a smart traffic light on a road segment reduces its travel time by a fixed percentage, `p`.
6.  **Optimization Goal:** Minimize the average shortest path travel time between all pairs of critical locations. That is, for each pair of critical locations (`u`, `v`), find the shortest path from `u` to `v`, sum the travel times of those paths, and divide by the total number of pairs of critical locations (`k * (k - 1)`).
7.  **Constraints:**
    *   The graph can be large, with up to 1000 nodes and 5000 edges.
    *   The number of critical locations, `k`, can be up to 100.
    *   The number of smart traffic lights, `n`, can be up to 20.
    *   Travel times are positive integers.
    *   The travel time reduction percentage, `p`, is a floating-point number between 0 and 1 (exclusive).
8.  **Edge Cases:**
    *   The graph may not be fully connected. If there is no path between two critical locations, their travel time should be considered as infinity (represented by `Integer.MAX_VALUE` in the calculations).
    *   Multiple edges can exist between two nodes.
    *   Self-loops (edges from a node to itself) can exist.
9. **Efficiency:** Your solution must be efficient enough to handle large graphs within a reasonable time limit. Consider algorithmic complexity.
10. **Multiple Optimal Solutions**: If multiple placements of traffic lights result in the same optimal average travel time, any one of those placements is considered a valid solution.

**Input:**

*   `numNodes`: The number of nodes in the graph (numbered 0 to `numNodes` - 1).
*   `edges`: A list of tuples, where each tuple `(u, v, travelTime)` represents a directed edge from node `u` to node `v` with the given `travelTime`.
*   `criticalLocations`: A list of integers representing the node IDs of the critical locations.
*   `numTrafficLights`: The number of smart traffic lights you can install.
*   `reductionPercentage`: The percentage (as a decimal between 0 and 1) by which a traffic light reduces the travel time of a road segment.

**Output:**

*   A list of tuples, where each tuple `(u, v)` represents a road segment (directed edge from `u` to `v`) where you should install a smart traffic light. The order of the tuples in the list does not matter.

**Example:**

```java
numNodes = 5;
edges = [[0, 1, 10], [0, 2, 15], [1, 3, 12], [2, 3, 8], [3, 4, 5]];
criticalLocations = [0, 3, 4];
numTrafficLights = 1;
reductionPercentage = 0.2;

// Possible Output (one optimal solution)
// [[2, 3]]
```

In the above example, placing one smart traffic light on the edge from node 2 to node 3 reduces its travel time from 8 to 6.4, resulting in a lower average travel time between critical locations.
