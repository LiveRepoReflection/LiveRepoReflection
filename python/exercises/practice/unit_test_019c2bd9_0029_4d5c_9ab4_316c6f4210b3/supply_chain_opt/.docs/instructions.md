## Project Name

`SupplyChainOptimization`

## Question Description

You are tasked with optimizing a supply chain for a large manufacturing company. The supply chain consists of a network of interconnected entities: factories, warehouses, and distribution centers. Each entity has a limited capacity for production, storage, or transportation, respectively. The goal is to determine the most efficient way to move raw materials from factories to distribution centers to meet customer demand, minimizing overall costs.

**Specifically:**

1.  **Network Representation:** The supply chain is represented as a directed graph. Nodes represent entities (factories, warehouses, distribution centers), and edges represent transportation routes between them. Each edge has a `capacity` (maximum amount of material that can be transported) and a `cost_per_unit` (cost to transport one unit of material along that route).
2.  **Entity Types:** Each node is one of three types:
    *   **Factory:** Produces raw materials. Has a `production_capacity`.
    *   **Warehouse:** Stores materials temporarily. Has a `storage_capacity`.
    *   **Distribution Center:** Receives materials to meet customer demand. Has a `demand`.
3.  **Optimization Goal:** Minimize the total transportation cost while satisfying all customer demands and respecting the capacities of all entities and routes.  The total transportation cost is the sum of (flow through each edge * cost per unit on that edge).
4.  **Constraints:**
    *   **Capacity Constraints:** The flow through any edge cannot exceed its capacity. The amount of material produced by a factory cannot exceed its production capacity. The amount of material stored in a warehouse cannot exceed its storage capacity.
    *   **Demand Satisfaction:** The total amount of material received by each distribution center must meet its demand.
    *   **Flow Conservation:** For each warehouse, the total inflow must equal the total outflow.
    *   **Non-negativity:** The flow through each edge must be non-negative.
5.  **Input:**
    *   A list of nodes, where each node is a dictionary with the following keys: `id` (unique identifier), `type` (`factory`, `warehouse`, or `distribution_center`), and capacity/demand depending on the type.
    *   A list of edges, where each edge is a dictionary with the following keys: `source` (source node id), `destination` (destination node id), `capacity`, and `cost_per_unit`.
6.  **Output:**
    *   A dictionary representing the optimal flow through each edge in the network. The dictionary should have edge tuples (source, destination) as keys and the optimal flow amount as values.
    *   Return None if no feasible solution exists that satisfies all constraints.

**Example Input (Illustrative - actual inputs will be much larger):**

```python
nodes = [
    {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
    {'id': 'W1', 'type': 'warehouse', 'storage_capacity': 80},
    {'id': 'D1', 'type': 'distribution_center', 'demand': 70},
    {'id': 'D2', 'type': 'distribution_center', 'demand': 30}
]

edges = [
    {'source': 'F1', 'destination': 'W1', 'capacity': 60, 'cost_per_unit': 2},
    {'source': 'F1', 'destination': 'D1', 'capacity': 40, 'cost_per_unit': 5},
    {'source': 'W1', 'destination': 'D1', 'capacity': 50, 'cost_per_unit': 3},
    {'source': 'W1', 'destination': 'D2', 'capacity': 30, 'cost_per_unit': 4}
]
```

**Constraints & Considerations:**

*   The input graph can be complex, with many nodes and edges.
*   The number of factories, warehouses, and distribution centers can vary.
*   The capacity and demand values can be large.
*   Edge costs can vary significantly.
*   Multiple valid solutions might exist; you need to find the one with the minimum total transportation cost.
*   Efficiency is critical.  Brute-force approaches will not work for large graphs.  Consider leveraging optimization libraries and algorithms.
*   Handle edge cases gracefully, such as disconnected graphs or infeasible scenarios.

**Expected Complexity:**

This problem requires a strong understanding of graph algorithms, optimization techniques (e.g., linear programming), and efficient coding practices. A correct and efficient solution should be able to handle large-scale supply chain networks within reasonable time and memory constraints. This is expected to be a LeetCode Hard level problem.
