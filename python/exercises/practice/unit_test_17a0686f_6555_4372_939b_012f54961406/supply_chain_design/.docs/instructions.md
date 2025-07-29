## Question: Optimal Supply Chain Network Design

### Question Description

You are tasked with designing an optimal supply chain network for a global manufacturing company. The company produces a single product and has a set of potential locations for factories and warehouses across the globe.  The goal is to determine the optimal placement of factories and warehouses, and the optimal flow of goods between them, to minimize the total cost of production, transportation, and storage, while meeting customer demand in various regions.

**Input:**

The input data is provided as follows:

*   **Factories:** A list of potential factory locations, each with:
    *   `location_id`: A unique identifier for the location (string).
    *   `production_capacity`: The maximum number of units that can be produced annually (integer).
    *   `production_cost_per_unit`: The cost to produce one unit at this factory (float).
    *   `fixed_cost`:  The annual fixed cost of operating the factory, regardless of production volume (float).

*   **Warehouses:** A list of potential warehouse locations, each with:
    *   `location_id`: A unique identifier for the location (string).
    *   `storage_capacity`: The maximum number of units that can be stored annually (integer).
    *   `storage_cost_per_unit`: The cost to store one unit at this warehouse for a year (float).
    *   `fixed_cost`: The annual fixed cost of operating the warehouse, regardless of storage volume (float).

*   **Customer Demand:** A list of customer regions, each with:
    *   `location_id`: A unique identifier for the region (string).
    *   `demand`: The annual demand for the product in this region (integer).

*   **Transportation Costs:** A matrix representing the transportation cost per unit between any two locations (factories, warehouses, and customer regions).  This is represented as a dictionary of dictionaries: `transportation_costs[location_id_1][location_id_2]` returns the cost per unit to transport goods from `location_id_1` to `location_id_2` (float). Assume the graph is fully connected.

**Output:**

Your program should output a dictionary containing the following information:

*   `selected_factories`: A list of `location_id`s of the factories that should be opened.
*   `selected_warehouses`: A list of `location_id`s of the warehouses that should be opened.
*   `flow`: A dictionary representing the optimal flow of goods. The keys are tuples `(source_location_id, destination_location_id)`, and the values are the number of units transported from the source to the destination (integer). The source and destination locations can be factories, warehouses, or customer regions.
*   `total_cost`: The total cost of the optimal supply chain network (float), including production, transportation, and storage costs, and fixed costs for operating factories and warehouses.

**Constraints:**

*   All demand must be met.
*   Production at each factory cannot exceed its `production_capacity`.
*   Storage at each warehouse cannot exceed its `storage_capacity`.
*   The objective is to minimize the `total_cost`.
*   The number of potential factory and warehouse locations can be large (up to 100 each), and the number of customer regions can also be large (up to 50).
*   Transportation costs can vary significantly between locations.
*   The solution must be computationally efficient. A brute-force approach will not be feasible for larger datasets.
*   You can assume all input values are non-negative.

**Optimization Requirements:**

*   The solution should be optimized for speed and memory usage. Solutions that take excessively long to run or consume large amounts of memory will not be accepted.
*   Consider using appropriate data structures and algorithms to achieve optimal performance.
*   Explore different optimization techniques to find the best possible solution within a reasonable timeframe.

**System Design Aspects:**

*   Consider how the solution could be scaled to handle larger datasets and more complex supply chain networks.
*   Think about how the solution could be integrated into a larger supply chain management system.
*   Error handling for edge cases (e.g., no feasible solution) should be included.  If no feasible solution exists, return a dictionary with `total_cost` set to `float('inf')` and empty lists/dictionaries for other fields.

**Algorithmic Efficiency Requirements:**

*   The algorithm should have a reasonable time complexity.  An optimal solution using Linear Programming techniques is expected. Consider the use of libraries designed for solving optimization problems.

This problem requires a deep understanding of optimization techniques, data structures, and algorithms. Good luck!
