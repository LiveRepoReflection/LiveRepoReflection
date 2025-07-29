Okay, here's a challenging Go coding problem designed to push even experienced programmers.

**Problem Title:** Optimal Multi-Source Shortest Paths with Time Windows

**Problem Description:**

You are tasked with designing an optimal route planning system for a fleet of delivery drones. The drones need to deliver packages from multiple origin warehouses to multiple destination locations within specific time windows.

You are given the following information:

*   `N`: The number of locations (warehouses and destinations). Locations are numbered from 0 to N-1.
*   `M`: The number of drone routes that need to be optimized.
*   `adjMatrix`: An adjacency matrix representing a weighted, directed graph where `adjMatrix[i][j]` represents the travel time (in minutes) from location `i` to location `j`. A value of `-1` indicates no direct route exists between those locations. The `adjMatrix` is guaranteed to be non-negative if a route exists.
*   `origins`: A list of origin locations (warehouses) for the drones. Multiple drones can start from the same warehouse.
*   `destinations`: A list of destination locations (delivery points). Multiple drones can deliver to the same location. The length of `origins` and `destinations` are both equal to `M`.
*   `timeWindows`: A 2D array where `timeWindows[i]` contains the start and end time (in minutes, relative to a global starting time) for a delivery to destination `i`.  Arrival outside this window is not allowed. `timeWindows[i][0]` is the earliest allowed arrival time at location `i` and `timeWindows[i][1]` is the latest allowed arrival time.

Each drone route (from origin `i` to destination `i`) must adhere to the following constraints:

1.  **Time Window Constraint:** Each drone *must* arrive at its destination *within* the specified time window.  Arriving *before* `timeWindows[i][0]` or *after* `timeWindows[i][1]` for delivery `i` is not permitted.
2.  **Path Existence:** A valid path must exist from the origin to the destination.
3.  **No Intermediate Stops are Allowed:** Drones must travel directly from the origin to the destination, i.e. only a single edge is allowed in the path.
4.  **Optimization Goal:** Minimize the total idle time across all drone routes. Idle time for a single drone route is the difference between the earliest arrival time and the actual arrival time. Sum the idle time over all `M` routes.

**Input:**

*   `N` (int): Number of locations.
*   `M` (int): Number of drone routes.
*   `adjMatrix` ([][]int): Adjacency matrix representing travel times.
*   `origins` ([]int): List of origin locations.
*   `destinations` ([]int): List of destination locations.
*   `timeWindows` ([][]int): 2D array of time windows for each destination.

**Output:**

*   (int): The minimum total idle time across all drone routes. If it is impossible to satisfy all the constraints for any route, return `-1`.

**Constraints:**

*   1 <= `N` <= 100
*   1 <= `M` <= 100
*   0 <= `origins[i]` < `N`
*   0 <= `destinations[i]` < `N`
*   0 <= `timeWindows[i][0]` <= `timeWindows[i][1]` <= 1000
*   -1 <= `adjMatrix[i][j]` <= 1000
*   The adjacency matrix may not be symmetric.
*   Self-loops are allowed (i.e., `adjMatrix[i][i]` can be a valid travel time).

**Example:**

```
N = 4
M = 2
adjMatrix = [][]int{
    {0, 10, -1, -1},
    {-1, 0, 5, -1},
    {-1, -1, 0, 8},
    {-1, -1, -1, 0},
}
origins = []int{0, 1}
destinations = []int{1, 2}
timeWindows = [][]int{
    {12, 20},
    {5, 10},
}

// Expected output: 2
//
// Explanation:
// Route 1: Origin 0, Destination 1, Travel Time 10. Earliest arrival time 12. Idle time = 12-10 = 2.
// Route 2: Origin 1, Destination 2, Travel Time 5. Earliest arrival time 5. Idle time = 5-5 = 0.
// Total idle time = 2 + 0 = 2.
```

**Challenge:**

The core challenge lies in efficiently verifying whether a route satisfies the time window constraints and correctly calculating the idle time. The complexity increases with the number of locations and routes.
