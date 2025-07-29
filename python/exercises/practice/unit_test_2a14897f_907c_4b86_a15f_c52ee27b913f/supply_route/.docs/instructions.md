## Problem: Optimal Supply Chain Routing

### Description

You are tasked with optimizing the delivery routes for a large e-commerce company. The company has a network of warehouses and delivery hubs across the country. Each hub serves a specific set of geographical regions, and the company needs to fulfill orders efficiently.

**Input:**

*   A list of warehouses, each with a location (latitude, longitude) and a maximum outgoing capacity (number of packages per hour).
*   A list of delivery hubs, each with a location (latitude, longitude), a demand rate (number of packages per hour), and the warehouse it must receive packages from.
*   A matrix representing the estimated travel time (in minutes) between each warehouse and delivery hub. This matrix is pre-computed using historical traffic data and distance calculations. Note that travel times are NOT symmetric, i.e. travel from warehouse A to hub B may differ from travel from hub B to warehouse A.
*   A maximum allowable delivery time (in minutes) for any package. Packages that take longer than this time to reach their destination incur a significant penalty.
*   A cost-per-package for each route, representing the cost of transporting a package from a given warehouse to a given hub.

**Constraints:**

*   Each delivery hub must be served by exactly one warehouse.
*   The total outgoing capacity of each warehouse cannot be exceeded.
*   The delivery time for each package (warehouse to hub) must be less than or equal to the maximum allowable delivery time.
*   The total cost of the delivery network must be minimized.
*   The number of warehouses and delivery hubs can be large (up to 1000 each).
*   Demand rate and outgoing capacity are integers.

**Output:**

*   A dictionary or similar data structure representing the optimal routing plan. For each delivery hub, specify the warehouse it should receive packages from.
*   The total cost of the optimized delivery network.
*   A boolean value indicating whether a feasible solution was found. It is possible that the constraints are too strict, and no routing plan can satisfy all requirements. In this case, return `False` and a cost of `Infinity`.

**Optimization Goal:**

Minimize the total cost of the delivery network while satisfying all constraints. The cost is calculated as the sum of the cost-per-package for each route multiplied by the demand of the delivery hub.

**Example:**

```
Warehouses:
[
    {'location': (34.0522, -118.2437), 'capacity': 100},  # Los Angeles
    {'location': (40.7128, -74.0060), 'capacity': 150}   # New York
]

Delivery Hubs:
[
    {'location': (37.7749, -122.4194), 'demand': 60, 'warehouse': None},  # San Francisco
    {'location': (41.8781, -87.6298), 'demand': 80, 'warehouse': None},   # Chicago
    {'location': (33.4484, -112.0740), 'demand': 40, 'warehouse': None}    # Phoenix
]

Travel Times:
[
    [300, 2400],  # LA to SF, Chicago
    [2400, 120]  # NY to SF, Chicago
]

Cost-per-package:
[
    [1.0, 2.0, 1.5],  # Cost from LA to SF, Chicago, Phoenix
    [2.5, 1.5, 3.0]   # Cost from NY to SF, Chicago, Phoenix
]

Max Allowable Delivery Time: 360 minutes

Expected Output (Illustrative):
{
    'San Francisco': 'Los Angeles',
    'Chicago': 'New York',
    'Phoenix': 'Los Angeles'
},
Total Cost: 60 * 1.0 + 80 * 1.5 + 40 * 1.5 = 240
Feasible Solution: True
```

**Grading Criteria:**

*   Correctness: The solution must produce a valid routing plan that satisfies all constraints.
*   Optimality: The solution should minimize the total cost of the delivery network as much as possible.  Solutions that are closer to the optimal cost will receive higher scores.
*   Efficiency: The solution should be able to handle large inputs (up to 1000 warehouses and 1000 delivery hubs) within a reasonable time limit (e.g., 5 minutes).
*   Handling Infeasibility: The code should correctly detect and handle cases where a feasible solution does not exist.

This problem requires a combination of algorithmic thinking, data structure design, and optimization techniques. Potential approaches include greedy algorithms, linear programming, and heuristics. The challenge lies in finding a balance between solution quality and computational efficiency.
