## Project Name

`AncientCipher`

## Question Description

An ancient civilization has developed a complex cipher based on a system of interconnected cities and roads. Each city possesses a unique value, and the roads connecting them have associated traversal costs. The cipher involves traversing a specific path through these cities, accumulating values and costs along the way. Cracking this cipher requires finding the optimal path based on certain criteria.

You are given a directed graph representing the road network of this ancient civilization. The graph has `N` cities (nodes) numbered from `0` to `N-1`. Each city `i` has an associated value `V[i]`. The roads (edges) are represented by a list of tuples `(u, v, c)`, where `u` is the starting city, `v` is the destination city, and `c` is the traversal cost of the road.

The cipher message is derived by finding a path that starts at a given `start_city` and ends at a given `end_city` while adhering to the following rules:

1.  **Path Value:** The path value is the sum of the city values `V[i]` for each city `i` visited along the path (including the start and end cities). A city can be visited multiple times.
2.  **Path Cost:** The path cost is the sum of the traversal costs `c` for each road traversed along the path.
3.  **Optimization Criteria:** Find the path that maximizes the `(Path Value - Path Cost)`.

However, there are some constraints to make the problem more challenging:

*   **Cyclic Paths:** The graph may contain cycles, so the path can theoretically be infinitely long. Therefore, you need to detect and handle cycles appropriately.
*   **Maximum Path Length:** To prevent infinite loops, the path can have at most `K` edges.
*   **Negative Costs:** The traversal costs `c` can be negative, which introduces the possibility of negative cycles and makes the optimization more complex.
*   **Multiple Optimal Paths:** If multiple paths have the same maximum `(Path Value - Path Cost)`, return the path with the fewest number of edges.

Your task is to write a function that takes the following inputs and returns the optimal path (as a list of city indices) and the corresponding `(Path Value - Path Cost)`:

*   `N`: The number of cities.
*   `V`: A list of integers representing the value of each city (size N).
*   `roads`: A list of tuples `(u, v, c)` representing the roads.
*   `start_city`: The starting city index.
*   `end_city`: The ending city index.
*   `K`: The maximum number of edges in the path.

**Constraints:**

*   `1 <= N <= 100`
*   `-100 <= V[i] <= 100`
*   `0 <= len(roads) <= N * (N - 1)`
*   `0 <= u < N`
*   `0 <= v < N`
*   `-100 <= c <= 100`
*   `0 <= start_city < N`
*   `0 <= end_city < N`
*   `1 <= K <= 200`

**Output:**

Return a `std::pair<std::vector<int>, int>` representing the optimal path and the maximum `(Path Value - Path Cost)`.  The first element of the pair is a `std::vector<int>` containing the city indices of the optimal path in the order they are visited. The second element is the corresponding `(Path Value - Path Cost)`. If no path exists between the start and end cities within `K` edges, return a pair with an empty path vector and `INT_MIN`.

**Example:**

```
N = 4
V = [1, 2, 3, 4]
roads = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 2, -1)]
start_city = 0
end_city = 3
K = 3

Optimal Path: [0, 2, 3]
Path Value: 1 + 3 + 4 = 8
Path Cost: -1 + 3 = 2
(Path Value - Path Cost): 8 - 2 = 6
```
Therefore, the function should return `std::make_pair(std::vector<int>{0, 2, 3}, 6)`.
