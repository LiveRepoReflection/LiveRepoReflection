## Problem: Optimal Traffic Light Synchronization

**Description:**

You are tasked with optimizing the synchronization of traffic lights along a major arterial road in a city. The goal is to minimize the average travel time for vehicles traveling the entire length of the road. This is a complex problem with many real-world constraints.

**Road Network:**

The arterial road consists of `N` intersections, numbered from 0 to `N-1`. Each intersection has a traffic light. The distance between intersection `i` and `i+1` is `distance[i]` (where `0 <= i < N-1`). All distances are positive integers.

**Traffic Lights:**

Each traffic light `i` has the following properties:

*   `cycle_time[i]`: The total time (in seconds) for one complete cycle (red + green). This is a constant.
*   `red_duration[i]`: The duration of the red light (in seconds). This is a constant and `red_duration[i] < cycle_time[i]`.
*   `offset[i]`: The offset (in seconds) representing when the light turns green relative to some arbitrary starting time `t=0`. This is what you can adjust.  `0 <= offset[i] < cycle_time[i]`.

A traffic light is green from `offset[i]` to `offset[i] + cycle_time[i] - red_duration[i]`, then red from `offset[i] + cycle_time[i] - red_duration[i]` to `offset[i] + cycle_time[i]`. This pattern repeats indefinitely.

**Vehicles:**

*   Vehicles travel at a constant speed `speed` (meters per second) along the road.
*   Vehicles start at intersection 0 at time `t=0`.
*   Vehicles *must* stop completely at a red light and wait until it turns green.
*   Vehicles are considered to have "passed" an intersection the instant the front of the vehicle reaches the intersection.

**Objective:**

Write a function `optimizeTrafficLights(N int, distance []int, cycle_time []int, red_duration []int, speed int) []int` that takes the road network and traffic light information as input and returns an array of `N` integers representing the optimal `offset` for each traffic light (i.e., `offset[i]`).  The goal is to minimize the *average* travel time for a large number of vehicles.

**Constraints and Considerations:**

1.  **Large-Scale Simulation:**  Directly simulating a large number of vehicles for every possible `offset` combination is computationally prohibitive.  The time limit for execution is tight.
2.  **Complex Interactions:**  The optimal `offset` for one light depends on the `offset` of all the other lights.
3.  **Real-World Considerations:**  Consider how traffic "platoons" might form and how these platoons affect the overall traffic flow.  Avoid solutions that create artificial bottlenecks.
4.  **Potential for Multiple Solutions:** There may be multiple valid solutions. Your algorithm should aim to find a "good" solution, not necessarily the absolute global optimum (which may be impossible to find efficiently).
5.  **Edge Cases:** Handle cases where `N` is small (e.g., 1 or 2) efficiently.
6.  **Reasonable Ranges:**  Assume that all input values are within reasonable ranges. Specifically:
    *   `1 <= N <= 50`
    *   `1 <= distance[i] <= 1000`
    *   `1 <= cycle_time[i] <= 300`
    *   `1 <= red_duration[i] < cycle_time[i]`
    *   `1 <= speed <= 30`

**Input:**

*   `N int`: The number of intersections.
*   `distance []int`: An array of length `N-1` representing the distance between consecutive intersections.
*   `cycle_time []int`: An array of length `N` representing the cycle time of each traffic light.
*   `red_duration []int`: An array of length `N` representing the red light duration of each traffic light.
*   `speed int`: The speed of the vehicles in meters per second.

**Output:**

*   `[]int`: An array of length `N` representing the optimal `offset` for each traffic light.

**Example:**

```go
N := 3
distance := []int{200, 300}
cycle_time := []int{60, 45, 50}
red_duration := []int{30, 20, 25}
speed := 10

optimizeTrafficLights(N, distance, cycle_time, red_duration, speed) // Returns []int{...} (An optimal offset array)
```

**Judging:**

Your solution will be judged based on its correctness and efficiency. Correctness will be determined by running your code on a set of test cases and comparing your output to the expected output. Efficiency will be determined by measuring the execution time of your code. The execution time limit is strict. The solution that yields the lowest average travel time across all test cases will be considered the best. Solutions will be penalized for excessive memory usage.
