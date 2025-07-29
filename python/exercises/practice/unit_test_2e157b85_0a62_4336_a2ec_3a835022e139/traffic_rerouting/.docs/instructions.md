Okay, here's a challenging problem designed for a high-level programming competition. It combines graph algorithms, optimization, and real-world constraints.

**Problem Title: Optimal Traffic Rerouting for Emergency Evacuation**

**Problem Description:**

A major city is represented as a directed graph, where nodes represent intersections and edges represent one-way streets. Each edge has a capacity, representing the maximum number of vehicles that can traverse that street per unit of time, and a travel time, representing the time it takes to traverse that street.

Due to an imminent natural disaster, the city needs to evacuate its residents to a single designated safe zone located at a specific node in the graph. Each intersection (node) has a population count representing the number of vehicles needing to evacuate from that intersection.

The goal is to determine the optimal set of street capacity adjustments (rerouting) to minimize the total evacuation time. You can increase or decrease the capacity of each street by a certain percentage (**not to exceed 50% increase and 50% decrease**). Capacity adjustment comes at a cost. Each 1% (of the original capacity) increase on a street costs 'increase_cost' and each 1% (of the original capacity) decrease on a street costs 'decrease_cost'.

Your task is to write a program that calculates:

1.  The **minimum total evacuation time** for all residents to reach the safe zone, considering optimal traffic rerouting. The total evacuation time is the sum of the time each vehicle takes to reach the safe zone.
2.  The **total cost** for increasing and decreasing the capacity based on the percentage changes you have implemented.

**Input:**

*   `n`: The number of intersections (nodes) in the city.
*   `m`: The number of streets (edges) in the city.
*   `edges`: A list of tuples, where each tuple `(u, v, capacity, travel_time)` represents a directed street from intersection `u` to intersection `v` with the given `capacity` and `travel_time`.  Node indices are 0-based.
*   `population`: A list of integers, where `population[i]` represents the number of vehicles at intersection `i`.
*   `safe_zone`: The index of the safe zone intersection.
*   `increase_cost`: The cost to increase the capacity of a street by 1%.
*   `decrease_cost`: The cost to decrease the capacity of a street by 1%.

**Output:**

A tuple: `(minimum_total_evacuation_time, total_capacity_adjustment_cost)`

**Constraints and Considerations:**

*   1 <= n <= 100
*   1 <= m <= 500
*   1 <= capacity <= 100
*   1 <= travel_time <= 100
*   0 <= population[i] <= 1000
*   0 <= safe\_zone < n
*   1 <= increase\_cost <= 10
*   1 <= decrease\_cost <= 10
*   The graph may not be fully connected.  If a node cannot reach the safe zone, its population should not be included in the total evacuation time.
*   You are allowed to use fractional vehicle flow (e.g., a street can have 2.5 vehicles passing through it per unit of time) for the sake of the problem.
*   The solution must be reasonably efficient.  Brute-force approaches will likely time out.  Consider algorithms that effectively explore the search space of possible capacity adjustments.
*   The graph could contain cycles.
*   Minimize the total evacuation time as the primary goal. Only then, minimize the total capacity adjustment cost.

**Example:**

```
n = 4
m = 5
edges = [
    (0, 1, 10, 2),  # Intersection 0 to 1, capacity 10, travel time 2
    (0, 2, 5, 3),   # Intersection 0 to 2, capacity 5, travel time 3
    (1, 3, 15, 1),  # Intersection 1 to 3, capacity 15, travel time 1
    (2, 3, 7, 2),   # Intersection 2 to 3, capacity 7, travel time 2
    (0, 3, 3, 5)    # Intersection 0 to 3, capacity 3, travel time 5
]
population = [100, 50, 75, 0] # Population at intersections 0, 1, 2, 3
safe_zone = 3
increase_cost = 2
decrease_cost = 1

# Expected Output (Illustrative - the exact values will depend on the optimal solution):
# (approximate_minimum_total_evacuation_time, approximate_total_capacity_adjustment_cost)
# For example: (650, 50)

```

**Judging Criteria:**

*   **Correctness:**  The solution must produce the correct minimum total evacuation time and total capacity adjustment cost for all test cases.
*   **Efficiency:**  The solution must be efficient enough to solve the test cases within a reasonable time limit.
*   **Optimality:** The degree to which the program's answer matches the optimal answer.
*   **Code Clarity:** Code should be reasonably well-structured and commented.

This problem requires a solid understanding of graph algorithms, particularly flow networks, shortest paths, and optimization techniques.  It encourages thinking about how to balance competing objectives (evacuation time vs. cost) and how to handle complex constraints. Good luck!
