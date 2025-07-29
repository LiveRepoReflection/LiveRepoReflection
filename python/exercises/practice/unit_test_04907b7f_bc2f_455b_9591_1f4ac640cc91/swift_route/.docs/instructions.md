## Question Title: Optimizing Inter-City Package Delivery

**Question Description:**

A national logistics company, "SwiftRoute," is facing a major challenge in optimizing its inter-city package delivery network. They operate a fleet of trucks that travel between various cities, each with its own delivery demands and warehouse capacity. The goal is to minimize the overall delivery cost, which is a function of distance traveled and the number of trucks used, while satisfying all delivery requirements and respecting warehouse capacities.

You are given the following information:

*   **Cities:** A list of cities, each identified by a unique ID and having a warehouse with a maximum capacity (in package units).
*   **Road Network:** A weighted graph representing the road network connecting the cities. The nodes are cities, and the edges represent roads with associated distances (weights).
*   **Delivery Demands:** A list of delivery requests, each specifying a source city, a destination city, and the number of packages to be delivered.
*   **Truck Capacity:** Each truck has a fixed capacity for the number of packages it can carry.
*   **Truck Cost:** A fixed cost associated with using each truck, regardless of distance traveled.
*   **Distance Cost:** A cost per unit distance traveled by each truck.

Your task is to write a Python function that determines the optimal delivery plan. The function should:

1.  **Determine the minimum number of trucks required.** Since using a truck incurs a cost, you should aim to minimize the number of trucks used.
2.  **Determine the routes each truck should take.** Each truck can make multiple deliveries along a route, but must return to its starting city (any city with a warehouse, chosen strategically).
3.  **Ensure that warehouse capacities are never exceeded.** The total number of packages entering or leaving a warehouse cannot exceed its capacity.
4.  **Satisfy all delivery demands.** All packages must be delivered from their source to their destination.
5.  **Minimize the total delivery cost.** The total cost is the sum of the truck costs (number of trucks \* truck cost) and the distance costs (total distance traveled by all trucks \* distance cost per unit).

**Input:**

Your function should accept the following inputs:

*   `cities`: A dictionary where keys are city IDs (integers) and values are warehouse capacities (integers).  E.g., `{1: 1000, 2: 500, 3: 750}`
*   `road_network`: A list of tuples, where each tuple represents a road: `(city1_id, city2_id, distance)`. E.g., `[(1, 2, 150), (1, 3, 200), (2, 3, 100)]`
*   `delivery_demands`: A list of tuples, where each tuple represents a delivery request: `(source_city_id, destination_city_id, num_packages)`. E.g., `[(1, 2, 200), (2, 3, 300), (1, 3, 150)]`
*   `truck_capacity`: An integer representing the number of packages a single truck can carry. E.g., `300`
*   `truck_cost`: A float representing the cost of using a single truck. E.g., `1000.0`
*   `distance_cost_per_unit`: A float representing the cost per unit distance traveled by a truck. E.g., `2.0`

**Output:**

Your function should return a dictionary representing the optimal delivery plan. The dictionary should have the following structure:

```python
{
    "trucks": [
        {
            "route": [city_id1, city_id2, ..., city_id1],  # Route the truck takes, returning to starting city
            "packages": [(source_city_id, destination_city_id, num_packages), ...], # List of deliveries made on this route
        },
        ...
    ],
    "total_cost": total_delivery_cost  # Float representing the total cost
}
```

**Constraints:**

*   Number of cities: 2 <= N <= 20
*   Number of roads: N-1 <= M <= N\*(N-1)/2
*   Warehouse capacities: 100 <= capacity <= 2000
*   Number of delivery requests: 1 <= K <= 50
*   Number of packages per delivery request: 50 <= packages <= 500
*   Truck capacity: 100 <= capacity <= 500
*   Truck cost: 500 <= cost <= 2000
*   Distance cost per unit: 1.0 <= cost <= 5.0
*   Distances between cities are positive integers.
*   You can assume that there is always a path between any two cities.
*   Assume all cities are interconnected directly or indirectly via roads.

**Example:**

```python
cities = {1: 1000, 2: 500, 3: 750}
road_network = [(1, 2, 150), (1, 3, 200), (2, 3, 100)]
delivery_demands = [(1, 2, 200), (2, 3, 300), (1, 3, 150)]
truck_capacity = 300
truck_cost = 1000.0
distance_cost_per_unit = 2.0

optimal_plan = solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit)

print(optimal_plan)
```

**Grading Criteria:**

*   Correctness: The solution must satisfy all delivery demands and warehouse capacity constraints.
*   Optimality: The solution must minimize the total delivery cost. (Partial credit will be given for solutions that are close to optimal).
*   Efficiency: The solution must run within a reasonable time limit (e.g., 5 minutes).
*   Code Quality: The code should be well-structured, readable, and properly documented.
*   Handling Edge Cases:  The solution must handle various edge cases gracefully (e.g., no delivery demands, single city, etc.).

This is a challenging optimization problem that requires careful consideration of multiple factors and potentially the use of advanced algorithms and heuristics. Good luck!
