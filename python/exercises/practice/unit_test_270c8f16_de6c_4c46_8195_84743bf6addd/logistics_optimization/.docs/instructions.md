## The Global Logistics Network Optimization Problem

**Question Description:**

You are tasked with optimizing the global logistics network for a large multinational corporation. The corporation has warehouses located in various cities across the globe, and needs to transport goods between these warehouses to meet fluctuating demands.

The global logistics network can be represented as a directed graph, where:

*   Nodes represent warehouses, identified by a unique city ID (integer).
*   Edges represent transportation routes between warehouses. Each edge has the following properties:
    *   `source`: The city ID of the source warehouse.
    *   `destination`: The city ID of the destination warehouse.
    *   `capacity`: The maximum number of goods that can be transported along this route in a given time period (integer).
    *   `cost_per_unit`: The cost of transporting one unit of goods along this route (float).
    *   `transport_time`: The time (in hours) it takes to transport goods along this route (float).

You are given the following inputs:

*   A list of warehouses, where each warehouse is represented by its city ID (integer).
*   A list of transportation routes, as described above.
*   A list of demands for a specific time period. Each demand is represented by:
    *   `source`: The city ID of the source warehouse.
    *   `destination`: The city ID of the destination warehouse.
    *   `quantity`: The number of goods that need to be transported from the source to the destination (integer).
    *   `deadline`: The latest time (in hours from the start of the period) by which the goods must arrive at the destination (float).

Your goal is to determine the optimal transportation plan that satisfies all demands while minimizing the total transportation cost. The transportation plan should specify the quantity of goods to be transported along each route.

**Constraints and Requirements:**

1.  **Demand Satisfaction:** All demands must be fully satisfied within their respective deadlines.
2.  **Capacity Constraints:** The total quantity of goods transported along any route must not exceed its capacity.
3.  **Cost Minimization:** The total transportation cost (sum of `quantity * cost_per_unit` for each route used) must be minimized.
4.  **Time Constraints:** Goods must arrive at the destination warehouse no later than the specified deadline, considering the `transport_time` for each route used. The transport time is fixed for each route and is not dependent on the quantity of goods transported.
5.  **Integer Goods:** The quantity of goods transported along each route must be an integer. You cannot transport fractions of goods.
6.  **Large-Scale Network:** The logistics network can be large, with thousands of warehouses and transportation routes. Your solution must be computationally efficient.
7.  **Dynamic Routing:** A single demand can be satisfied by transporting goods through multiple intermediate warehouses (i.e., using multiple routes).
8.  **Cycle Handling**: The graph might contain cycles. Your solution must handle cycles without getting stuck in infinite loops.
9.  **No Negative Flow:** The flow of goods must always be non-negative.
10. **Feasibility Check**: If it is not possible to satisfy all demands within the given constraints, your solution should report that the problem is infeasible.

**Output:**

Your solution should output:

*   A dictionary representing the transportation plan. The keys should be tuples `(source_city_id, destination_city_id)` representing the routes used, and the values should be the quantity of goods transported along that route (integer).
*   The total transportation cost (float).
*   If the problem is infeasible, output "Infeasible".

**Example Input (Simplified):**

```python
warehouses = [1, 2, 3]
routes = [
    {"source": 1, "destination": 2, "capacity": 100, "cost_per_unit": 1.0, "transport_time": 2.0},
    {"source": 2, "destination": 3, "capacity": 80, "cost_per_unit": 1.5, "transport_time": 3.0},
    {"source": 1, "destination": 3, "capacity": 50, "cost_per_unit": 2.0, "transport_time": 5.0},
]
demands = [
    {"source": 1, "destination": 3, "quantity": 70, "deadline": 8.0},
]
```

This problem requires a combination of graph algorithms, optimization techniques (potentially linear programming or network flow algorithms), and careful handling of constraints. Efficient implementations are crucial for handling large-scale networks. Good luck!
