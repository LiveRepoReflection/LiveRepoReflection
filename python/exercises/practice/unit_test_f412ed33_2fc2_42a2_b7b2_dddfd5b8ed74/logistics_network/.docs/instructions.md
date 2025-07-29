## Project Name

`Optimal Logistics Network Design`

## Question Description

A major logistics company, "OmniLogistics," is seeking to optimize its delivery network across a large country. They have a set of distribution centers (DCs) and customer locations. The goal is to design the most cost-effective network that guarantees delivery within a given service level agreement (SLA).

**Problem:**

Given a set of distribution centers (DCs), customer locations, and a fleet of trucks with varying capacities and costs, design a logistics network that minimizes the total cost while ensuring that all customers receive their required deliveries within the specified SLA.

**Input:**

*   `DCs`: A list of dictionaries, each representing a distribution center. Each dictionary has the following keys:
    *   `id`: Unique identifier for the DC (integer).
    *   `location`: Tuple representing the (x, y) coordinates of the DC (integers).
    *   `capacity`: Maximum amount of goods that can be handled by the DC per day (integer).
    *   `fixed_cost`: Daily fixed operational cost of the DC (integer).

*   `Customers`: A list of dictionaries, each representing a customer location. Each dictionary has the following keys:
    *   `id`: Unique identifier for the customer (integer).
    *   `location`: Tuple representing the (x, y) coordinates of the customer (integers).
    *   `demand`: Daily demand of the customer (integer).

*   `Trucks`: A list of dictionaries, each representing a type of truck. Each dictionary has the following keys:
    *   `id`: Unique identifier for the truck type (integer).
    *   `capacity`: Maximum load capacity of the truck (integer).
    *   `cost_per_km`: Cost per kilometer for operating the truck (float).

*   `SLA`: The maximum allowed delivery time in hours from a DC to any customer. Delivery time is calculated based on distance (Euclidean distance) and average truck speed (60 km/h). (float).

*   `Max_trucks_per_DC`: The maximum number of each truck type available at any DC. (integer)

**Output:**

A dictionary representing the optimal logistics network design. The dictionary should have the following keys:

*   `total_cost`: The total cost of the designed network (integer). This includes the fixed costs of the DCs and the transportation costs.
*   `routes`: A list of dictionaries, each representing a route. Each dictionary has the following keys:
    *   `DC_id`: The ID of the distribution center serving the route (integer).
    *   `truck_id`: The ID of the truck type used for the route (integer).
    *   `customers`: A list of customer IDs served by this route (list of integers).

**Constraints:**

*   Every customer's demand must be fully met.
*   The capacity of each DC must not be exceeded.
*   The delivery time from a DC to any customer on a route must be within the specified SLA.
*   Trucks can only serve customers from a single DC in a single route.
*   Minimize the `total_cost`.
*   Each DC has a limited number of trucks of each type available.

**Optimization Requirements:**

*   The solution should be optimized for minimal `total_cost`. Efficient algorithms and data structures are crucial for handling potentially large input datasets.

**Edge Cases:**

*   Consider cases where the total demand exceeds the combined capacity of all DCs. In this case, return -1 for `total_cost` and an empty list for `routes`.
*   Consider cases where some customers are impossible to serve within the SLA from any DC. In this case, return -1 for `total_cost` and an empty list for `routes`.
*   Consider multiple DCs being able to serve a customer and pick the one that leads to an overall cost-optimized solution.

**Scoring:**

The solution will be scored based on its correctness and the `total_cost` of the designed network. Solutions with lower `total_cost` will receive higher scores. Solutions that do not meet all the constraints will be considered incorrect and receive a score of 0.

This problem requires a combination of graph theory, optimization techniques (possibly linear programming or heuristics), and careful handling of constraints and edge cases. Efficient implementations are essential for handling larger datasets within a reasonable time limit.
