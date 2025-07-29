## Question: Optimized Multi-Source Shortest Path in a Dynamic Road Network

**Problem Description:**

You are given a road network represented as a directed graph. The graph consists of `N` cities (nodes) numbered from 0 to `N-1` and `M` roads (edges) connecting them. Each road has a length (positive integer).

You are also given a set of `K` "source" cities. You need to find the shortest path from *any* of these source cities to *every* other city in the network.

However, the road network is dynamic. You will receive a series of `Q` updates. Each update can be one of two types:

1.  **Road Update:** A road's length changes. You are given the start city `u`, the end city `v`, and the new length `w` of the road connecting them. If no such road exists, create one. If the road exists, but it's in the opposite direction, create a new one.
2.  **Source Update:** A city is added to or removed from the set of source cities. You are given the city `x` and a boolean value `add`. If `add` is true, city `x` is added to the source cities. If `add` is false, city `x` is removed from the source cities.  It is guaranteed that if `add` is false, city `x` is already a source city.

After each update, you need to calculate and output the sum of the shortest path distances from the *current* set of source cities to all other cities. If a city is unreachable from any of the source cities, its distance is considered to be -1.

**Input:**

*   `N`: The number of cities.
*   `M`: The number of initial roads.
*   `roads`: A list of tuples `(u, v, w)` representing the initial roads, where `u` is the start city, `v` is the end city, and `w` is the road length.
*   `K`: The number of initial source cities.
*   `sources`: A list of integers representing the initial source cities.
*   `Q`: The number of updates.
*   `updates`: A list of tuples. Each tuple can be one of two forms:
    *   `(0, u, v, w)`: Road update, where `u` is the start city, `v` is the end city, and `w` is the new road length.  The first element `0` indicates this is a road update.
    *   `(1, x, add)`: Source update, where `x` is the city to add/remove, and `add` is a boolean value indicating whether to add or remove the city.  The first element `1` indicates this is a source update.

**Output:**

A list of integers, where each integer is the sum of the shortest path distances after each update.

**Constraints:**

*   `1 <= N <= 1000`
*   `0 <= M <= N * (N - 1)`
*   `0 <= K <= N`
*   `0 <= u, v, x < N`
*   `1 <= w <= 1000`
*   `1 <= Q <= 1000`

**Example:**

```
N = 4
M = 2
roads = [(0, 1, 2), (1, 2, 3)]
K = 1
sources = [0]
Q = 2
updates = [
    (0, 2, 3, 1),  # Road Update: road from 2 to 3 with length 1
    (1, 1, True)   # Source Update: Add city 1 to the source cities
]

Output: [5, 4]

Explanation:

Initial Graph:
0 -> 1 (2)
1 -> 2 (3)

Initial Sources: [0]

After Road Update (0, 2, 3, 1):
0 -> 1 (2)
1 -> 2 (3)
2 -> 3 (1)

Shortest paths from source [0]:
0 -> 0: 0
0 -> 1: 2
0 -> 2: 5
0 -> 3: -1 (unreachable)
Sum: 0 + 2 + 5 + (-1) = 6

After Source Update (1, 1, True):
0 -> 1 (2)
1 -> 2 (3)
2 -> 3 (1)

Sources: [0, 1]

Shortest paths from sources [0, 1]:
0 -> 0: 0
0 -> 1: 2
0 -> 2: 3 (1->2)
0 -> 3: 4 (1->2->3)
Sum: 0 + 2 + 3 + 4 = 9
```

**Optimization Requirements:**

*   Naive recomputation of shortest paths after each update will likely result in a Time Limit Exceeded (TLE) error.  You need to optimize your algorithm to handle the updates efficiently.
*   Consider using appropriate data structures and algorithms to minimize the time complexity of each update and shortest path calculation.

**Judging Criteria:**

*   Correctness: Your solution must produce the correct output for all valid input cases.
*   Efficiency: Your solution must be efficient enough to pass the time limit constraints.  Solutions with high time complexity will be penalized.
*   Code Clarity: Your code should be well-structured and easy to understand.

This problem requires a combination of graph algorithms (shortest path), data structure knowledge, and optimization techniques to solve efficiently. Good luck!
