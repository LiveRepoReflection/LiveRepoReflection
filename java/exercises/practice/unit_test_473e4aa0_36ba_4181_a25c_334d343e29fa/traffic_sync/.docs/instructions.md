## Question: Optimal Traffic Light Synchronization

### Project Name

`trafficsync`

### Question Description

You are tasked with optimizing traffic flow in a city grid. The city can be represented as a graph where intersections are nodes and roads connecting them are edges. Each intersection has a traffic light. Your goal is to find the *optimal* synchronization schedule for these traffic lights to minimize the average travel time between *all* pairs of intersections in the city.

**Specifics:**

*   **City Representation:** The city is represented as a directed, weighted graph. Nodes are numbered from 0 to N-1, where N is the number of intersections. Edges represent roads, with weights representing the travel time along that road. You are given an adjacency list `adjList` representing the graph. `adjList[i]` contains a list of `Pair<Integer, Integer>` objects, where the first integer is the destination intersection and the second integer is the travel time (weight) to that intersection from intersection `i`.

*   **Traffic Light Cycles:** Each traffic light has a fixed cycle time `T`. At each intersection `i`, you can set a phase offset `phase[i]` (an integer between 0 and T-1, inclusive). The traffic light at intersection `i` is "green" for a duration `G` and "red" for a duration `R`, where `G + R = T`. The start of the green phase for traffic light `i` occurs at time `phase[i]`.

*   **Travel Time Calculation:** When a vehicle arrives at an intersection, it may have to wait if the traffic light is red. If the vehicle arrives at time `t` at intersection `i`, it will have to wait until time `t'` where `t' >= t` and `(t' - phase[i]) % T < G`. The waiting time is therefore `t' - t`.  The total travel time between two intersections is the sum of the road travel times and any waiting times at intermediate traffic lights.

*   **Optimization Goal:** Your task is to find a set of `phase[i]` values (one for each intersection `i`) that minimizes the average travel time between *all* pairs of intersections in the city. Specifically, you want to minimize:

    ```
    Average Travel Time = (1 / (N * (N - 1))) * sum(travelTime(u, v))  for all u != v
    ```

    where `travelTime(u, v)` is the minimum travel time from intersection `u` to intersection `v` given the current `phase` settings. Use Dijkstra's algorithm or a similar shortest path algorithm to compute `travelTime(u,v)` given `phase`.

**Input:**

*   `N`: The number of intersections (nodes in the graph).
*   `adjList`: An adjacency list representing the city graph. `adjList[i]` is a `List<Pair<Integer, Integer>>`, where each pair represents a road from intersection `i` to another intersection, with the integer representing the destination intersection and the other integer representing the travel time along the road.
*   `T`: The cycle time for all traffic lights.
*   `G`: The duration for which each traffic light is green.

**Output:**

*   A `List<Integer>` of length `N`, where the `i`-th element represents the optimal `phase[i]` for intersection `i`.

**Constraints:**

*   2 <= N <= 50
*   1 <= T <= 20
*   1 <= G < T
*   Travel times between intersections are non-negative integers.
*   The graph may not be fully connected. If there is no path between two intersections, the travel time should be considered `Double.POSITIVE_INFINITY`. Such pairs should still be included in the average travel time calculation, with infinite travel time.

**Optimization Requirements:**

*   **Time Limit:** Your solution must complete within a reasonable time limit (e.g., 5 minutes).
*   **Phase Optimization:**  A brute-force approach of trying all possible phase combinations will likely be too slow. You will need to develop a more intelligent search or optimization strategy.

**Hint:**

Consider using a local search algorithm (e.g., hill climbing, simulated annealing) or a genetic algorithm to find a near-optimal solution. Since the search space is `T^N`, even with constraints, this is a very large search space.  Consider using heuristics to guide your search. For example, initializing the phases of adjacent intersections to be different might be a good starting point. Remember to handle cases where there's no path between intersections by assigning a very large travel time.
