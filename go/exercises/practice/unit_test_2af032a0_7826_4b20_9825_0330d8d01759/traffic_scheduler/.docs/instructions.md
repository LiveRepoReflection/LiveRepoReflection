## Question: Optimal Traffic Light Scheduling

**Description:**

You are tasked with designing an intelligent traffic light scheduling system for a complex road network. The network consists of `N` intersections and `M` bidirectional roads connecting them. Each intersection has a traffic light that can be in one of `K` states. Each state represents a specific configuration of green lights allowing traffic flow in certain directions. Switching between states takes a fixed amount of time `T` (transition cost).

Given a traffic demand matrix `D` where `D[i][j]` represents the number of vehicles wanting to travel from intersection `i` to intersection `j`, your goal is to find an optimal sequence of traffic light states for each intersection over a fixed time horizon to minimize the overall travel time of all vehicles. Assume vehicles can only move when the lights allow.

**Constraints:**

1.  **Network Representation:** The road network is represented as a graph. `N` (number of intersections) can be up to 100. `M` (number of roads) can be up to 500.  You will be given an adjacency list representing the graph.
2.  **Traffic Light States:** Each traffic light can have up to `K` = 5 distinct states. You will be given a function that, given an intersection and a state, returns the set of roads that have a green light in that state.
3.  **Time Horizon:** The scheduling must be optimized for a time horizon of `H` time units, where `H` can be up to 30.
4.  **Transition Cost:** Switching between traffic light states at an intersection incurs a fixed time penalty `T` = 1 time unit.  This transition time must be factored into the total travel time.
5.  **Traffic Demand:** `D[i][j]` is an integer representing the number of vehicles traveling from `i` to `j`, and its value can be up to 100.
6.  **Vehicle Movement:** In each time unit, a vehicle can move from one intersection to an adjacent intersection if the traffic light state at the origin intersection allows movement along that road.  If the light is red, the vehicle must wait at the intersection. Assume that all vehicles start at their origin at the start of the time horizon.
7.  **Optimization Goal:** Minimize the *total* travel time of *all* vehicles from their origin to their destination.  Vehicles that do not reach their destination within the time horizon `H` are considered to have traveled for the full `H` time units.
8.  **Realistic Assumptions:** Assume that the vehicles are infinitesimally small, so one road can hold any number of vehicles. Also, vehicles will always take shortest path to reach to destination, if multiple shortest paths are available, randomly choose one.

**Input:**

*   `N`: Number of intersections (indexed from 0 to N-1).
*   `M`: Number of roads.
*   `roads`: A 2D array representing the roads, where each row is `[intersection1, intersection2]`.
*   `K`: Number of traffic light states.
*   `allowedRoads(intersection, state)`: A function that returns a set of roads (represented as tuples `(intersection1, intersection2)`) that have a green light at a given intersection in a specific state. The returned road has to be one of the roads from `roads`. The intersection is the origin intersection.
*   `D`: The traffic demand matrix (N x N).
*   `H`: Time horizon.
*   `T`: Transition cost (fixed at 1).

**Output:**

A 2D array representing the optimal traffic light schedule. The dimensions are `N x H`, where `schedule[i][t]` represents the state of the traffic light at intersection `i` at time `t`.

**Scoring:**

The solution will be evaluated based on the total travel time of all vehicles. Lower total travel time scores higher. Partial credit will be awarded for solutions that improve upon a naive baseline. Solutions will be tested on a variety of road networks and traffic demand patterns.

**Example:**

Imagine a simple network with 2 intersections and 1 road between them. Each intersection has two states. State 0 allows traffic from 0 to 1, and state 1 allows traffic from 1 to 0.  The traffic demand is high in both directions. A good schedule would likely alternate states at both intersections to allow traffic to flow in both directions.

**Challenge:**

This problem requires a combination of graph algorithms (shortest path), dynamic programming (to optimize the schedule), and careful consideration of edge cases and constraints. Efficiently exploring the vast state space of possible schedules is crucial. Consider the time complexity, since the problem size can be relatively large.

Good luck!
