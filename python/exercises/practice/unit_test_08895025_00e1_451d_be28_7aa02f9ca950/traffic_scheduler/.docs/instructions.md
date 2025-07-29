## Problem: Optimal Traffic Light Scheduling

### Question Description

Imagine you are tasked with optimizing the traffic flow in a city with a complex network of intersections. You are given a road network represented as a directed graph where nodes are intersections and edges are roads connecting them. Each road has a specific travel time associated with it, representing the time it takes to traverse that road under normal traffic conditions. Each intersection has a set of incoming and outgoing roads.

Your goal is to design a traffic light scheduling algorithm that minimizes the average travel time for vehicles traveling between any two intersections in the city. Each intersection has a traffic light that cycles through different phases. Each phase allows traffic to flow from a specific subset of incoming roads to a specific subset of outgoing roads. The duration of each phase can be configured.

**Input:**

*   **`N`**: The number of intersections in the city (numbered from 0 to N-1).
*   **`roads`**: A list of tuples, where each tuple `(u, v, time)` represents a directed road from intersection `u` to intersection `v` with a travel time of `time`.
*   **`phases`**: A dictionary where keys are intersection IDs (0 to N-1) and values are lists of phases for that intersection. Each phase is represented as a tuple `(incoming_roads, outgoing_roads, duration)`.
    *   `incoming_roads`: A set of intersection IDs representing the incoming roads that are open during this phase.
    *   `outgoing_roads`: A set of intersection IDs representing the outgoing roads that are open during this phase.
    *   `duration`: The duration of the phase in seconds.

**Constraints:**

*   `1 <= N <= 50`
*   The graph is strongly connected (there is a path between any two intersections).
*   Travel times are positive integers.
*   Phase durations are positive integers.
*   For each intersection, the sum of all phase durations must be a fixed cycle length `C` (10 <= C <= 60). This `C` is same for all intersections.
*   An intersection can have multiple phases.
*   There are no self-loops (no road from an intersection to itself).
*   The sum of `duration` for all phases of any intersection is same and is equal to `C`.
*   `0 <= u, v < N` for each road `(u, v, time)`.

**Output:**

Return the minimum average travel time (in seconds) between any two intersections in the city, considering the traffic light schedules. The average travel time is calculated as the sum of the shortest path lengths between all pairs of intersections, divided by the total number of pairs (N * (N - 1)). If any two intersections are unreachable, return `float('inf')`.

**Challenge:**

*   The optimal traffic light schedule is not immediately obvious. The best phase durations and sequences must be determined to minimize overall travel time.
*   The search space for possible traffic light schedules is extremely large.
*   You need to consider the waiting time at intersections caused by the traffic lights.
*   Your solution should be efficient enough to handle relatively large city networks within a reasonable time limit (e.g., a few seconds).

**Note:**

You can assume that vehicles arrive at intersections at random times. Therefore, on average, a vehicle will wait half the duration of the current phase if it arrives at an intersection when the light is red for its desired direction. If a vehicle arrives at the right time to traverse the intersection with zero wait time, then the shortest path from that intersection will be updated.

This problem requires careful consideration of graph algorithms (shortest paths), optimization techniques, and the dynamics of traffic flow. The challenge lies in finding an efficient way to explore the solution space and determine the best traffic light scheduling strategy.
