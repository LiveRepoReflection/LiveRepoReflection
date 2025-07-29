## Question: Optimized Supply Chain Network Design

**Problem Description:**

You are tasked with designing an optimal supply chain network for a large e-commerce company. The company has `n` warehouses and `m` customer zones. Each warehouse has a limited capacity to store and ship products, and each customer zone has a specific demand for these products. The goal is to minimize the total cost of transporting goods from warehouses to customer zones while meeting all customer demands and respecting warehouse capacities.

**Input:**

*   `warehouses`: A list of tuples, where each tuple represents a warehouse and contains the following information: `(warehouse_id, capacity)`. `warehouse_id` is a unique integer identifier for the warehouse, and `capacity` is the maximum amount of product the warehouse can ship.
*   `customer_zones`: A list of tuples, where each tuple represents a customer zone and contains the following information: `(zone_id, demand)`. `zone_id` is a unique integer identifier for the customer zone, and `demand` is the amount of product the customer zone needs.
*   `transportation_costs`: A dictionary where keys are tuples `(warehouse_id, zone_id)` and values are the cost per unit of product transported between the specified warehouse and customer zone.  If a key is missing, it indicates there is no direct route.
*   `fixed_warehouse_costs`: A dictionary where keys are `warehouse_id` and values are the fixed cost associated with opening and maintaining that warehouse.

**Output:**

A dictionary representing the optimal shipping plan. The keys of the dictionary are tuples `(warehouse_id, zone_id)`, and the values are the amount of product to ship from that warehouse to that zone. If no product should be shipped from a given warehouse to a given zone, that entry should *not* exist in the dictionary.

**Constraints:**

1.  **Demand Satisfaction:** The total amount of product shipped to each customer zone must equal its demand.
2.  **Capacity Constraints:** The total amount of product shipped from each warehouse must not exceed its capacity.
3.  **Non-negativity:** The amount of product shipped between any warehouse and customer zone must be a non-negative integer.
4.  **Connected Graph:** The graph formed by warehouses, customer zones, and existing transportation routes is guaranteed to be connected.
5.  **Cost Minimization:** The solution must minimize the *total* cost.  The total cost is the sum of the transportation costs *plus* the fixed warehouse costs for all warehouses that are used (shipping at least one item).
6.  **Warehouse Selection**: The algorithm **must** decide which warehouses to open, considering the fixed costs. Leaving a warehouse unopened (shipping zero items) reduces the fixed cost but might increase transportation costs.

**Optimization Requirements:**

*   The solution must be computationally efficient, especially for large input sizes (e.g., hundreds of warehouses and thousands of customer zones).  Consider the algorithmic complexity of your solution.
*   The solution must produce a near-optimal result within a reasonable time limit (e.g., a few minutes).

**Edge Cases and Considerations:**

*   There might be multiple optimal solutions. Your algorithm should find one of them.
*   The total warehouse capacity might be less than the total customer demand, making it impossible to satisfy all demands.  In this case, the algorithm must raise a `ValueError` exception with a descriptive message.
*   The transportation cost matrix might be sparse, meaning not all warehouses can ship to all customer zones.
*   Some warehouses may have very high fixed costs, making them undesirable to open even if they have low transportation costs.

**Example:**

```python
warehouses = [(1, 100), (2, 150)]
customer_zones = [(101, 80), (102, 120)]
transportation_costs = {
    (1, 101): 2,
    (1, 102): 5,
    (2, 101): 3,
    (2, 102): 1
}
fixed_warehouse_costs = {1: 50, 2: 75}

# An optimal solution might be:
# {
#   (1, 101): 80,
#   (2, 102): 120
# }
# Total cost: (80 * 2) + (120 * 1) + 50 + 75 = 160 + 120 + 50 + 75 = 405
```
