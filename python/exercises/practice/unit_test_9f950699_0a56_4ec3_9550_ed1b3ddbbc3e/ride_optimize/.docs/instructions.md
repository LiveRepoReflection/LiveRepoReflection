## Problem: Real-Time Ride Sharing Optimization

**Description:**

Imagine you're building the backend for a ride-sharing application like Uber or Lyft. Your service operates in a city represented as a weighted graph, where nodes are intersections and edges are road segments with associated travel times (weights).

At any given moment, you have a list of `n` active drivers and `m` waiting passengers. Each driver has a current location (intersection) and a maximum capacity (number of passengers they can carry). Each passenger has a pickup location, a destination location, and a maximum acceptable waiting time.

Your task is to design an efficient algorithm that assigns drivers to passengers in real-time to minimize the *average* passenger waiting time, subject to the following constraints:

*   **Capacity Constraint:** A driver cannot exceed their maximum capacity.
*   **Time Constraint:** A passenger's actual waiting time (time until pickup) must be less than or equal to their maximum acceptable waiting time.
*   **Feasibility Constraint:**  There must exist a path from driver location to passenger location and, subsequently, from passenger location to destination location on the graph.
*   **Real-time Constraint:** You have a strict time limit to compute the assignment (e.g., 1 second). The graph can be quite large (thousands of nodes and edges), and the number of drivers and passengers can also be significant (hundreds).

The algorithm must output a list of driver-passenger assignments. If a passenger cannot be assigned within their waiting time limit, they should be left unassigned. The goal is to maximize the number of assigned passengers while minimizing the average waiting time of the assigned passengers.

**Input:**

*   `graph`: A weighted graph represented as an adjacency list or matrix. The weight of an edge represents the travel time between two intersections.
*   `drivers`: A list of tuples, where each tuple represents a driver: `(driver_id, location, capacity)`.
*   `passengers`: A list of tuples, where each tuple represents a passenger: `(passenger_id, pickup_location, destination_location, max_waiting_time)`.

**Output:**

*   A list of tuples, where each tuple represents a driver-passenger assignment: `(driver_id, passenger_id)`.

**Constraints:**

*   The graph can be large (up to 1000 nodes and 5000 edges).
*   The number of drivers and passengers can be significant (up to 200 drivers and 200 passengers).
*   Travel times are positive integers.
*   Capacities and maximum waiting times are positive integers.
*   The algorithm must run within a strict time limit (e.g., 1 second).
*   Assume graph is undirected.

**Optimization Requirements:**

*   Minimize the average waiting time of assigned passengers.
*   Maximize the number of passengers assigned.

**Grading Criteria:**

The solution will be graded based on a combination of:

*   **Correctness:** The solution must produce valid assignments that satisfy all constraints.
*   **Efficiency:** The solution must run within the time limit.
*   **Optimization:** The solution's ability to minimize average waiting time and maximize the number of assigned passengers will be evaluated. Solutions will be compared against each other on a set of hidden test cases.

**Considerations:**

*   Think about efficient shortest path algorithms (e.g., Dijkstra, A*) for finding travel times.
*   Consider using appropriate data structures to store and retrieve information quickly.
*   Think about different assignment strategies and their trade-offs (e.g., greedy, optimal).
*   Consider heuristics and approximations to find good solutions within the time limit.  A perfect optimal solution might not be achievable within the time constraint.
*   Think about how to handle edge cases and invalid inputs gracefully.
*   Consider the scalability of your solution as the number of drivers and passengers increases.
