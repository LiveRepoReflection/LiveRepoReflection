## Question: Optimal Traffic Light Control

**Description:**

You are tasked with designing an intelligent traffic light control system for a complex road network. This network consists of `N` intersections and `M` bidirectional roads connecting them. Each road `(u, v)` has a specific travel time `t(u, v)` representing the time it takes to traverse it. Each intersection has a set of traffic lights.

The goal is to minimize the average travel time for all vehicles in the network. You are provided with a simulation of vehicle routes, represented as a list of `K` trips. Each trip `i` consists of a starting intersection `start_i` and a destination intersection `end_i`. Vehicles always take the shortest path from their start to their end.

Traffic lights at each intersection can be in one of two states: "Green" or "Red". When a vehicle arrives at an intersection with a red light, it must wait for the light to turn green. You can control the timing of the traffic lights at each intersection.  The light cycle at each intersection `i` consists of a "Green" duration `green_i` and a "Red" duration `red_i`.  Assume the light cycle starts at time 0 with the Green phase.

**Constraints:**

*   `1 <= N <= 100` (Number of intersections)
*   `1 <= M <= N * (N - 1) / 2` (Number of roads)
*   `1 <= K <= 1000` (Number of trips)
*   `1 <= t(u, v) <= 100` (Travel time for each road)
*   `1 <= green_i <= 100` (Minimum possible green duration)
*   `1 <= red_i <= 100` (Minimum possible red duration)
*   `2 <= green_i + red_i <= 200` (Total cycle length for each intersection)
*   All intersections are reachable from all other intersections.
*   Intersections are numbered from 0 to `N-1`.

**Input:**

Your function will receive the following inputs:

1.  `N` (Integer): The number of intersections.
2.  `M` (Integer): The number of roads.
3.  `roads` (\[]\[]int): A 2D array representing the roads. Each road is defined as `[u, v, t]`, where `u` and `v` are the connected intersections, and `t` is the travel time.
4.  `K` (Integer): The number of trips.
5.  `trips` (\[]\[]int): A 2D array representing the trips. Each trip is defined as `[start, end]`, where `start` and `end` are the starting and ending intersections.

**Output:**

Your function must return a 1D array `schedule` of length `N`, representing the optimal traffic light schedule. `schedule[i]` contains an integer representing the length of the Green light at intersection `i`. The Red light will last `cycle_length - schedule[i]`. The cycle length is same for all traffic lights and is pre-calculated as the value "cycle_length".

**Scoring:**

The score will be based on the average travel time across all `K` trips. The lower the average travel time, the higher the score. Your solution will be compared against other submissions, and the top-performing solutions will receive the highest scores.

**Example:**

Let's say cycle length is 50.
If `schedule[i]` is 20, then intersection `i` has a Green light for 20 time units and a Red light for 30 time units.

**Challenge:**

This problem requires you to design an efficient algorithm that balances exploration and exploitation to find a near-optimal solution. Due to the complexity of the search space, a brute-force approach will not be feasible. Consider using techniques like:

*   Graph algorithms (Dijkstra, A\*) for shortest path calculation.
*   Heuristics to guide the search for optimal traffic light timings.
*   Optimization algorithms (Simulated Annealing, Genetic Algorithms) to explore the solution space.
*   Dynamic Programming to pre-calculate shortest paths.

Good luck!
