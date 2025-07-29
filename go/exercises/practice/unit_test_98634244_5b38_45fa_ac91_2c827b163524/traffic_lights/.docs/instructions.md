## Question: Optimal Traffic Light Placement

**Description:**

You are tasked with optimizing traffic flow in a newly developed city district. The district can be represented as a grid graph where each node is an intersection, and edges represent bidirectional roads connecting adjacent intersections. The city planner has provided you with a map of the district, represented as an `N x M` grid.

Your goal is to determine the *minimum* number of traffic lights needed to ensure that *every* road in the district is "controlled". A road is considered "controlled" if at least one of its endpoints (the intersections it connects) has a traffic light.

However, due to budget constraints, there are some intersections where you *cannot* place traffic lights. The city planner provides you with a list of these restricted intersections.

Furthermore, to improve public transport efficiency, the city planner wants to ensure that the longest shortest path (in terms of number of roads) between any two intersections without traffic lights is minimized. In other words, you need to place the traffic lights such that the maximum distance between any two intersections that *don't* have traffic lights is as small as possible. If there are multiple solutions that achieve the minimum number of traffic lights, choose the one that minimizes this maximum distance.

**Input:**

*   `N`: An integer representing the number of rows in the grid (1 <= N <= 50).
*   `M`: An integer representing the number of columns in the grid (1 <= M <= 50).
*   `restricted`: A slice of `[row, column]` integer slices representing the coordinates of intersections where traffic lights cannot be placed. Coordinates are 0-indexed.  `len(restricted) <= N*M`
*   Grid Graph is implicitly defined as a `N*M` nodes which are the intersections, and the roads connect adjacent nodes in four directions.

**Output:**

*   An integer representing the minimum number of traffic lights needed to control all roads, while also minimizing the maximum distance between any two intersections without traffic lights.

**Constraints:**

*   Your solution must run within a time limit of 5 seconds.
*   Memory usage should be reasonable.
*   The grid is guaranteed to be connected.  That is, it's always possible to travel between any two intersections.
*   It's guaranteed that there is at least one valid solution.
*   `N` and `M` are relatively small, but exploring all combinations of placing traffic lights on valid locations will time out.

**Example:**

```
N = 3
M = 3
restricted = [][]int{{1, 1}}

Output: 4
```

**Explanation of Example:**

The grid is 3x3.  You cannot place a traffic light at (1,1).  One optimal solution is to place traffic lights at (0,0), (0,2), (2,0), and (2,2). This controls all roads. The maximum distance between any two intersections *without* traffic lights is 2 (e.g., from (0,1) to (1,2) or (1,0) to (2,1)).  Other solutions with 4 lights might exist, but this one minimizes the maximum distance between intersections without traffic lights. It's impossible to control all roads with fewer than 4 traffic lights.
