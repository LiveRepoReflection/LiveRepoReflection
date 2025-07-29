## Problem: Optimal Traffic Light Placement

**Description:**

Imagine you are tasked with designing a smart traffic management system for a rapidly growing city. The city's road network can be represented as an undirected graph where nodes are intersections and edges are road segments. The goal is to minimize the average travel time between any two intersections in the city.

You have a limited budget to install traffic lights at some of the intersections. Installing a traffic light at an intersection introduces a fixed delay for vehicles passing through it, regardless of the direction. Your task is to determine the optimal placement of traffic lights to minimize the overall average travel time across all pairs of intersections.

**Specifically:**

*   **Input:**
    *   `n`: The number of intersections in the city (numbered from 0 to n-1).
    *   `roads`: A list of tuples `(u, v, w)` representing undirected road segments, where `u` and `v` are the intersection IDs connected by the road, and `w` is the travel time (weight) along that road segment.
    *   `budget`: The maximum number of traffic lights you can install.
    *   `delay`: The fixed delay introduced by each traffic light installed at an intersection.

*   **Output:**
    *   The minimum possible average travel time between all pairs of intersections in the city, rounded to six decimal places. The average travel time should be calculated *after* the optimal placement of traffic lights.

**Constraints:**

*   `1 <= n <= 100` (Number of intersections)
*   `0 <= len(roads) <= n * (n - 1) / 2` (Number of road segments, fully connected graph)
*   `1 <= budget <= n` (Maximum number of traffic lights)
*   `1 <= w <= 100` for each road segment (Travel time weight)
*   `1 <= delay <= 100` (Traffic light delay)
*   The graph is guaranteed to be connected.
*   You must install at most `budget` traffic lights. You can choose to install fewer, or even none, if it optimizes the result.

**Example:**

```
n = 3
roads = [(0, 1, 10), (1, 2, 10), (0, 2, 15)]
budget = 1
delay = 5

# One possible optimal solution is to place a traffic light at intersection 1.

# The average travel time is calculated as follows:
# Distance(0, 1) = 10 + 5 = 15
# Distance(1, 0) = 10 + 5 = 15
# Distance(0, 2) = 15
# Distance(2, 0) = 15
# Distance(1, 2) = 10 + 5 = 15
# Distance(2, 1) = 10 + 5 = 15
# Total Distance = 90
# Average Distance = 90 / (3 * (3 - 1)) = 90 / 6 = 15.000000

# Another possible optimal solution is to place a traffic light at intersection 0

# The average travel time is calculated as follows:
# Distance(0, 1) = 10 + 5 = 15
# Distance(1, 0) = 10 + 5 = 15
# Distance(0, 2) = 15 + 5 = 20
# Distance(2, 0) = 15 + 5 = 20
# Distance(1, 2) = 10
# Distance(2, 1) = 10
# Total Distance = 90
# Average Distance = 90 / (3 * (3 - 1)) = 90 / 6 = 15.000000

# If no traffic lights are placed:
# Distance(0, 1) = 10
# Distance(1, 0) = 10
# Distance(0, 2) = 15
# Distance(2, 0) = 15
# Distance(1, 2) = 10
# Distance(2, 1) = 10
# Total Distance = 70
# Average Distance = 70 / 6 = 11.666667

# Therefore, the minimum average travel time is 11.666667

Output: 11.666667
```

**Challenge:**

This problem requires you to:

1.  Represent the road network as a graph.
2.  Implement an algorithm to calculate the shortest path between all pairs of intersections (e.g., Floyd-Warshall, Dijkstra's).
3.  Enumerate all possible combinations of traffic light placements within the budget constraint.
4.  For each combination, calculate the average travel time.
5.  Return the minimum average travel time found across all combinations.

**Optimization Considerations:**

*   The brute-force approach of trying all possible traffic light placements will likely be too slow for larger inputs.
*   Consider using dynamic programming or other optimization techniques to reduce the search space.
*   Think about how to efficiently update the shortest path distances when a traffic light is added.

This problem combines graph algorithms, optimization, and careful consideration of edge cases to deliver a truly challenging coding experience. Good luck!
