## Question: Optimal Traffic Light Control

### Problem Description

You are tasked with designing an intelligent traffic light control system for a complex road network. The road network is represented as a directed graph where nodes represent intersections and edges represent road segments connecting intersections. Each road segment has a capacity, representing the maximum number of vehicles that can traverse it per unit of time. Each intersection has a set of traffic lights, one for each incoming road segment.

The goal is to minimize the average waiting time of vehicles in the network. Vehicles arrive at each intersection at a certain rate (vehicles per unit time) along each incoming road segment. When a vehicle arrives at an intersection, it must wait until the traffic light for its incoming road segment turns green. The traffic light cycle is divided into phases. In each phase, a subset of traffic lights at each intersection is green, allowing vehicles from the corresponding incoming road segments to pass through the intersection and proceed along their chosen outgoing road segment.

**Constraints:**

1.  **Network Representation:** The road network will be provided as a list of intersections and a list of road segments. Each intersection will have a unique ID. Each road segment will have a source intersection ID, a destination intersection ID, a capacity, and an arrival rate.
2.  **Traffic Light Phases:** You must define the traffic light phases for each intersection. Each phase specifies which incoming road segments have a green light. The duration of each phase is fixed.
3.  **Phase Duration:** The duration of each phase is a global constant, `PHASE_DURATION`. This is provided.
4.  **Switching Time:**  There is a fixed switching time, `SWITCHING_TIME`, between phases at each intersection. During this time, all traffic lights are red.  This value is also provided.
5.  **Vehicle Routing:** Vehicles arriving at an intersection choose their outgoing road segment according to a fixed probability distribution. This distribution will be provided for each intersection. Note that the route choice probabilities may change over time.
6.  **Capacity Constraint:** The number of vehicles passing through a road segment in a given time unit cannot exceed its capacity.
7.  **Fairness:** All incoming road segments at an intersection must have at least one phase in which their traffic light is green within a complete cycle.
8.  **Optimization Goal:** Minimize the average waiting time of vehicles in the network. Waiting time is defined as the time a vehicle spends at an intersection waiting for its traffic light to turn green.  Average the waiting time across *all* vehicles entering the network over a simulation period.
9.  **Simulation:**  Your solution needs to simulate the traffic flow for a given simulation time. The simulation involves tracking vehicles as they arrive, wait at intersections, and travel along road segments.
10. **Dynamic Arrival Rates:** The arrival rates for each road segment may change over time. Your solution should adapt to these changes.
11. **Real-time Performance:**  The solution must be able to re-optimize the traffic light phases efficiently (within a reasonable time limit) when arrival rates change significantly. The system must re-optimize every `REOPTIMIZATION_INTERVAL` which is provided.
12. **Deadlock Prevention:** The configuration of traffic light phases must prevent deadlocks, where vehicles are indefinitely stuck in the network because no path is available.
13. **Integer Phase Durations:** For simplicity, assume that `PHASE_DURATION` and `SWITCHING_TIME` are integers.
14. **Integer Vehicle Counts:** For simulation purposes, you can assume that vehicle arrival rates are scaled so that the number of vehicles arriving in a single simulation step is an integer.

**Input:**

*   A description of the road network (intersections and road segments).
*   `PHASE_DURATION`: Duration of each traffic light phase.
*   `SWITCHING_TIME`: Switching time between phases.
*   Vehicle routing probabilities for each intersection.
*   Initial vehicle arrival rates for each road segment.
*   Simulation time.
*   `REOPTIMIZATION_INTERVAL`: Time between re-optimization.

**Output:**

*   A list of traffic light phases for each intersection. Each phase should specify the IDs of the incoming road segments that have a green light during that phase.
*   The average waiting time of vehicles in the network after the simulation.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   Correctness: The traffic light phases must be valid and prevent deadlocks.
*   Efficiency: The average waiting time of vehicles must be minimized.
*   Scalability: The solution must be able to handle large road networks.
*   Real-time Performance: The solution must be able to re-optimize the traffic light phases efficiently when arrival rates change.

This problem requires a combination of graph algorithms, optimization techniques, and simulation skills. Good luck!
