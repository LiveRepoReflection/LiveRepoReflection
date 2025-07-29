## Project Name

`Multi-Source Shortest Path on Weighted Graph with Time Windows`

## Question Description

You are tasked with designing a system to find the optimal route for delivery vehicles operating from multiple distribution centers, considering time windows for deliveries and capacity constraints.

**Problem Statement:**

Given a weighted directed graph representing a road network, a set of distribution centers (sources), a set of delivery locations (destinations), and a fleet of delivery vehicles, determine the shortest (least cost) path for each vehicle to deliver goods to a subset of the delivery locations, satisfying the following constraints:

*   **Multiple Sources:** Vehicles can start their routes from any of the available distribution centers.
*   **Weighted Graph:** The graph edges have associated costs (e.g., travel time, fuel consumption).
*   **Time Windows:** Each delivery location has a specific time window during which the delivery must be made. Arriving before the time window incurs a waiting cost, and arriving after the time window is not allowed.
*   **Vehicle Capacity:** Each vehicle has a maximum capacity of goods it can carry. Each delivery location has a demand.
*   **Optimization Goal:** Minimize the total cost, which includes travel costs and waiting costs.
*   **Heterogeneous Fleet:** You have a limited number of vehicles at each distribution center with varying capacities and costs per unit distance.

**Input:**

*   **Graph:** A weighted directed graph represented as an adjacency list or matrix. Each edge includes a source node, a destination node, and a weight (cost).
*   **Distribution Centers:** A list of nodes representing the distribution centers, along with the number of available vehicles, their capacities and cost per unit distance.
*   **Delivery Locations:** A list of nodes representing the delivery locations. Each location includes a demand, a time window (start and end time), and waiting cost per unit time.
*   **Vehicle Fleet:** Characteristics of vehicles available at each distribution center, including capacity and cost per unit distance.

**Output:**

*   A list of routes for each vehicle, specifying the sequence of delivery locations, the start time at each location, and the total cost of each route.  If no feasible solution exists, return an appropriate error message.
*   Each route must start from a distribution center, visit a subset of delivery locations within their respective time windows without exceeding the vehicle's capacity, and minimize the total cost.

**Constraints and Edge Cases:**

*   The graph can be large (e.g., thousands of nodes and edges).
*   The number of distribution centers and delivery locations can be significant (e.g., hundreds).
*   Time windows can be narrow, making it challenging to find feasible routes.
*   Vehicle capacities can be restrictive, requiring careful allocation of deliveries.
*   Some delivery locations might be unreachable from certain distribution centers within the given time constraints.
*   It might not always be possible to serve all delivery locations with the available vehicles and constraints.
*   The algorithm should be efficient enough to produce results in a reasonable time (e.g., within a few minutes).
*   Consider the real-world scenario where vehicles can only make one trip. Once they unload, they cannot reload.

**Example:**

(Simplified for illustration)

*   **Graph:** A simple graph with 5 nodes (A, B, C, D, E) and edges with weights.
*   **Distribution Centers:** A (2 vehicles), B (1 vehicle). Each vehicle has capacity 10. Cost per unit distance is 1 for all vehicles.
*   **Delivery Locations:** C (demand 5, time window 10-15, waiting cost 0.5), D (demand 5, time window 12-18, waiting cost 0.5), E (demand 3, time window 14-16, waiting cost 0.5).

**Expected Output:**

(A possible solution)

*   Vehicle 1 (from A): Route: A -> C -> D, Start times: A(0), C(10), D(15), Total Cost: (Travel Cost) + (Waiting Cost)
*   Vehicle 2 (from B): Route: B -> E, Start times: B(0), E(14), Total Cost: (Travel Cost)

**Judging Criteria:**

*   Correctness: The routes must be feasible and satisfy all constraints.
*   Optimality: The solution should minimize the total cost.
*   Efficiency: The algorithm should scale well to large problem instances.
*   Handling of edge cases and constraints.

This problem combines graph algorithms, optimization techniques (possibly dynamic programming or heuristics), and careful consideration of real-world constraints. It demands a sophisticated solution that balances accuracy and efficiency. Good luck!
