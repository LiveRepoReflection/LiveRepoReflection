## Problem: Autonomous Traffic Management System

### Question Description

You are tasked with designing a core component of an Autonomous Traffic Management System (ATMS) for a smart city. The system aims to optimize traffic flow by dynamically adjusting traffic light timings based on real-time traffic conditions.

The city's road network is represented as a directed graph where:

*   Nodes represent intersections. Each intersection has a unique ID from `0` to `N-1`.
*   Edges represent road segments connecting intersections. Each road segment has a length (in meters) and a current traffic density (vehicles per meter).

Your task is to implement a function that calculates the optimal traffic light schedule for a specific intersection, given the current state of the surrounding road network.

**Specifics:**

1.  **Input:**
    *   `N`: An integer representing the number of intersections in the city (0 to N-1).
    *   `roads`: A list of tuples, where each tuple `(u, v, length, density)` represents a directed road segment from intersection `u` to intersection `v` with length `length` (in meters) and current traffic density `density` (vehicles/meter).
    *   `target_intersection`: An integer representing the ID of the intersection for which you need to optimize the traffic light schedule.
    *   `time_horizon`: An integer representing the time horizon (in seconds) for which the schedule needs to be optimized. This means you need to find a schedule that minimizes the total waiting time at the `target_intersection` for all incoming vehicles within this time frame.
    *   `min_green_time`: Minimum green time allowed for any incoming roads on the target intersection.
    *   `max_green_time`: Maximum green time allowed for any incoming roads on the target intersection.
    *   `amber_time`: Fixed amber time allowed for any incoming roads on the target intersection.

2.  **Traffic Model:**

    *   Assume vehicles arrive at the start of each road segment at a rate proportional to the density of that segment. This means you need to calculate the number of vehicles arriving at the `target_intersection` from each incoming road within the `time_horizon`.
    *   Assume vehicles travel at a constant speed of `speed = 10 m/s` on all road segments when there is no congestion.
    *   Assume waiting vehicles consume 1 unit of time (seconds) per vehicle. The objective is to minimize total waiting time for all vehicles arriving at the intersection within the given `time_horizon`.
    *   Assume there is enough road capacity to accommodate all incoming vehicles, vehicles do not block the flow of other vehicles, they only incur waiting time at the intersection.

3.  **Traffic Light Schedule:**

    *   The traffic light schedule is a sequence of green times for each incoming road to the `target_intersection`. After each green time, there is a fixed `amber_time` before switching to the next road.
    *   You need to determine the optimal green times for each incoming road to minimize the total waiting time of vehicles arriving at the `target_intersection` within the `time_horizon`.
    *   Green times must be within the range `[min_green_time, max_green_time]`.

4.  **Objective:**

    *   Minimize the total waiting time (in seconds) of all vehicles arriving at the `target_intersection` within the `time_horizon`.

5.  **Constraints:**

    *   The number of intersections `N` can be up to 100.
    *   The number of road segments can be up to 200.
    *   `0 <= u, v < N` for each road segment `(u, v, length, density)`.
    *   `0 < length <= 10000` (meters).
    *   `0 <= density <= 1.0` (vehicles/meter).
    *   `0 <= target_intersection < N`.
    *   `0 < time_horizon <= 3600` (seconds).
    *   `0 < min_green_time <= 60` (seconds).
    *   `60 < max_green_time <= 300` (seconds).
    *   `0 < amber_time <= 10` (seconds).

6.  **Optimization:**
    *   The solution needs to be computationally efficient. A naive brute-force approach will likely time out. Consider dynamic programming, gradient descent, or other optimization techniques.
    *   Assume that the time taken for vehicles to travel along road segments to the target intersection is negligible compared to the waiting time.

7.  **Output:**

    *   Return a list of integers representing the optimal green times (in seconds) for each incoming road to the `target_intersection`. The order of the green times should correspond to the order of the incoming roads in the `roads` input.
    *   If no incoming roads exist, return an empty list `[]`.
    *   If no valid solution is found satisfying the constraints, return `None`.

This problem combines graph traversal, traffic modeling, and optimization, requiring careful consideration of algorithmic efficiency and constraint satisfaction. Good luck!
