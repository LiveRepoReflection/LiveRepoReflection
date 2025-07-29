## Question: The Optimal Traffic Light Controller

### Question Description

Design an algorithm to optimize traffic flow in a simulated city. The city is represented as a directed graph where nodes are intersections and edges are roads connecting them. Each road has a capacity representing the maximum number of vehicles that can traverse it in a unit of time. Each intersection has a traffic light controlling the flow of traffic.

Initially, all traffic lights have a fixed cycle: a sequence of phases, each lasting a specific duration. Each phase allows traffic from a specific set of incoming roads to proceed. The goal is to dynamically adjust the traffic light cycle at each intersection to minimize the average travel time of vehicles through the city.

You are given:

*   **A directed graph:** Representing the city's road network. Nodes are labeled from `0` to `N-1`, where N is the number of intersections.
*   **Road capacities:** A matrix `capacities[i][j]` representing the capacity of the road from intersection `i` to intersection `j`. A value of `0` indicates no road exists between the intersections.
*   **Initial traffic light cycles:** A list of `TrafficLightCycle` objects, one for each intersection. A `TrafficLightCycle` consists of a list of `Phase` objects. Each `Phase` object contains:
    *   A list of incoming roads (identified by the source intersection) that are allowed to proceed during this phase.
    *   The duration of the phase.
*   **Vehicle arrival rates:** A matrix `arrivalRates[i][j]` representing the average number of vehicles arriving at intersection `j` from intersection `i` per unit of time. A value of `0` indicates no vehicles arrive from that source.
*   **Simulation time:** The total time (in units of time) for which the simulation should run.

Your task is to implement a function that dynamically adjusts the traffic light cycles at each intersection to minimize the average travel time of all vehicles during the simulation. You can only modify the *duration* of each existing phase, but the order of phases and which incoming roads are allowed to proceed during each phase MUST remain the same. The total duration of all phases in a cycle must remain constant.

**Constraints:**

*   The number of intersections (N) will be in the range [2, 50].
*   Road capacities will be in the range [0, 1000].
*   Arrival rates will be in the range [0, 500].
*   Simulation time will be in the range [100, 1000].
*   The number of phases in each traffic light cycle will be in the range [1, 5].
*   Phase durations will be non-negative integers.
*   The total duration of all phases in a cycle will be between [10, 50].
*   Your solution must be efficient. The simulation needs to run within a reasonable time limit (e.g., a few seconds).
*   You cannot change the *order* of phases in a traffic light cycle.
*   You cannot change which incoming roads are allowed to proceed during a phase, only the duration of the phase.
*   The total duration of all phases in a cycle must remain constant throughout the simulation.
*   The vehicles should be processed on a First-In-First-Out (FIFO) basis for each road.

**Optimization Requirements:**

*   Minimize the average travel time of vehicles during the simulation. This is calculated as the total travel time of all vehicles divided by the total number of vehicles that successfully reached their destinations during the simulation.
*   Your algorithm should be able to adapt to changing traffic conditions during the simulation.

**System Design Aspects:**

*   Consider how you would represent the state of the simulation (e.g., vehicle queues on roads, current phase of each traffic light).
*   Think about how you would efficiently update the simulation state at each time step.
*   How would you evaluate the performance of different traffic light configurations?

**Multiple Valid Approaches:**

*   There are likely multiple valid approaches to this problem. Some possible strategies include:
    *   Gradient descent-based optimization
    *   Reinforcement learning
    *   Heuristic search algorithms (e.g., simulated annealing, genetic algorithms)

**Classes:**

```java
class Phase {
    List<Integer> allowedIncomingRoads; // List of source intersections allowed in this phase
    int duration; // Duration of the phase
}

class TrafficLightCycle {
    List<Phase> phases;
    int totalDuration; // The sum of all phase durations, which MUST remain constant.
}
```

**Input (Provided):**

*   `N`: Number of intersections
*   `capacities`: `int[][]` - Road capacities
*   `initialTrafficLightCycles`: `List<TrafficLightCycle>` - Initial traffic light cycles
*   `arrivalRates`: `int[][]` - Vehicle arrival rates
*   `simulationTime`: `int` - Total simulation time

**Output (Required):**

*   A `List<TrafficLightCycle>` representing the optimized traffic light cycles for each intersection after the simulation.

This problem requires a combination of algorithmic thinking, system design, and optimization techniques to achieve good performance. Good luck!
