## Question: Optimal Traffic Light Control

**Problem Description:**

You are tasked with optimizing the traffic flow in a simulated city. The city's road network is represented as a directed graph, where nodes represent intersections and edges represent roads. Each road has a capacity, representing the maximum number of vehicles that can travel on it per unit of time. Each intersection has a set of traffic lights that control the flow of traffic.

Your goal is to implement a traffic light control system that minimizes the average travel time of vehicles across the city.

**Specifically:**

1.  **Input:**
    *   A directed graph representing the city's road network. The graph will be provided as an adjacency list. Each node (intersection) is labeled with a unique integer ID from 0 to N-1, where N is the total number of intersections. Each edge (road) will have the following properties:
        *   `to`: The ID of the destination intersection.
        *   `capacity`: The maximum number of vehicles that can travel on this road per unit of time (an integer).
        *   `travel_time`:  The time (in arbitrary units) it takes a vehicle to traverse the road when there's no congestion (an integer).

    *   A list of vehicle routes. Each route consists of a sequence of intersection IDs that a vehicle must traverse. Each route also specifies the number of vehicles following that route.

    *   The number of traffic light phases allowed at each intersection. A phase defines which incoming and outgoing roads have a green light simultaneously.

2.  **Traffic Light Control:**
    *   Each intersection can have multiple traffic light phases. Each phase is defined by a set of incoming and outgoing roads that are allowed to have a green light simultaneously. The traffic lights cycle through these phases in a fixed order. The duration of each phase can be adjusted to optimize traffic flow.
    *   When a vehicle arrives at an intersection and the traffic light is green for the road it wants to take, it can proceed immediately. Otherwise, it must wait until the traffic light cycles to a green phase for that road.
    *   The time it takes for traffic lights to switch between phases is negligible.

3.  **Simulation:**
    *   You need to simulate the traffic flow for a fixed period (e.g., 1000 time units).
    *   Vehicles start their routes at time 0.
    *   Vehicles travel along roads at a rate limited by the road's capacity. If the number of vehicles wanting to enter a road exceeds its capacity at any given time, vehicles are queued (delayed) at the origin intersection. These vehicles will enter the road in the next time unit, if there is capacity available.
    *   Congestion on a road increases the travel time. The travel time on a road at time `t` is calculated as: `travel_time_base * (1 + congestion_factor * (num_vehicles_on_road(t) / capacity))`, where:
        *   `travel_time_base` is the base travel time of the road.
        *   `congestion_factor` is a global parameter (e.g., 0.5) that determines the sensitivity of travel time to congestion.
        *   `num_vehicles_on_road(t)` is the number of vehicles currently on the road at time `t`.

4.  **Optimization:**
    *   Your goal is to minimize the average travel time of all vehicles across all routes. Average travel time is calculated as the total time spent by all vehicles on their routes, divided by the total number of vehicles.
    *   You can control the following parameters to achieve this:
        *   **Phase Durations:** The duration (in time units) of each traffic light phase at each intersection. The sum of phase durations at each intersection must be a fixed value (e.g., 60 time units).
        *   **Phase Configurations:** The configuration of the traffic light phases (which incoming and outgoing roads are green in each phase) are fixed and provided as input and cannot be changed.

5.  **Constraints:**

    *   The number of intersections (N) will be in the range of 10 to 100.
    *   The number of roads (M) will be in the range of 20 to 500.
    *   The number of routes (R) will be in the range of 10 to 200.
    *   Road capacities will be integers between 1 and 10.
    *   Base travel times will be integers between 1 and 20.
    *   The number of phases per intersection will be between 2 and 4.
    *   Phase durations must be non-negative integers.
    *   The total duration of phases at each intersection is fixed (e.g., 60 time units).
    *   You must complete your solution within a reasonable time limit (e.g., 5 seconds).

6.  **Output:**
    *   A list of phase durations for each intersection. The output should be formatted as follows: `[[duration_phase_1_intersection_0, duration_phase_2_intersection_0, ...], [duration_phase_1_intersection_1, duration_phase_2_intersection_1, ...], ...]`.

**Judging Criteria:**

Your solution will be judged based on the average travel time of vehicles across the city. Solutions with lower average travel times will be ranked higher. Solutions that violate the constraints or time out will be considered incorrect.

**Scoring:**

Your solution will be tested against a hidden set of test cases. The score for each test case will be inversely proportional to the average travel time of your solution, compared to the best solution submitted by other participants.

**Challenge:**

This problem requires a combination of graph algorithms, simulation techniques, and optimization strategies. You will need to design an efficient algorithm to explore the space of possible phase durations and find a configuration that minimizes average travel time while respecting the capacity constraints and congestion effects. Consider using techniques like gradient descent, simulated annealing, or genetic algorithms to optimize the phase durations.  The complexity arises from the interplay of capacity constraints, variable travel times due to congestion, and the cyclic nature of traffic light phases.
