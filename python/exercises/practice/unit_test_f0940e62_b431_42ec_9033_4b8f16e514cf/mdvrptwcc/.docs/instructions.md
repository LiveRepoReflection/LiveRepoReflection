## Problem Title: Optimal Multi-Depot Vehicle Routing with Time Windows and Capacity Constraints (MDVRPTWCC)

**Problem Description:**

You are tasked with designing an efficient delivery system for a large e-commerce company operating in a sprawling metropolitan area. The company has multiple distribution centers (depots) and needs to serve a large number of customer orders. Each customer order has a specific location, a required delivery quantity, and a time window within which the delivery must be made. Each depot has a limited number of vehicles and each vehicle has a limited capacity.

The goal is to design a set of routes for the vehicles originating from these depots to serve all customers while minimizing the total travel cost (distance).

**Constraints:**

1.  **All customers must be served:** Each customer order must be delivered exactly once by a single vehicle.
2.  **Vehicle capacity:** The total quantity of goods delivered by a vehicle on a single route must not exceed the vehicle's capacity.
3.  **Time windows:** Deliveries to customers must be made within their specified time windows. A vehicle arriving before the start of the time window must wait.
4.  **Depot assignment:** Each vehicle must start and end its route at the same depot.
5.  **Number of Vehicles:** The total number of vehicles used from any depot should not exceed the number of available vehicles in that depot.
6.  **Homogenous Fleet**: All vehicles have the same capacity and travel speed.
7.  **Travel Time Calculation**: Travel time between any two locations (depot or customer) is directly proportional to the Euclidean distance between them.

**Input:**

The input will be provided in the following format:

*   **Depots:** A list of depots, where each depot is represented by:
    *   Depot ID (integer)
    *   X and Y coordinates (integers)
    *   Number of available vehicles (integer)
*   **Customers:** A list of customers, where each customer is represented by:
    *   Customer ID (integer)
    *   X and Y coordinates (integers)
    *   Demand (integer)
    *   Start of time window (integer)
    *   End of time window (integer)
*   **Vehicle:**
    *   Vehicle Capacity (integer)
    *   Vehicle Speed (constant, e.g. 1 unit distance per unit time).

**Output:**

The output should be a list of routes, where each route is represented by:

*   Depot ID (integer) - The depot from which the route originates.
*   A list of customer IDs (integers) representing the order in which the customers are visited on the route.

The output should minimize the total travel distance of all routes.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** All constraints must be satisfied. Failure to satisfy any constraint will result in a zero score.
2.  **Total Travel Distance:** The primary objective is to minimize the total travel distance of all routes.  Your solution's score will be relative to the best solution obtained by the judge.
3.  **Time Limit:** Your solution must complete within a specified time limit (e.g., 10 minutes).
4.  **Memory Limit:** Your solution must operate within a specified memory limit.

**Optimization Requirements:**

This problem is NP-hard, so finding the absolute optimal solution is likely infeasible for large instances. You are expected to develop an efficient heuristic or metaheuristic algorithm that can find a near-optimal solution within the given time and memory constraints. Consider techniques such as:

*   Simulated Annealing
*   Genetic Algorithms
*   Tabu Search
*   Large Neighborhood Search
*   Adaptive Large Neighborhood Search

**Scoring:**

Your score will be calculated as follows:

*   If your solution violates any constraint, your score is 0.
*   Otherwise, your score will be proportional to the difference between your total travel distance and the best-known total travel distance, normalized by the best-known total travel distance. A solution closer to the best-known solution will receive a higher score.

**Hints and Considerations:**

*   Start with a feasible solution.  A simple greedy approach can be used to generate an initial feasible solution.
*   Consider using efficient data structures for representing routes and neighborhoods.
*   Experiment with different neighborhood structures and search strategies.
*   Pay attention to the time limit and memory limit. Profile your code and optimize for performance.
*   Think about how to efficiently evaluate the feasibility of moves during the search process.  Incremental evaluation can significantly improve performance.
*   Consider parallelizing your algorithm to take advantage of multi-core processors.
*   The quality of the solution will be judged based on how well it minimizes the objective function (total distance traveled) within the allowed time and memory constraints.
