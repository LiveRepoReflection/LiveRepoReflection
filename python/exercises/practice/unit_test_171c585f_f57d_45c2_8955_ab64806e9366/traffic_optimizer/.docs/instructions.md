Okay, I'm ready to create a challenging Python coding problem suitable for a high-level programming competition. Here's the problem statement:

## Problem: Optimal Traffic Light Scheduling

**Description:**

The city of Algorithmia is experiencing severe traffic congestion. As a brilliant algorithm designer, you've been tasked with optimizing the traffic light schedules to minimize the average waiting time for vehicles. The city's road network can be represented as a directed graph, where nodes represent intersections and edges represent roads connecting the intersections. Each road has a specific length and a maximum speed limit. Each intersection has traffic lights controlling the flow of traffic.

You are given:

*   **N:** The number of intersections (numbered from 0 to N-1).
*   **M:** The number of roads.
*   **roads:** A list of tuples (u, v, length, speed_limit), where 'u' and 'v' are the starting and ending intersections of the road, 'length' is the length of the road, and 'speed_limit' is the maximum allowed speed on that road.  Assume the units for 'length' and 'speed_limit' produce travel times in seconds (e.g., length in meters, speed_limit in meters/second).
*   **K:** The number of traffic light schedules you can control.
*   **lights:** A list of the intersections (nodes in the graph) with traffic lights that you can control.
*   **max_cycle_time:** A maximum cycle time allowed for any traffic light schedule. All traffic lights have a *cycle*, consisting of a green light duration and a red light duration.
*   **arrival_times:** A list of tuples representing the arrival times and paths of vehicles. Each tuple is of the format `(arrival_time, path)`, where `arrival_time` is the time (in seconds) the vehicle enters the network, and `path` is a list of intersection IDs representing the route the vehicle will take. Vehicles travel at the road's speed limit.

Your task is to determine the optimal green light durations for each of the K traffic lights you control to minimize the average waiting time for all vehicles.  You must return a list of K floating-point numbers representing the green light durations for each of the K traffic lights, rounded to two decimal places.

**Constraints:**

*   1 <= N <= 100
*   1 <= M <= 500
*   1 <= K <= min(N, 10)
*   1 <= length <= 1000
*   1 <= speed\_limit <= 100
*   1 <= max\_cycle\_time <= 300
*   0 <= arrival\_time <= 1000
*   The graph is guaranteed to be connected.
*   All roads are one-way only.
*   The path for each vehicle is guaranteed to be valid (i.e., there exists a road connecting consecutive intersections in the path).
*   Traffic lights switch instantaneously (no transition time).
*   All green and red light durations must be non-negative and the sum of the green and red light duration must be <= max_cycle_time.
*   Assume a simple queuing model: vehicles arrive at a traffic light and wait if it's red; they immediately proceed when the light turns green (or is already green).
*   The solution needs to be computationally efficient as the grader will use large test cases.

**Scoring:**

Your score will be based on the average waiting time of all the vehicles, with lower average waiting times resulting in higher scores. The grading system will compare against other submissions.

**Example:**

Let's say you have two controllable lights (K=2). The green light duration for the first light is `green_time_1`, and for the second, it's `green_time_2`. The red light duration for each light is implicitly `max_cycle_time - green_time`. A vehicle arrives at the first traffic light. Based on its arrival time and the traffic light's schedule (`green_time_1` and `max_cycle_time`), the vehicle may have to wait. The same logic applies to the second traffic light when the vehicle reaches it.  The goal is to find `green_time_1` and `green_time_2` that minimize the average wait time across all vehicles.

**Note:** This is a complex optimization problem.  A brute-force approach will likely time out.  Consider using techniques like gradient descent, simulated annealing, or other optimization algorithms, potentially combined with efficient graph traversal and simulation to evaluate the impact of traffic light timings. The traffic lights start at time 0 with the green light on.

This problem requires a combination of graph algorithms, simulation, and optimization techniques. It's designed to be challenging and differentiate strong programmers. Good luck!
