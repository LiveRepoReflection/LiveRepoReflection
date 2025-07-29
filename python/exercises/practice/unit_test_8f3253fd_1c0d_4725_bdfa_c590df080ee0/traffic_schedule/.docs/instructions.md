## Question: Optimal Traffic Light Scheduling

### Question Description

You are tasked with optimizing the traffic light schedule for a complex road network in a city. The goal is to minimize the average waiting time of vehicles across the entire network while adhering to safety constraints and real-time traffic conditions.

The road network is represented as a directed graph where:

*   **Nodes:** Intersections with traffic lights. Each intersection has a unique ID.
*   **Edges:** Road segments connecting intersections. Each road segment has a length (in meters) and a speed limit (in km/h).

Each traffic light can be in one of two states: **Green** or **Red**. For simplicity, assume each intersection has only two incoming and two outgoing roads. When a traffic light is Green for an incoming road, vehicles can proceed through the intersection. When it's Red, vehicles must stop.

**Objective:**

Design an algorithm to determine the optimal schedule for each traffic light, specifying the duration of Green and Red phases, to minimize the average waiting time of vehicles in the network.

**Input:**

Your function will receive the following input:

1.  `network`: A dictionary representing the road network graph. The keys are intersection IDs (integers), and the values are dictionaries containing:
    *   `incoming`: A list of tuples representing incoming roads. Each tuple contains: `(source_intersection_id, road_length, speed_limit)`.
    *   `outgoing`: A list of tuples representing outgoing roads. Each tuple contains: `(destination_intersection_id, road_length, speed_limit)`.
2.  `traffic_flow`: A dictionary representing the estimated traffic flow between intersections over a given time period. The keys are tuples of `(source_intersection_id, destination_intersection_id)`, and the values are the number of vehicles expected to travel between those intersections during the time period.
3.  `min_green_time`: Minimum duration (in seconds) for which a traffic light must remain Green.
4.  `max_green_time`: Maximum duration (in seconds) for which a traffic light can remain Green.
5.  `yellow_time`: Fixed duration (in seconds) for the yellow light phase (transition between Green and Red). This is a constant value for all intersections.
6.  `total_simulation_time`: The total duration (in seconds) for which the simulation should run.

**Output:**

Your function should return a dictionary representing the optimal traffic light schedule. The keys are intersection IDs, and the values are lists of tuples. Each tuple in the list represents a phase of the traffic light cycle and contains:

*   `(incoming_road_index, duration)` where `incoming_road_index` represents the index of the incoming road (0 or 1) and `duration` is the duration of the green light phase in seconds. The order of incoming roads in the `network` dictionary defines the index.

**Constraints:**

*   **Safety:** Each traffic light cycle must include a `yellow_time` transition phase after each Green phase.
*   **Minimum and Maximum Green Time:** The duration of each Green phase must be within the `min_green_time` and `max_green_time` constraints.
*   **Cycle Consistency:** The schedule must be cyclic, meaning it repeats continuously throughout the simulation period.
*   **Optimization Goal:** Prioritize minimizing the *average* waiting time of all vehicles in the network. Consider the traffic flow between intersections when optimizing. Assume vehicles arrive at a constant rate during the simulation.
*   **Realistic Road Network:** Assume the road network can be large and complex, requiring efficient algorithms.

**Example:**

```python
network = {
    1: {'incoming': [(2, 500, 50), (3, 600, 40)], 'outgoing': [(4, 700, 60), (5, 800, 50)]},
    2: {'incoming': [(1, 500, 50), (6, 400, 30)], 'outgoing': [(7, 900, 40), (8, 300, 20)]},
    3: {'incoming': [(1, 600, 40), (9, 700, 50)], 'outgoing': [(10, 500, 30), (11, 600, 40)]}
    # ... more intersections
}

traffic_flow = {
    (2, 4): 100,
    (3, 5): 80,
    (1, 7): 120,
    (6, 8): 90,
    (1, 10): 70,
    (9, 11): 110
    # ... more traffic flow data
}

min_green_time = 15
max_green_time = 60
yellow_time = 5
total_simulation_time = 3600  # 1 hour

optimal_schedule = optimize_traffic_lights(network, traffic_flow, min_green_time, max_green_time, yellow_time, total_simulation_time)

# Example of optimal_schedule output:
# {
#     1: [(0, 30), (1, 40)],  # Intersection 1: Incoming road 0 (from intersection 2) Green for 30s, then incoming road 1 (from intersection 3) Green for 40s
#     2: [(0, 25), (1, 35)],  # Intersection 2: ...
#     3: [(0, 35), (1, 45)],  # Intersection 3: ...
#     # ... more intersections
# }
```

**Grading Criteria:**

*   **Correctness:** The solution must produce valid traffic light schedules that adhere to all constraints.
*   **Optimization:** The solution will be evaluated based on the average waiting time achieved for a set of test cases, compared to other submissions. Lower average waiting time scores higher.
*   **Efficiency:** The solution must be able to handle large road networks within a reasonable time limit.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.

This is a challenging problem that requires a combination of graph algorithms, optimization techniques, and careful consideration of real-world constraints. Good luck!
