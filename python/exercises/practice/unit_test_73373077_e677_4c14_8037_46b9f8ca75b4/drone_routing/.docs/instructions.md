## Project Name

```
Optimized Route Planning for Autonomous Delivery Drones with Time Windows and Charging Constraints
```

## Question Description

You are tasked with developing an efficient route planning algorithm for a fleet of autonomous delivery drones operating in a dense urban environment. Each drone has a limited battery capacity and must return to a designated charging station when its battery level falls below a critical threshold.  The drones need to fulfill a set of delivery requests, each with a specific location and a **time window** within which the delivery must be completed. Furthermore, drones can only carry a limited number of packages at a time before needing to return to the depot to reload.

**Specifically, you are given the following:**

*   **`num_drones`:** The number of drones in the fleet.
*   **`depot_location`:** A tuple `(x, y)` representing the coordinates of the depot (charging station).
*   **`drone_battery_capacity`:** An integer representing the maximum battery capacity of each drone (in abstract units).
*   **`drone_package_capacity`:** An integer representing the maximum number of packages each drone can carry.
*   **`battery_consumption_rate`:** An integer representing the battery units consumed per unit distance traveled. Assume Euclidean distance.
*   **`delivery_requests`:** A list of tuples, where each tuple represents a delivery request in the format `(request_id, x, y, start_time, end_time, package_weight)`.

    *   `request_id`: A unique identifier for the request.
    *   `(x, y)`: The coordinates of the delivery location.
    *   `start_time`: The earliest time the delivery can be made.
    *   `end_time`: The latest time the delivery can be made.
    *   `package_weight`: The weight of the package to be delivered. Drones have unlimited weight capacity (only package count matters)
*   **`time_penalty_per_unit`:** An integer representing the cost of time spent travelling.
*   **`missed_delivery_penalty`:** An integer representing the cost of a missed delivery.
*   **`charging_time_per_unit`:** An integer representing the time units required to charge one battery unit.
*   **`max_simulation_time`**: An integer representing the maximum time units the simulation can run for. It is allowed to not service all requests within this time.

**Your goal is to devise a routing plan for the drones that minimizes the total cost, defined as:**

`Total Cost = (Time Spent Travelling * time_penalty_per_unit) + (Number of Missed Deliveries * missed_delivery_penalty)`

**Constraints:**

1.  **Time Windows:** Each delivery must be completed within its specified `start_time` and `end_time`. Drones can wait at a delivery location if they arrive before the `start_time`.
2.  **Battery Capacity:** Drones must have sufficient battery to reach each delivery location and return to the depot for recharging when necessary.
3.  **Package Capacity:** Drones must return to the depot to reload when their package count reaches `drone_package_capacity`.
4.  **Feasibility:** Routes must be feasible. A route is infeasible if any delivery's time window is missed, if a drone runs out of battery before reaching its destination, or if any other constraint is violated.
5.  **Optimization:** The solution must be optimized to minimize the total cost.  A naive solution will likely time out on larger test cases.
6.  **Real-time Planning:** Each simulation runs for only a short duration. Optimise for fast planning speeds.
7.  **Complete/Incomplete Solutions:** It is valid to not service all requests within the `max_simulation_time`.
8. **Charging:** Assume drones can fully recharge in the depot. Assume multiple drones can charge at the depot simultaneously. Drones can only charge at the depot.

**Input:**

The input will be provided as described above.

**Output:**

Your function should return a list of lists, where each inner list represents the route for a single drone. Each route should be a list of tuples, where each tuple represents a location the drone visits, in the order it visits them. The format of the tuple should be `(location_type, request_id/depot_id, time_of_arrival)`.

*   `location_type`: A string, either `"delivery"` or `"depot"`.
*   `request_id/depot_id`: The `request_id` of the delivery request if `location_type` is `"delivery"`, or a unique depot_id if `location_type` is `"depot"`. Since all drones use the same depot, let depot_id be simply `0`.
*   `time_of_arrival`: An integer representing the time the drone arrives at the location.

If a drone misses a delivery, it should NOT appear in the route. The missed delivery will be accounted for in the missed delivery penalty.

**Example:**

```python
num_drones = 2
depot_location = (0, 0)
drone_battery_capacity = 100
drone_package_capacity = 2
battery_consumption_rate = 1
delivery_requests = [
    (1, 10, 10, 10, 20, 1),
    (2, 5, 5, 5, 15, 1),
    (3, -5, -5, 20, 30, 1)
]
time_penalty_per_unit = 1
missed_delivery_penalty = 1000
charging_time_per_unit = 1
max_simulation_time = 100

# Example (potentially suboptimal) output:
# [
#     [("depot", 0, 0), ("delivery", 2, 7), ("depot", 0, 14)],
#     [("depot", 0, 0), ("delivery", 1, 14)]
# ]

```

**Grading:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** Does the solution produce feasible routes that satisfy all the constraints?
*   **Optimization:** How close is the total cost of the solution to the optimal cost?
*   **Efficiency:** How quickly does the solution generate the routing plan? Solutions that exceed the time limit will not be graded.
*   **Scalability:** How well does the solution perform with a large number of drones, delivery requests, and complex constraints?
