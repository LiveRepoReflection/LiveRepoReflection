Okay, here's a challenging Python coding problem designed to test advanced data structures, algorithmic thinking, and optimization.

**Problem Title:** Efficient Flight Planner

**Problem Description:**

You are given a directed graph representing an air transportation network. Each node in the graph represents an airport, and each directed edge represents a flight route between two airports. Each flight route has a cost associated with it, representing the price of the flight.

Your task is to implement an efficient flight planner that can answer queries about the cheapest way to travel between airports, subject to certain constraints.

Specifically, you are given the following:

*   **Airports:** A list of `n` airports, labeled from `0` to `n-1`.
*   **Flights:** A list of `m` directed flights, where each flight is represented as a tuple `(u, v, cost)`, meaning there is a flight from airport `u` to airport `v` with a cost of `cost`.
*   **Queries:** A list of `q` queries, where each query is represented as a tuple `(start, end, max_flights, max_cost)`. For each query, you need to find the minimum cost to travel from airport `start` to airport `end`, subject to the following constraints:
    *   You can take at most `max_flights` flights.
    *   The total cost of your journey cannot exceed `max_cost`.

**Constraints:**

*   `1 <= n <= 1000` (number of airports)
*   `1 <= m <= 5000` (number of flights)
*   `1 <= q <= 10000` (number of queries)
*   `0 <= u, v < n` (airport indices)
*   `1 <= cost <= 1000` (flight cost)
*   `0 <= start, end < n` (query start and end airports)
*   `1 <= max_flights <= 10` (maximum number of flights allowed)
*   `1 <= max_cost <= 10000` (maximum total cost allowed)
*   The graph might not be fully connected. There might not be a path between some pairs of airports.
*   The graph can contain cycles.
*   Multiple flights can exist between the same pair of airports (with potentially different costs).

**Input:**

The input will be provided in the following format:

```python
def solve_flight_planner(n: int, flights: list[tuple[int, int, int]], queries: list[tuple[int, int, int, int]]) -> list[int]:
    """
    Solves the flight planner problem.

    Args:
        n: The number of airports.
        flights: A list of flights, where each flight is a tuple (u, v, cost).
        queries: A list of queries, where each query is a tuple (start, end, max_flights, max_cost).

    Returns:
        A list of the minimum costs for each query.  If no path exists within the constraints, return -1 for that query.
    """
    # Your code here
    pass
```

**Output:**

The function should return a list of integers, where the `i`-th element is the minimum cost to travel from `start` to `end` for the `i`-th query, subject to the given constraints. If no path exists within the constraints, return `-1` for that query.

**Example:**

```python
n = 5
flights = [(0, 1, 10), (0, 2, 15), (1, 3, 12), (2, 3, 8), (3, 4, 5)]
queries = [(0, 4, 3, 30), (0, 4, 2, 25), (1, 4, 1, 10)]

result = solve_flight_planner(n, flights, queries)
print(result)  # Output: [30, -1, -1]

# Explanation:
# Query 1: (0, 4, 3, 30) - The path 0->1->3->4 has cost 10 + 12 + 5 = 27 <= 30 and takes 3 flights, so the answer is 27.
# Query 2: (0, 4, 2, 25) - There is no path from 0 to 4 with at most 2 flights and a total cost <= 25.
# Query 3: (1, 4, 1, 10) - There is no path from 1 to 4 with at most 1 flight and a total cost <= 10.
```

**Judging Criteria:**

*   Correctness: Your solution must produce the correct output for all valid inputs.
*   Efficiency: Your solution must be efficient enough to handle the given constraints within a reasonable time limit (e.g., a few seconds per test case).  Solutions that use brute-force or inefficient algorithms may time out.
*   Code Clarity: Your code should be well-structured, readable, and maintainable.

**Hints:**

*   Consider using dynamic programming or a modified version of Dijkstra's algorithm or Bellman-Ford algorithm to solve this problem.  Think about how to incorporate the `max_flights` and `max_cost` constraints into your algorithm.
*   Memoization can be helpful to avoid redundant calculations.
*   Careful optimization is necessary to achieve the required efficiency.

This problem requires a solid understanding of graph algorithms and dynamic programming. Good luck!
