## Question: Optimal Highway Construction

**Description:**

The Ministry of Infrastructure is planning to build a new highway system connecting several cities. Due to geographical constraints, the project is divided into multiple phases. Each phase involves connecting a subset of cities using bidirectional highway segments.

The goal is to minimize the total construction cost while ensuring that all cities are connected *as early as possible* in the construction process.

**Input:**

*   `N`: An integer representing the number of cities, labeled from `0` to `N-1`.
*   `M`: An integer representing the number of construction phases.
*   `phases`: A vector of vectors of tuples, where `phases[i]` represents the *i*-th construction phase. Each element in `phases[i]` is a tuple `(city1, city2, cost)`, representing a potential bidirectional highway segment between `city1` and `city2` with a construction cost of `cost`.

**Constraints:**

*   `1 <= N <= 200` (number of cities)
*   `1 <= M <= 100` (number of construction phases)
*   `0 <= city1, city2 < N`
*   `1 <= cost <= 1000`
*   It is guaranteed that it is possible to connect all cities using some combination of highway segments across all phases.
*   A city might appear in multiple phases.
*   Within each phase, there are no duplicate highway segments (i.e., no two entries with the same `city1` and `city2`).
*   `city1 != city2` for any highway segment.

**Output:**

An integer representing the *minimum possible total cost* to connect all cities using a subset of highway segments from the given phases, satisfying the constraint that the cities must be connected *as early as possible*.

**"As Early As Possible" Definition:**

Connectivity is defined as all cities belonging to a single connected component.  We want to minimize the *earliest* phase `p` such that all cities are connected.  If there are multiple solutions that achieve the same earliest phase `p`, we want to minimize the total cost among those solutions.

**Specifically, the algorithm should follow these steps:**

1.  **Minimize the earliest phase:** Find the smallest phase index `p` (0-indexed) such that it's possible to connect all cities by only using highway segments up to and including phase `p`.

2.  **Minimize cost within the earliest phase:**  Among all combinations of highway segments up to phase `p` that achieve full connectivity, choose the combination with the minimum total cost.

**Example:**

```
N = 4
M = 3
phases = {
    {{0, 1, 10}, {1, 2, 15}}, // Phase 0
    {{2, 3, 20}, {0, 3, 5}},   // Phase 1
    {{1, 3, 12}}               // Phase 2
}

Output: 47

Explanation:
- Using only Phase 0, cities are not connected.
- Using Phase 0 and Phase 1, cities can be connected. One optimal solution is to use the highway segments (0, 1, 10), (1, 2, 15), and (2, 3, 20), resulting in a total cost of 45.  Another is to use (0,1,10), (1,2,15) and (0,3,5), resulting in a cost of 30.
- Using Phase 0, Phase 1 and Phase 2 does not change the earliest phase we can connect the cities.
- To connect the cities with a minimum cost of 30, we use roads (0,1,10), (1,2,15), (0,3,5).
```

**Scoring:**

The solution will be judged on correctness and efficiency.  Solutions that do not connect all cities or fail to find the minimum cost within the earliest possible phase will receive a lower score.  Solutions with high time complexity will be penalized. Efficiency is crucial for passing all test cases.
