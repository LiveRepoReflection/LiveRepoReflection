## Problem: Optimal Disaster Response Network Design

**Problem Description:**

A catastrophic earthquake has struck a region, severely damaging the existing infrastructure. You are tasked with designing an optimal disaster response network to efficiently distribute essential resources (food, medicine, shelter) from a set of strategically located supply depots to a set of affected cities.

You are given the following information:

*   **Cities:** A list of `n` cities, each with a known population `population[i]` and a location represented by (x, y) coordinates. Each city `i` has a demand `demand[i]` representing the amount of resources it requires.
*   **Depots:** A list of `m` potential supply depot locations, each with a maximum capacity `capacity[j]` representing the total amount of resources it can store. Each depot also has (x,y) coordinates.
*   **Transportation Network:** Initially, there are no direct connections between cities and depots. You can establish bidirectional transportation routes between any city and any depot.
*   **Transportation Cost:** The cost of establishing a transportation route between a city `i` and a depot `j` is proportional to the Euclidean distance between them: `cost = distance(city[i], depot[j]) * cost_per_unit`.

**Objective:**

Design a transportation network that minimizes the total cost of establishing routes while ensuring that all cities' demands are fully satisfied and no depot exceeds its capacity. Additionally, due to the urgency of the situation, minimize the maximum delay in resource delivery to any city.

**Constraints:**

*   **Demand Satisfaction:** The total amount of resources delivered to each city must be equal to or greater than its demand.
*   **Depot Capacity:** The total amount of resources shipped from each depot must be less than or equal to its capacity.
*   **Network Connectivity:** Every city must be reachable from at least one depot.
*   **Integer Resources:** The amount of resources transported between each city and depot must be a non-negative integer.
*   **Delay Minimization:** For each city `i`, the delay is defined as the distance between that city and the closest depot supplying it with resources (where distance is Euclidean). You must minimize the *maximum* delay across all cities.

**Input:**

*   `cities`: A list of tuples, where each tuple represents a city: `(x, y, population, demand)`.
*   `depots`: A list of tuples, where each tuple represents a depot: `(x, y, capacity)`.
*   `cost_per_unit`: A floating-point number representing the cost per unit distance for establishing a transportation route.

**Output:**

A dictionary representing the optimal transportation network. The keys are city indices, and the values are dictionaries. For each city, the inner dictionary maps depot indices to the amount of resources transported from that depot to the city.

```python
{
  0: { # city 0
    0: 10, # from depot 0, 10 units of resource
    1: 5  # from depot 1, 5 units of resource
  },
  1: { # city 1
    2: 20 # from depot 2, 20 units of resource
  },
  ...
}

```

**Example:**

```python
cities = [(0, 0, 1000, 15), (10, 0, 500, 10), (5, 5, 750, 20)]
depots = [(0, 10, 30), (10, 10, 25)]
cost_per_unit = 1.0

# Expected (but not necessarily unique) output format:
# {
#   0: {0: 15},  # City 0 gets 15 from depot 0
#   1: {1: 10},  # City 1 gets 10 from depot 1
#   2: {0: 15, 1: 5}   # City 2 gets 15 from depot 0 and 5 from depot 1
# }
```

**Constraints for Evaluation:**

*   `1 <= n <= 50` (number of cities)
*   `1 <= m <= 20` (number of depots)
*   `1 <= population[i] <= 10000`
*   `1 <= demand[i] <= 50`
*   `1 <= capacity[j] <= 100`
*   `0.1 <= cost_per_unit <= 10.0`
*   The coordinates (x, y) for cities and depots are integers between 0 and 100.
*   All demands can be met within the total capacities of all depots.

**Scoring:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** Does your solution satisfy all the constraints (demand, capacity, connectivity)?
2.  **Cost Minimization:** How close is the total cost of your solution to the optimal cost?
3.  **Maximum Delay Minimization:** How low is the maximum delay among all the cities?

A weighted scoring system will be used, giving higher weight to correctness, followed by cost minimization, and then delay minimization. Solutions that fail to satisfy the constraints will receive a score of 0.

**Hints:**

*   Consider using linear programming or network flow algorithms to find the optimal resource allocation.
*   The delay minimization requirement adds an extra layer of complexity, potentially requiring heuristics or approximation algorithms.
*   Start with a simple solution that satisfies the constraints and then iteratively improve it to minimize cost and delay.
*   Think about how to efficiently search the solution space given the constraints.
*   Precomputing distances between cities and depots can improve performance.
