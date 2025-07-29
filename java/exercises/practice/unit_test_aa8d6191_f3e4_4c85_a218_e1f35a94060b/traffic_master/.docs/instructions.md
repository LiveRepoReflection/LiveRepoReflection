## Project Name

```
AdaptiveTrafficControl
```

## Question Description

You are tasked with designing an adaptive traffic control system for a city. The city can be represented as a directed graph where nodes represent intersections and edges represent roads connecting them. Each road has a *capacity* (maximum number of vehicles that can pass through it per unit time) and a *travel time* (time taken to traverse the road under ideal conditions).

The traffic control system needs to dynamically adjust the *cycle length* and *green light duration* for each intersection to minimize the overall average travel time across the city.

**Specific Requirements:**

1.  **Graph Representation:** Implement a data structure to represent the city's road network. The graph should allow efficient retrieval of neighbors (outgoing roads) for each intersection, as well as the capacity and travel time of each road.

2.  **Traffic Simulation:** Simulate traffic flow through the city for a given time period. You are provided with a series of vehicle *requests*. Each request specifies a start intersection, a destination intersection, and an arrival time at the start intersection.

3.  **Traffic Control Policy:** Each intersection has a traffic light that cycles through its outgoing roads. For each road, the light is green for a certain *duration* within the *cycle length*. The sum of the green light durations for all outgoing roads of an intersection must equal the cycle length.

4.  **Adaptive Adjustment:** Implement an algorithm to adjust the cycle length and green light durations for each intersection based on the observed traffic conditions. The goal is to minimize the average travel time of vehicles across the city. You can use any approach (e.g., gradient descent, reinforcement learning, heuristics) to achieve this. The system should adapt in real-time to changing traffic patterns. The algorithm should be time efficient.

5.  **Performance Metrics:** Measure the performance of your traffic control system based on the following metrics:
    *   **Average Travel Time:** Average time taken by vehicles to reach their destinations.
    *   **Throughput:** Number of vehicles that successfully reach their destinations within the simulation period.
    *   **Queue Length:** Average queue length at each intersection.
    *   **Road Utilization:** average number of car on a specific road per time unit / road capacity (the closer to 1 the more utilized the road is).
    *   **Jerk:** absolute changes in the traffic policy (Green light duration, cycle length) per time unit. We want to keep the jerk low to avoid sudden policy changes.

6.  **Constraints:**
    *   The cycle length for each intersection must be within a specified range (e.g., 30 seconds to 180 seconds).
    *   The green light duration for each road must be non-negative.
    *   The capacity of each road cannot be exceeded. If the number of vehicles waiting to enter a road exceeds its capacity, the excess vehicles must wait in a queue at the intersection.
    *   The number of vehicles in the simulation can be very large (e.g., millions). The system should be able to handle this scale efficiently.
    *   The simulation time can be long (e.g., several hours). The system should adapt in a reasonable amount of time (e.g., minutes).
    *   You need to minimize the average travel time while keeping the jerk low. It is okay to have a tradeoff between those two.
    *   Road capacity is an integer, but travel time, cycle length, and green light duration can be double.
    *   Intersections are identified by unique integer IDs.

**Input:**

*   A description of the city's road network (intersections, roads, capacities, travel times).
*   A stream of vehicle requests (start intersection, destination intersection, arrival time).
*   Simulation parameters (simulation time, adaptation frequency, initial traffic control policy).

**Output:**

*   The final traffic control policy (cycle lengths and green light durations for each intersection).
*   The performance metrics (average travel time, throughput, queue lengths, road utilization, jerk).
*   For each vehicle, a log containing its arrival time at the source, its departure time from the source, and its arrival time at the destination.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   Correctness: The traffic simulation and traffic control policy must be implemented correctly.
*   Efficiency: The system must be able to handle large-scale traffic simulations efficiently.
*   Effectiveness: The traffic control policy must effectively minimize average travel time.
*   Adaptability: The system must be able to adapt to changing traffic patterns.
*   Code Quality: The code must be well-structured, readable, and maintainable.

This problem requires a strong understanding of graph data structures, traffic simulation techniques, and optimization algorithms. Good luck!
