## Problem: Optimal Traffic Light Placement

**Description:**

A rapidly growing city, "Technopolis," is experiencing severe traffic congestion. The city planners have decided to implement an intelligent traffic light system to optimize traffic flow. The city's road network can be represented as a directed graph where intersections are nodes and roads connecting them are edges. Each road has a specific length and a maximum speed limit.

The goal is to strategically place traffic lights at a subset of the intersections to minimize the average travel time between all pairs of locations within the city. You are given the city's road network, a limited budget for installing traffic lights, and a model of how traffic lights affect travel time.

**Specifics:**

*   **Input:**
    *   `N`: The number of intersections in Technopolis (numbered from 0 to N-1).
    *   `M`: The number of roads connecting the intersections.
    *   `roads`: A list of tuples `(u, v, length, speed_limit)` representing a directed road from intersection `u` to intersection `v` with a given `length` (in meters) and `speed_limit` (in meters per second).
    *   `budget`: The maximum number of traffic lights that can be installed.
    *   `light_cost`: The cost of installing one traffic light. Assume each light costs the same amount.
    *   `delay_function(length, speed_limit)`: A function that calculates the additional delay (in seconds) incurred on a road if a traffic light is installed at the *destination* intersection of that road. This function takes the road's `length` and `speed_limit` as input.  The delay function is non-negative.  For example, a possible delay function could be: `lambda length, speed_limit: length / (2 * speed_limit)` (halving the effective speed). It is assumed that the traffic light introduces a delay due to stopping and accelerating.

*   **Output:**

    A list of intersection IDs representing the optimal locations to install traffic lights to minimize the average travel time between all pairs of intersections. If multiple solutions exist with the same minimal average travel time, return any one of them.

*   **Constraints:**

    *   1 <= N <= 50
    *   1 <= M <= N * (N - 1) (fully connected graph possible).
    *   1 <= length <= 10000 (meters)
    *   1 <= speed\_limit <= 50 (meters/second)
    *   0 <= budget <= N
    *   `delay_function` will always return a non-negative float.
    *   The graph may not be fully connected, and some pairs of intersections may not have a path between them.

*   **Optimization Requirement:**

    The solution must be efficient enough to handle the given constraints within a reasonable time limit (e.g., several minutes on a standard machine). Inefficient solutions that explore the entire search space will likely time out.

*   **Edge Cases and Considerations:**

    *   The graph may contain cycles.
    *   There might be multiple roads between two intersections.
    *   The graph might not be strongly connected (some intersections might be unreachable from others).
    *   Consider the case where placing no traffic lights is the optimal solution.
    *   The `delay_function` can heavily influence the optimal placement.
    *   The average travel time calculation must account for pairs of intersections that are unreachable from each other. You could define the average travel time as the average over *reachable* pairs only.

*   **Evaluation Metric:**

    The solution will be evaluated based on the average travel time between all pairs of reachable intersections, weighted by the number of reachable pairs. The lower the average travel time, the better the solution.

**Example:**

Let's say you have the following simplified input:

```
N = 3
M = 3
roads = [(0, 1, 100, 10), (1, 2, 50, 5), (2, 0, 200, 20)]
budget = 1
light_cost = 1
delay_function = lambda length, speed_limit: length / (2 * speed_limit)
```

A possible solution could be to place a traffic light at intersection 1. You would need to calculate the average travel time for all pairs (0,1), (0,2), (1,0), (1,2), (2,0), and (2,1) *with* and *without* the traffic light to determine if placing it at intersection 1 is optimal.  You would then compare this result to placing the single light at intersection 0 or 2.

**Challenge:**

This problem requires a combination of graph algorithms (shortest path), optimization techniques, and careful handling of edge cases. The key is to find an efficient way to explore the possible placements of traffic lights within the budget constraint and accurately calculate the impact of each placement on the overall average travel time. Solutions might involve heuristics, approximation algorithms, or intelligent search strategies to navigate the complex search space. Dynamic programming is also potentially useful.
