Okay, I'm ready to craft a challenging coding problem. Here it is:

### Project Name

`OptimalRoutePlanner`

### Question Description

**Scenario:**

A large logistics company operates a network of warehouses across a country. Each warehouse has a limited capacity for storing goods. The company needs to deliver a set of orders, each specifying a source warehouse, a destination warehouse, and a quantity of goods. The company also has a fleet of trucks. Each truck has a maximum capacity.  The goal is to determine the *minimum number of trucks* required to deliver all the orders, respecting warehouse capacities and truck capacities.

**Detailed Problem:**

You are given the following inputs:

1.  `warehouses`: A dictionary where keys are warehouse IDs (strings) and values are their storage capacities (integers).
2.  `orders`: A list of tuples, where each tuple represents an order in the format `(source_warehouse_id, destination_warehouse_id, quantity)`.
3.  `truck_capacity`: An integer representing the maximum capacity of each truck.

**Constraints and Edge Cases:**

*   Warehouse Capacities: After fulfilling an order from a source warehouse, the inventory at that warehouse decreases. Similarly, upon delivery to a destination warehouse, the inventory increases. At no point can the inventory at a warehouse exceed its maximum capacity. You must maintain a record of the current inventory at each warehouse. Treat the initial inventory at each warehouse as zero.
*   Truck Capacity: A truck can only carry a quantity of goods up to its `truck_capacity`.
*   Order Splitting:  Orders can be split across multiple trucks. A single truck can also carry multiple orders. The origin and destination of the goods must remain consistent when splitting orders.
*   Warehouse Restrictions: If a warehouse does not have enough inventory on hand to fulfill an order, the remaining amount of the order cannot be split among other warehouses.
*   Optimization: You are evaluated on the *minimum* number of trucks used. Using more trucks than necessary will result in a lower score.
*   Efficiency: The number of warehouses can be large (up to 10,000), and the number of orders can be even larger (up to 100,000). Aim for a solution with a time complexity better than O(N\*M) where N is the number of warehouses and M is the number of orders.
*   Real-World Consideration: Account for the case where it is impossible to fulfill all orders (due to warehouse capacities or truck capacity). In this case, return `-1`.
*   Zero Quantity Orders: The list of orders may contain orders with zero quantity. The code must execute successfully while processing them.
*   Invalid Warehouse IDs: The `orders` list may contain warehouse IDs that are not present in the `warehouses` dictionary. In such cases, ignore these orders.
*   Integer Overflow: The quantity of goods and the truck capacity are integers. Handle potential integer overflows when performing calculations.
*   Multiple Valid Solutions: There might be multiple valid truck assignments that result in the minimum number of trucks. Any of these valid solutions is acceptable.

**Output:**

Return an integer representing the minimum number of trucks required to deliver all orders. If it is impossible to fulfill all orders, return `-1`.

**Example:**

```python
warehouses = {"A": 100, "B": 50, "C": 75}
orders = [("A", "B", 30), ("B", "C", 20), ("A", "C", 40)]
truck_capacity = 50

# Expected output: 2
# Explanation:
# Truck 1: Delivers 30 from A to B and 20 from B to C (capacity 50)
# Truck 2: Delivers 40 from A to C (capacity 50)
```

**Judging Criteria:**

Your solution will be judged based on the following criteria:

1.  **Correctness:** Does your solution correctly determine the minimum number of trucks for all valid input scenarios?
2.  **Completeness:** Does your solution handle all the specified constraints and edge cases?
3.  **Efficiency:** Is your solution efficient enough to handle large datasets within a reasonable time limit?
4.  **Optimality:** Does your solution consistently find the *minimum* number of trucks?
5.  **Code Quality:** Is your code well-structured, readable, and maintainable?

This problem is designed to test a candidate's ability to:

*   Model a real-world optimization problem.
*   Choose and apply appropriate data structures (dictionaries, heaps, etc.).
*   Design an efficient algorithm.
*   Handle complex constraints and edge cases.
*   Write clean and maintainable code.
Good luck!
