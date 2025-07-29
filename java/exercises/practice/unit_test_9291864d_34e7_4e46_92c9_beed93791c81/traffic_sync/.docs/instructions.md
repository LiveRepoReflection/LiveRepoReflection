## Question: Optimal Traffic Light Synchronization

**Problem Description:**

Imagine you are tasked with optimizing traffic flow in a smart city. The city has a network of N intersections connected by roads. Each intersection has a traffic light that cycles through a sequence of colors (Red, Yellow, Green) with specific durations for each color. Your goal is to find the optimal synchronization scheme for these traffic lights to minimize the average travel time between any two intersections in the city.

**Detailed Setup:**

1.  **City Representation:** The city is represented as a directed graph where:
    *   Nodes (Vertices) are intersections, numbered from 0 to N-1.
    *   Edges are roads connecting the intersections. Each road has a travel time (in seconds) associated with it, representing the time it takes to travel from one intersection to another. The graph may contain cycles.
    *   Assume that waiting time to turn is negligible.

2.  **Traffic Lights:** Each intersection `i` has a traffic light with the following properties:
    *   `cycle_duration[i]`: The total duration (in seconds) of one complete cycle of the traffic light.
    *   `color_timings[i]`: An array of three integers representing the durations (in seconds) of Red, Yellow, and Green, in that order.  The sum of `color_timings[i]` must equal `cycle_duration[i]`.
    *   `offset[i]`:  The starting offset (in seconds, relative to a global time zero) of the traffic light cycle. At time `t = offset[i]`, the traffic light at intersection `i` starts its cycle from the beginning (Red).

3.  **Travel Time Calculation:** When a vehicle arrives at an intersection, it may have to wait if the traffic light is Red or Yellow.

    *   If the light is Green, the vehicle can proceed immediately.
    *   If the light is Red or Yellow, the vehicle must wait until the light turns Green. The waiting time is calculated as the time until the *end* of the Red/Yellow phase.

4.  **Synchronization:** The only parameter you can control is the `offset[i]` for each traffic light. Your task is to find the optimal `offset[i]` for each intersection `i` such that the average travel time between all pairs of intersections is minimized.

**Input:**

*   `N`: The number of intersections (nodes in the graph).
*   `edges`: A list of tuples `(u, v, travel_time)`, where:
    *   `u` is the starting intersection (0 <= u < N).
    *   `v` is the ending intersection (0 <= v < N).
    *   `travel_time` is the time in seconds to travel from intersection `u` to intersection `v`.
*   `cycle_duration`: An array of N integers, where `cycle_duration[i]` is the cycle duration of the traffic light at intersection `i`.
*   `color_timings`: A 2D array of N rows and 3 columns, where `color_timings[i][0]` is the Red duration, `color_timings[i][1]` is the Yellow duration, and `color_timings[i][2]` is the Green duration for intersection `i`.

**Output:**

*   An array of N integers representing the optimal `offset[i]` for each intersection `i`.  Offsets must be non-negative integers. Offsets should be within the range of [0, cycle\_duration\[i]).

**Constraints:**

*   2 <= N <= 25 (The number of intersections is relatively small, hinting at the possible use of some exponential or factorial complexity algorithms for certain parts of the solution)
*   1 <= travel\_time <= 1000
*   1 <= cycle\_duration\[i] <= 600
*   0 <= color\_timings\[i][j] <= 600
*   The graph is guaranteed to be strongly connected (there is a path between any two intersections).
*   The solution must be found within a reasonable time limit (e.g., a few minutes).

**Optimization Requirement:**

Minimize the average travel time between all pairs of intersections. The average travel time is calculated as follows:

1.  For each pair of intersections (start, end), find the shortest path (in terms of total travel time including waiting times) from 'start' to 'end'.
2.  Sum the shortest path travel times for all possible pairs of intersections.
3.  Divide the sum by the total number of pairs (N * (N - 1)).

**Edge Cases and Considerations:**

*   **Cycles in the Graph:**  The shortest path between two intersections might involve traversing cycles. You need to handle this.
*   **Multiple Shortest Paths:** If there are multiple shortest paths between two intersections, use any one of them.
*   **Time Complexity:**  A brute-force approach (trying all possible offset combinations) would be extremely slow. You need to devise a more efficient algorithm.
*   **Local Optima:** The search space might have local optima.  Consider using techniques to escape local optima, such as simulated annealing or genetic algorithms.
*   **Integer Offsets:** The offsets must be integers. You cannot have fractional offsets.

**Judging Criteria:**

Your solution will be judged based on the average travel time it achieves on a set of hidden test cases. A lower average travel time indicates a better solution. The efficiency of your code will also be considered, especially the time it takes to find a solution. Solutions that time out will not be considered correct.

This problem requires a combination of graph algorithms (shortest path), optimization techniques, and careful handling of time calculations. Good luck!
