## The Intergalactic Shortest Path Problem

**Problem Description:**

The Intergalactic Federation (IGF) maintains a network of interconnected space stations across the galaxy. Each station possesses a unique set of resources, and travel between stations is facilitated by wormholes. However, wormholes are unstable and traversing them incurs a risk of temporary resource degradation.

You are tasked with developing an algorithm to determine the shortest path between two given space stations while minimizing the total resource degradation incurred during the journey.

**Formal Definition:**

You are given:

1.  **`n`**: The number of space stations, numbered from 0 to `n-1`.
2.  **`adj`**: An adjacency list representing the wormhole network. `adj[i]` is a list of tuples `(j, d, r)`, where:

    *   `j` is the destination space station (0-indexed).
    *   `d` is the distance (time units) to travel through the wormhole from station `i` to station `j`.
    *   `r` is a list of tuples `(resource_id, degradation_amount)`. Each wormhole degrades certain resources by the specified amount during traversal. `resource_id` is an integer identifying the specific resource. Resources are 0-indexed.
3.  **`start`**: The index of the starting space station.
4.  **`end`**: The index of the destination space station.
5.  **`resources`**: A list representing the initial amount of each resource at the starting station. `resources[i]` is the initial amount of the resource with `resource_id = i`.
6.  **`resource_thresholds`**: A list representing the minimum required amount for each resource to maintain functionality. `resource_thresholds[i]` is the minimum amount needed for resource `i`. If a resource's amount falls below its threshold at *any* point during the journey (including at intermediate stations), the entire journey is considered invalid.

Your algorithm must find the shortest path (minimum total distance) from the `start` station to the `end` station, such that:

*   The total resource degradation along the path is minimized.
*   The amount of each resource at every station along the path never falls below the corresponding resource threshold.
*   The amount of each resource at the destination station is greater than or equal to the corresponding resource threshold.
*   If multiple shortest paths exist, choose the path with the least degradation.

**Constraints:**

*   `1 <= n <= 1000` (Number of space stations)
*   `0 <= start, end < n`
*   `0 <= resource_id < len(resources)`
*   `0 <= degradation_amount <= 1000`
*   `0 <= resources[i] <= 100000`
*   `0 <= resource_thresholds[i] <= 100000`
*   The graph may contain cycles.
*   The graph may not be fully connected.
*   Wormholes are unidirectional.
*   Distances (`d`) are non-negative integers.
*   Number of wormholes per station can vary.
*   Number of resources can vary.
*   The amount of resource cannot be negative.
*   If no valid path exists, return `-1`.

**Output:**

Return the minimum distance (total time units) required to travel from the `start` station to the `end` station while satisfying the resource constraints. Return `-1` if no such path exists.

**Example:**

```python
n = 3
adj = [
    [(1, 5, [(0, 10)]), (2, 10, [(1, 5)])],  # Station 0
    [(2, 3, [(0, 5), (1, 2)])],  # Station 1
    []   # Station 2
]
start = 0
end = 2
resources = [50, 30]  # Initial resources at station 0
resource_thresholds = [15, 10]

# Expected output: 8 (0 -> 1 -> 2)
# Path 0 -> 1: distance 5, resource degradation (0: 10) -> resources = [40, 30]
# Path 1 -> 2: distance 3, resource degradation (0: 5, 1:2) -> resources = [35, 28]
# Total distance: 5 + 3 = 8
# Resources at station 2: [35, 28] >= resource_thresholds [15, 10]
```

**Optimization Requirements:**

The solution should be optimized for both time and space complexity, considering the constraints. Naive approaches (e.g., brute-force search) will likely result in timeouts. Techniques like Dijkstra's algorithm or A\* search (with appropriate heuristics to account for resource constraints) might be necessary.
