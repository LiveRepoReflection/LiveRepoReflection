Okay, here's a problem designed to be challenging and require careful optimization in C++.

**Problem Title:** Optimal Route Planning in a Dynamic City

**Problem Description:**

The city of Algorithmia is experiencing rapid growth and constant construction.  You are tasked with designing an optimal route planning system for delivery drones.  The city can be modeled as a directed graph where intersections are nodes and roads are edges. Each road has a *traversal cost*, representing the time it takes a drone to travel that road.

However, the construction crews are unpredictable.  At any given time `t`, a subset of the roads might be temporarily blocked due to construction.  This means the traversal cost for those roads becomes effectively infinite for the duration of the block.  Furthermore, construction projects have a start time `s` and end time `e`. You can only access the road if `t < s` or `t > e`.

Given a series of delivery requests, each with a start intersection, a destination intersection, and a *delivery deadline*, your system must determine the minimum time required for the drone to complete the delivery, considering the dynamic road closures. If a route is impossible (drone cannot reach the destination by the deadline), report that.

**Input Format:**

1.  **City Map:**
    *   `N`: The number of intersections (nodes) in the city (1 <= N <= 10,000). Intersections are numbered from 0 to N-1.
    *   `M`: The number of roads (edges) in the city (1 <= M <= 50,000).
    *   `M` lines, each describing a road: `u v w`, where:
        *   `u`: The starting intersection of the road (0 <= u < N).
        *   `v`: The ending intersection of the road (0 <= v < N).
        *   `w`: The traversal cost of the road (1 <= w <= 100).

2.  **Construction Schedule:**
    *   `K`: The number of construction projects (0 <= K <= 1,000).
    *   `K` lines, each describing a construction project: `u v s e`, where:
        *   `u`: The starting intersection of the road under construction (0 <= u < N).
        *   `v`: The ending intersection of the road under construction (0 <= v < N).
        *   `s`: The start time of the construction (0 <= s <= 1,000,000).
        *   `e`: The end time of the construction (s < e <= 1,000,000).

3.  **Delivery Requests:**
    *   `Q`: The number of delivery requests (1 <= Q <= 100).
    *   `Q` lines, each describing a delivery request: `start destination deadline`, where:
        *   `start`: The starting intersection for the delivery (0 <= start < N).
        *   `destination`: The destination intersection for the delivery (0 <= destination < N).
        *   `deadline`: The delivery deadline (0 <= deadline <= 1,000,000).

**Output Format:**

For each delivery request, output a single line containing the minimum time required to complete the delivery, or `-1` if the delivery is impossible within the deadline.

**Constraints:**

*   Time Limit: 5 seconds per test case.
*   Memory Limit: 256 MB.
*   All inputs are integers.

**Example:**

**Input:**

```
4 5
0 1 10
0 2 5
1 2 2
1 3 1
2 3 4
1
0 1 0 5
2
0 3 20
1 3 10
```

**Output:**

```
9
-1
```

**Explanation:**

*   **City Map:** 4 intersections, 5 roads.
*   **Construction:** One project blocking the road from 0 to 1 between time 0 and 5.
*   **Delivery 1:** Start at 0, destination 3, deadline 20.
    *   The shortest path without considering construction would be 0 -> 1 -> 3 (cost 10 + 1 = 11).
    *   However, the road 0 -> 1 is blocked until time 5.
    *   An alternative path is 0 -> 2 -> 3 (cost 5 + 4 = 9). This is within the deadline.
*   **Delivery 2:** Start at 1, destination 3, deadline 10.
    *   The shortest path is 1 -> 3 (cost 1). This is within the deadline.

**Judging Criteria:**

*   Correctness: Does your solution produce the correct output for all test cases?
*   Efficiency: Does your solution run within the time and memory limits? Solutions with high time complexity will likely fail. The test cases will include large graphs and complex construction schedules, requiring efficient data structures and algorithms.

**Hints:**

*   Consider using Dijkstra's algorithm or A\* search for pathfinding.
*   Think about how to efficiently represent the graph and the construction schedule.
*   Pre-computation or caching might be beneficial for optimizing performance.
*   Pay close attention to edge cases and boundary conditions.
*   Consider using appropriate data structures like priority queues to optimize the search.

Good luck!
