## Project Name

**Optimal Warehousing**

## Question Description

A large e-commerce company, "GlobalMart," operates a network of warehouses across the country. Each warehouse has a limited storage capacity (in cubic meters) and a fixed daily operational cost. GlobalMart needs to fulfill a large number of customer orders daily, each consisting of a set of products with specific volumes.

You are tasked with designing an algorithm to optimally assign customer orders to warehouses to minimize the total daily cost. However, there are several constraints:

1.  **Warehouse Capacity:** Each warehouse has a maximum storage capacity. The total volume of orders assigned to a warehouse cannot exceed its capacity.
2.  **Order Splitting:** Orders *cannot* be split across multiple warehouses. Each order must be fulfilled entirely by a single warehouse.
3.  **Product Dependency:** Certain products must be shipped from specific warehouses due to specialized handling equipment or regulatory restrictions. These dependencies are defined as a list of (product ID, warehouse ID) pairs. If an order contains a product with a dependency, the entire order *must* be assigned to the specified warehouse.
4.  **Warehouse Proximity Preference:** For each customer order, there's a list of warehouses with proximity preferences, ranked from most to least preferred. The algorithm should prioritize assigning orders to preferred warehouses, given the other constraints. This ranking is a list of warehouse IDs, ordered from most preferred to least preferred.
5. **Dynamic Reprioritization**: Warehouse operational costs are dynamic and change based on external factors. Periodically, there's a need to re-evaluate the assignments with updated warehouse costs. The frequency of updates is high, so recalculation must be efficient.
6.  **Optimization Goal:** Minimize the *total* daily operational cost of the warehouses used to fulfill all orders. Assume each warehouse is either "used" (at least one order assigned to it) or "not used". Only "used" warehouses incur their daily operational cost.

**Input:**

Your function will receive the following inputs:

*   `warehouses`: A dictionary where keys are warehouse IDs (integers) and values are dictionaries with keys "capacity" (in cubic meters, integer) and "cost" (daily operational cost, integer). Example: `{1: {"capacity": 1000, "cost": 500}, 2: {"capacity": 1500, "cost": 700}}`
*   `orders`: A list of dictionaries, where each dictionary represents a customer order. Each order dictionary has the following keys:
    *   `order_id`: Unique identifier for the order (integer).
    *   `products`: A list of product IDs (integers).
    *   `volumes`: A list of product volumes (in cubic meters, integers), corresponding to the `products` list.
    *   `preferred_warehouses`: A list of warehouse IDs (integers), ordered from most preferred to least preferred.
    Example: `[{"order_id": 1, "products": [1, 2], "volumes": [100, 50], "preferred_warehouses": [1, 2]}, {"order_id": 2, "products": [3], "volumes": [200], "preferred_warehouses": [2, 1]}]`
*   `product_dependencies`: A list of tuples, where each tuple represents a (product ID, warehouse ID) dependency. Example: `[(1, 1), (3, 2)]`

**Output:**

Your function should return a dictionary where keys are warehouse IDs (integers) and values are lists of order IDs (integers) assigned to that warehouse. If an order cannot be fulfilled due to capacity constraints or dependencies, it should *not* be assigned to any warehouse. The solution must minimize the total daily cost of used warehouses. Example: `{1: [1], 2: [2]}`

**Constraints:**

*   Number of warehouses: 1 <= N <= 50
*   Number of orders: 1 <= M <= 500
*   Warehouse capacity: 100 <= Capacity <= 5000
*   Warehouse cost: 100 <= Cost <= 1000
*   Number of products per order: 1 <= K <= 10
*   Product volume: 1 <= Volume <= 500
*   The order of the order IDs in the list for each warehouse does not matter.
*   Your solution should be efficient enough to handle the constraints within a reasonable time limit (e.g., a few seconds).

**Efficiency Considerations:**

*   The problem is NP-hard, so finding the absolute optimal solution might be computationally expensive. Aim for a near-optimal solution within the time constraints.
*   Consider using heuristics, approximation algorithms, or optimization techniques like simulated annealing or genetic algorithms to find a good solution.
*   The frequent need to re-evaluate assignments with updated warehouse costs requires an efficient algorithm that can adapt to changes without restarting from scratch. Consider using incremental optimization techniques.

This problem requires careful consideration of data structures, algorithm design, and optimization techniques to achieve a satisfactory solution within the given constraints. Good luck!
