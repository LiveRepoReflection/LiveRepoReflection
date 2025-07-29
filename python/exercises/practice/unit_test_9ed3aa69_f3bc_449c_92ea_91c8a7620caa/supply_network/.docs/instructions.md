## Problem: Optimal Supply Chain Network Design

**Description:**

You are tasked with designing the optimal supply chain network for a global manufacturing company. The company produces a single product at various factories worldwide and distributes it to customer demand centers. Your goal is to minimize the total cost of the supply chain, considering both transportation costs and factory operating costs.

**Data:**

You are given the following information:

*   **Factories:** A list of factories, each with the following properties:
    *   `factory_id`: A unique identifier for the factory (string).
    *   `capacity`: The maximum amount of product the factory can produce in a given time period (integer).
    *   `operating_cost`: The cost to operate the factory for the time period, *regardless* of how much it produces (integer). If a factory is not used, this cost is not incurred.

*   **Demand Centers:** A list of demand centers, each with the following properties:
    *   `demand_center_id`: A unique identifier for the demand center (string).
    *   `demand`: The amount of product the demand center requires in the given time period (integer).

*   **Transportation Costs:** A matrix representing the cost of transporting one unit of product from each factory to each demand center. The matrix is represented as a dictionary: `{(factory_id, demand_center_id): cost}`. `cost` is an integer representing the transportation cost per unit. If a key (factory\_id, demand\_center\_id) is *not* present, it implies transportation between the factory and the demand center is impossible or prohibitively expensive and should be considered as an infinite cost (i.e., no product can be transported between them).

**Objective:**

Determine which factories to operate and how much product to ship from each operating factory to each demand center to satisfy all demand while minimizing the total cost.

**Constraints:**

*   **Demand Satisfaction:**  All demand at each demand center must be met.
*   **Factory Capacity:** The total amount of product shipped from a factory cannot exceed its capacity.
*   **Transportation Feasibility:**  Product can only be shipped between factories and demand centers where a transportation cost is defined in the transportation cost matrix.
*   **Integer Solution:** The amount of product shipped between a factory and a demand center must be an integer.
*   **Scalability:** The number of factories and demand centers can be large (up to 100 factories and 100 demand centers). Your solution must be efficient enough to handle such cases within a reasonable time (e.g., under 60 seconds for a single test case on a standard machine).
*   **No Partial Operation:** A factory is either fully operational (incurring the full operating cost) or not operational at all (incurring no operating cost). It is not possible to operate a factory at a reduced capacity and pay a proportionally reduced operating cost.
*   **Unmet Demand is Unacceptable:** If the total capacity of all factories is less than the total demand, or if due to transportation restrictions it's impossible to fulfill all demand, your solution must return `None`.

**Input:**

*   `factories`: A list of dictionaries, each representing a factory.
*   `demand_centers`: A list of dictionaries, each representing a demand center.
*   `transportation_costs`: A dictionary representing the transportation costs between factories and demand centers.

**Output:**

If a feasible solution exists, return a dictionary representing the optimal supply chain network. The dictionary should have the following structure:

```python
{
    "factories": {
        "factory_id_1": {
            "operational": True/False, # Boolean: whether the factory is operating
            "shipments": {
                "demand_center_id_1": quantity_1, # Integer: amount shipped to demand center 1
                "demand_center_id_2": quantity_2, # Integer: amount shipped to demand center 2
                ...
            }
        },
        "factory_id_2": {
            "operational": True/False,
            "shipments": {
                "demand_center_id_1": quantity_1,
                "demand_center_id_2": quantity_2,
                ...
            }
        },
        ...
    }
}
```

If no feasible solution exists (unmet demand is unacceptable), return `None`.

**Example:**

(Simplified Example - actual test cases will be significantly more complex)

```python
factories = [
    {"factory_id": "F1", "capacity": 100, "operating_cost": 500},
    {"factory_id": "F2", "capacity": 50, "operating_cost": 300},
]
demand_centers = [
    {"demand_center_id": "D1", "demand": 70},
    {"demand_center_id": "D2", "demand": 80},
]
transportation_costs = {
    ("F1", "D1"): 5,
    ("F1", "D2"): 7,
    ("F2", "D1"): 8,
    ("F2", "D2"): 4,
}

# A possible (but not necessarily optimal) solution:
# {
#     "factories": {
#         "F1": {
#             "operational": True,
#             "shipments": {
#                 "D1": 70,
#                 "D2": 30,
#             }
#         },
#         "F2": {
#             "operational": True,
#             "shipments": {
#                 "D2": 50
#                 "D1": 0
#             }
#         }
#     }
# }
```

**Grading:**

Your solution will be evaluated based on:

*   **Correctness:** Does your solution satisfy all constraints and produce the optimal (minimum cost) supply chain network?
*   **Efficiency:** Can your solution handle large inputs (up to 100 factories and 100 demand centers) within a reasonable time limit?
*   **Code Quality:** Is your code well-structured, readable, and maintainable?
