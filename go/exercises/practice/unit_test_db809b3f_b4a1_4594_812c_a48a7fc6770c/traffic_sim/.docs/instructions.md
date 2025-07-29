Okay, here's a challenging Go coding problem designed to test advanced data structures, algorithmic efficiency, and real-world problem-solving skills.

## Project Name

`TrafficSim`

## Question Description

You are tasked with building a simplified traffic simulation system for a city. The city's road network is represented as a directed graph. Nodes in the graph represent intersections, and directed edges represent road segments connecting intersections. Each road segment has a `capacity`, representing the maximum number of vehicles that can be present on that segment at any given time.

The simulation runs in discrete time steps. At each time step, vehicles attempt to move from their current intersection to a neighboring intersection along a road segment.

**Your task is to implement the `simulateTraffic` function, which takes the road network, an initial distribution of vehicles at intersections, and a number of simulation steps as input. The function should return the final distribution of vehicles at each intersection after the simulation completes.**

Here are the specifics:

*   **Road Network:** The road network is represented as a `map[string]map[string]int`, where:
    *   The outer map's keys are the names of intersections (strings).
    *   The inner map's keys are the names of neighboring intersections (strings).
    *   The inner map's values are the `capacity` of the road segment connecting the two intersections.  A capacity of 0 indicates no road segment exists.

*   **Initial Vehicle Distribution:** The initial vehicle distribution is represented as a `map[string]int`, where:
    *   The keys are the names of intersections (strings).
    *   The values are the number of vehicles initially present at that intersection.

*   **Simulation Steps:** An integer representing the number of time steps to simulate.

*   **Vehicle Movement Rules (Applied at each time step):**
    1.  **Priority to Leave:**  At each intersection, vehicles *attempt* to leave the intersection first.
    2.  **Destination Selection:** Each vehicle at an intersection *randomly* chooses a destination intersection from its available neighbors (neighbors are determined by the road network). A vehicle can only select a neighbor if a road segment exists between the current intersection and the neighbor.
    3.  **Capacity Constraint:**  Vehicles can only move to a neighboring intersection if the road segment connecting the two intersections has enough remaining capacity.  Specifically, the number of vehicles moving onto a road segment *must not exceed* the road segment's capacity. If the capacity is exceeded, then vehicles are moved onto the road segment in a random order until the road segment is full.
    4.  **Simultaneous Movement:**  Assume that all vehicles make their movement decisions and movements occur *simultaneously*. This means that you should not update the number of vehicles at an intersection until *all* movements for that time step have been determined.
    5.  **Staying Put:** If a vehicle cannot move to its chosen destination (due to capacity constraints or no available neighbors), it remains at its current intersection.
    6.  **No New Vehicles:** The total number of vehicles in the system remains constant throughout the simulation. No vehicles are created or destroyed.

*   **`simulateTraffic` Function:**
    *   `func simulateTraffic(network map[string]map[string]int, initialDistribution map[string]int, steps int) map[string]int`
    *   The function should return a `map[string]int` representing the final distribution of vehicles at each intersection after the specified number of simulation steps. The keys are the intersection names, and the values are the number of vehicles.

**Constraints and Edge Cases:**

*   The city's road network can be complex, with many intersections and road segments.
*   The initial vehicle distribution can be uneven, with some intersections having many vehicles and others having few or none.
*   Road segment capacities can vary widely.
*   The number of simulation steps can be large.
*   The input maps (`network`, `initialDistribution`) can be empty.
*   Some intersections might not have any outgoing road segments.
*   Some intersections might not be present in the initial vehicle distribution. If an intersection is not present in the `initialDistribution`, assume it starts with zero vehicles.
*   The solution should be reasonably efficient, especially concerning memory usage and algorithm complexity. Avoid unnecessary copying of large data structures.
*   Ensure that the random movement is truly random and not biased in any way.  Use the `rand` package properly.

**Optimization Requirements:**

*   **Efficiency:** Your solution should be efficient enough to handle a large number of intersections, vehicles, and simulation steps without excessive memory usage or runtime.  Consider the time and space complexity of your algorithms.
*   **Scalability:**  Consider how your solution would scale if the city's road network and the number of vehicles were to increase significantly.

This problem challenges you to combine graph traversal, random number generation, and capacity management in a realistic simulation scenario.  Good luck!
