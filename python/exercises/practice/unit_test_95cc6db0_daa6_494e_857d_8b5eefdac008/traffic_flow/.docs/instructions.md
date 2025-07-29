Okay, here's a challenging problem designed with the specifications you provided.

### Project Name

```
optimal-traffic-flow
```

### Question Description

You are tasked with designing an optimal traffic flow system for a city represented as a directed graph. The city has `N` intersections (nodes) numbered from `0` to `N-1`, and `M` one-way streets (edges) connecting them. Each street has a capacity, representing the maximum number of vehicles that can pass through it per unit of time.

The city also has `K` designated "source" intersections, where traffic originates, and `K` corresponding "destination" intersections, where traffic needs to flow.  Each source intersection has a specified traffic demand (vehicles originating per unit of time), and each destination intersection has a corresponding traffic capacity (maximum vehicles it can absorb per unit of time). The total traffic demand from all sources is guaranteed to be equal to the total traffic capacity of all destinations.

Your goal is to determine the maximum possible traffic flow that can be routed from the sources to the destinations, respecting both street capacities and destination capacities. Furthermore, you need to provide the flow on each street in the city that achieves this maximum flow.

However, there's a catch! The city's infrastructure is old, and some streets are prone to congestion.  For each street, you are given a "congestion factor," which is a positive integer.  The overall "congestion score" of a traffic flow configuration is the sum of (flow on each street * congestion factor of that street) across all streets.

Your primary objective is to maximize the total traffic flow from sources to destinations. Among all traffic flow configurations that achieve this maximum flow, you must find the configuration with the *minimum* possible congestion score.

**Input:**

*   `N`: The number of intersections (nodes).
*   `M`: The number of streets (edges).
*   `edges`: A list of tuples `(u, v, capacity, congestion_factor)`, where:
    *   `u` is the source intersection of the street.
    *   `v` is the destination intersection of the street.
    *   `capacity` is the capacity of the street (non-negative integer).
    *   `congestion_factor` is the congestion factor of the street (positive integer).
*   `sources`: A list of tuples `(node, demand)`, where:
    *   `node` is the index of a source intersection.
    *   `demand` is the traffic demand originating from that intersection.
*   `destinations`: A list of tuples `(node, capacity)`, where:
    *   `node` is the index of a destination intersection.
    *   `capacity` is the traffic capacity of that intersection.

**Output:**

A dictionary representing the flow on each street, structured as: `{(u, v): flow}`, where:

*   `(u, v)` is a tuple representing the street from intersection `u` to intersection `v`.
*   `flow` is the amount of traffic flowing on that street in the optimal solution (non-negative integer).

**Constraints:**

*   `1 <= N <= 200`
*   `1 <= M <= 1000`
*   `1 <= K <= N` (number of sources/destinations)
*   `0 <= capacity <= 1000` for each street.
*   `1 <= congestion_factor <= 100` for each street.
*   `0 <= demand <= 1000` for each source.
*   `0 <= capacity <= 1000` for each destination.
*   The sum of all source demands equals the sum of all destination capacities.
*   It's guaranteed that a feasible solution exists.

**Example:**

```python
N = 4
M = 5
edges = [
    (0, 1, 10, 2),  # u, v, capacity, congestion_factor
    (0, 2, 5, 1),
    (1, 2, 15, 3),
    (1, 3, 7, 1),
    (2, 3, 8, 2)
]
sources = [(0, 10)]  # node, demand
destinations = [(3, 10)]  # node, capacity

# Expected output (example - the actual flows might be different but should fulfill the conditions)
# {
#   (0, 1): 10,
#   (0, 2): 0,
#   (1, 2): 0,
#   (1, 3): 10,
#   (2, 3): 0
# }
```

**Judging Criteria:**

*   **Correctness:** The solution must achieve the maximum possible traffic flow.
*   **Optimality:** Among all solutions achieving maximum flow, the solution must have the minimum possible congestion score.
*   **Efficiency:** The solution must be efficient enough to handle the given constraints within a reasonable time limit.
*   **Edge Cases:**  Consider edge cases such as disconnected graphs, zero capacities, and scenarios where multiple optimal solutions with the same minimum congestion score exist. Your code should produce one valid, optimal solution.

**Hints:**

*   This problem combines concepts from network flow and optimization. Consider using the Ford-Fulkerson algorithm or Edmonds-Karp algorithm to find the maximum flow.
*   To minimize the congestion score among maximum flow solutions, you might explore techniques like minimum cost maximum flow algorithms or linear programming. Be mindful of time complexity.
*   Think about how to represent the graph and flow efficiently.

This problem requires a solid understanding of graph algorithms, optimization techniques, and careful consideration of edge cases and efficiency. Good luck!
