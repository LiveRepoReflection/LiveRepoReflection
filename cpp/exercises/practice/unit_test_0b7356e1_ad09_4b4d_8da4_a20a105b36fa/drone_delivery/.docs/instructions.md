## Project Name

`Autonomous Drone Delivery Optimization`

## Question Description

You are tasked with designing an efficient delivery schedule for a fleet of autonomous drones operating in a densely populated urban environment. The drones need to deliver packages from a central depot to various delivery locations scattered throughout the city.

The city is represented as a weighted graph where nodes represent locations (depot, delivery points, and intermediate intersections) and edges represent streets connecting these locations. Each edge has a weight representing the travel time (in minutes) between the connected locations.

You are given:

1.  **A graph representation of the city:**  This will be provided as an adjacency list where each node is associated with a list of its neighbors and the corresponding travel time to each neighbor. Node `0` represents the depot.

2.  **A list of delivery requests:** Each request specifies:
    *   A unique delivery ID.
    *   The destination node (location in the city).
    *   A package weight (in kilograms).
    *   A strict delivery deadline (in minutes from the start of the delivery schedule).

3.  **Drone specifications:**
    *   Each drone has a maximum carrying capacity (in kilograms).
    *   Each drone has a limited battery life, represented as a maximum flight time (in minutes). Travel time back to the depot to recharge must be included in the battery life constraint.
    *   The depot has unlimited drones available.
    *   Drones can only carry one package at a time.
    *   Drones return to the depot after each delivery to pick up another package and recharge.

4.  **Objective:**

    Your task is to create a delivery schedule that maximizes the number of on-time deliveries. A delivery is considered on-time if the drone arrives at the destination node before or exactly at the delivery deadline.

    **Constraints:**

    *   The total weight of packages carried by a drone at any given time cannot exceed its maximum carrying capacity.
    *   The total round-trip flight time for each delivery (depot -> destination -> depot) cannot exceed the drone's maximum flight time.
    *   Each delivery request can be fulfilled by at most one drone.
    *   The drones operate sequentially; a drone cannot start a new delivery until it has returned to the depot from its previous delivery.
    *   The travel time between any two locations is deterministic and known in advance.

**Input Format:**

*   `num_nodes`: The number of nodes in the city graph (integer).
*   `adjacency_list`: A vector of vectors representing the adjacency list of the city graph. `adjacency_list[i]` contains a list of pairs `(neighbor, travel_time)` for node `i`.
*   `delivery_requests`: A vector of vectors representing the delivery requests. Each inner vector represents a single delivery request and contains: `(delivery_id, destination_node, package_weight, delivery_deadline)`.
*   `drone_capacity`: The maximum carrying capacity of each drone (integer).
*   `drone_flight_time`: The maximum flight time of each drone (integer).

**Output Format:**

Return a set (or vector) of delivery IDs representing the deliveries that can be completed on time. The order of delivery IDs in the output does not matter.

**Scoring:**

The solution will be scored based on the number of on-time deliveries achieved.  A higher number of on-time deliveries will result in a higher score. Solutions will also be evaluated for their efficiency (runtime) and adherence to the constraints.  Test cases will include scenarios with varying city sizes, delivery request densities, drone capacities, and delivery deadlines.

**Optimization Requirements:**

The solution should be optimized for performance to handle large-scale city graphs and a high volume of delivery requests. Consider efficient pathfinding algorithms and scheduling strategies.  Solutions exceeding a predefined time limit will be terminated.
