## Question: Optimal Traffic Light Scheduling

**Description:**

You are tasked with designing an optimal traffic light scheduling system for a complex road network. The network consists of `N` intersections and `M` bidirectional roads connecting them. Each road has a specific travel time `T_ij` (in seconds) between intersections `i` and `j`. Each intersection `i` has a traffic light that cycles through `K_i` phases. Each phase `p` at intersection `i` lasts for `D_ip` seconds and allows specific incoming roads to pass through while blocking others.

Your goal is to minimize the average travel time of vehicles traveling between a given set of origin-destination (O-D) pairs in the road network. You are given a set of `Q` O-D pairs, each with a specific traffic volume `V_q`. You can assume that vehicles always choose the shortest path based on the current traffic light timings.

**Input:**

*   `N`: The number of intersections (1 <= N <= 50).
*   `M`: The number of bidirectional roads (1 <= M <= 200).
*   A list of `M` tuples `(i, j, T_ij)` representing the roads, where `i` and `j` are the connected intersections (1 <= i, j <= N) and `T_ij` is the travel time (1 <= T_ij <= 100). Note that road `(i, j)` is the same as road `(j, i)`.
*   For each intersection `i` from 1 to `N`:
    *   `K_i`: The number of phases for intersection `i`'s traffic light (1 <= K_i <= 10).
    *   A list of `K_i` durations `D_i1, D_i2, ..., D_iKi` representing the duration of each phase in seconds (1 <= D_ip <= 60). The sum of durations must be greater than 0.
    *   For each phase `p` from 1 to `K_i`:
        *   A set of roads allowed to pass through the intersection `i` during phase `p`. This will be represented as a list of tuples `(u, i)` where traffic can flow from `u` to `i`.
*   `Q`: The number of O-D pairs (1 <= Q <= 100).
*   A list of `Q` tuples `(origin, destination, V_q)` representing the O-D pairs, where `origin` and `destination` are the intersection numbers (1 <= origin, destination <= N, origin != destination) and `V_q` is the traffic volume for that pair (1 <= V_q <= 100).

**Output:**

The minimum possible average travel time (in seconds) for all vehicles across all O-D pairs. The answer must be accurate to six decimal places.

**Constraints:**

*   Finding the absolute optimal solution is computationally infeasible within a reasonable time limit. You are expected to find a near-optimal solution using appropriate optimization techniques.
*   You are allowed to pre-compute and store data structures that might speed up the shortest path calculations.
*   The total simulation time for evaluating a scheduling configuration is limited to 1000 seconds.
*   Assume each intersection has a signal which is independent of the other signals.
*   Assume the travel time of each road is constant. It does not vary as a function of traffic.
*   Assume the car will find the optimal path given the current traffic light.
*   Assume cars do not interact and the travel time is the sum of the travel time on the road and the waiting time at the intersection.
*   If there is no path between origin and destination, ignore this route.

**Scoring:**

Your solution will be evaluated based on the average travel time across a set of test cases. The lower the average travel time, the higher the score. Solutions that fail to produce a valid output or exceed the time limit will receive a score of 0.

**Challenge:**

This problem requires you to combine graph algorithms (shortest path), simulation, and optimization techniques. You need to consider:

*   **Efficient Shortest Path Calculation:**  Repeatedly calculating shortest paths considering traffic light timings can be time-consuming. Implement an efficient shortest path algorithm (e.g., Dijkstra's or A\*) and consider caching or pre-computing relevant information.
*   **Traffic Light Simulation:**  Simulate the traffic light cycles accurately to determine waiting times at intersections.
*   **Optimization Strategy:**  Explore different optimization strategies to find a near-optimal traffic light schedule.  Possible approaches include:
    *   **Greedy Algorithms:** Iteratively improve the schedule by making small changes.
    *   **Simulated Annealing:**  Explore the solution space while avoiding local optima.
    *   **Genetic Algorithms:**  Evolve a population of schedules towards better solutions.

This problem requires careful algorithm design and efficient implementation to achieve a good score. Good luck!
