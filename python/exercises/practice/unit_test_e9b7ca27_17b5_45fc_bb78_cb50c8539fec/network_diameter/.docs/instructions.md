## Project Name

`OptimalNetworkDeployment`

## Question Description

A telecommunications company is planning to deploy a high-speed fiber optic network to connect `N` cities. The cities are numbered from `1` to `N`. The company has a list of potential bidirectional connections between cities, each with an associated cost (laying fiber, permits, etc.) and a latency (signal delay due to distance, equipment, etc.). The company wants to deploy the network such that:

1.  **Connectivity:** Every city must be connected to the network, either directly or indirectly through other cities.
2.  **Budget Constraint:** The total cost of the deployed connections must not exceed a given budget `B`.
3.  **Latency Minimization:** Among all possible network deployments that satisfy the connectivity and budget constraints, the company wants to minimize the maximum latency between any two cities in the network. This value is the *network diameter*.

You are given:

*   `N`: The number of cities.
*   `B`: The maximum budget.
*   `connections`: A list of tuples, where each tuple `(city1, city2, cost, latency)` represents a potential bidirectional connection between `city1` and `city2` with the given `cost` and `latency`.

Your task is to write a function that determines the *minimum possible network diameter* achievable under the given connectivity and budget constraints. If no feasible network deployment exists, return `-1`.

**Constraints:**

*   `1 <= N <= 100`
*   `0 <= B <= 10000`
*   The number of connections is at most `N * (N - 1) / 2`.
*   `1 <= city1, city2 <= N`
*   `city1 != city2`
*   `1 <= cost <= 100`
*   `1 <= latency <= 100`
*   There might be multiple connections between the same two cities.
*   You can select any subset of connections to build the network.

**Optimization Requirements:**

*   The solution should be efficient, as a naive brute-force approach will likely time out.  Consider using appropriate algorithms and data structures to optimize the solution.

**Example:**

```python
N = 4
B = 200
connections = [
    (1, 2, 50, 10),
    (1, 3, 75, 15),
    (1, 4, 100, 20),
    (2, 3, 60, 12),
    (2, 4, 80, 16),
    (3, 4, 40, 8)
]

# Expected output: 28
# Explanation:
# One possible optimal solution is to use the connections (1, 2, 50, 10), (1, 3, 75, 15), and (3, 4, 40, 8).
# The total cost is 50 + 75 + 40 = 165 <= 200.
# The maximum latency between any two cities is:
# - 1 and 2: 10
# - 1 and 3: 15
# - 1 and 4: 15 + 8 = 23
# - 2 and 3: 10 + 15 = 25
# - 2 and 4: 10 + 15 + 8 = 33
# - 3 and 4: 8

# The network diameter is then found by shortest path between each node pair (using Dijkstra or similar), which gives:
# 1-2: 10
# 1-3: 15
# 1-4: 23
# 2-3: 25
# 2-4: 33
# 3-4: 8
# Max path is then 33
# Better path is 1-2, 2-3, 3-4,
# Cost is 50 + 60 + 40 = 150 < 200
# Latency 1-2: 10
# Latency 1-3: 10 + 12 = 22
# Latency 1-4: 10 + 12 + 8 = 30
# Latency 2-3: 12
# Latency 2-4: 12+8 = 20
# Latency 3-4: 8
# Shortest path between all nodes using Floyd-Warshall
# [0, 10, 22, 30]
# [10, 0, 12, 20]
# [22, 12, 0, 8]
# [30, 20, 8, 0]
# Max path is 30

# Even better. Build 1-2, 1-3, 3-4
# Cost = 50 + 75 + 40 = 165
# [0, 10, 15, 23]
# [10, 0, 25, 33]
# [15, 25, 0, 8]
# [23, 33, 8, 0]
# Max path is 33
# The true minimal is 30.

```

**Function Signature:**

```python
def find_min_network_diameter(N: int, B: int, connections: list[tuple[int, int, int, int]]) -> int:
    """
    Finds the minimum possible network diameter achievable under the given constraints.

    Args:
        N: The number of cities.
        B: The maximum budget.
        connections: A list of tuples, where each tuple (city1, city2, cost, latency) represents a potential connection.

    Returns:
        The minimum possible network diameter, or -1 if no feasible network deployment exists.
    """
    pass  # Replace with your solution
```
