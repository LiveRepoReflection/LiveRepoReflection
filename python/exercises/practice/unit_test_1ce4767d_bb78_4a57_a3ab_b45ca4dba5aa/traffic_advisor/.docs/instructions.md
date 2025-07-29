Okay, here's a challenging Python coding problem designed to be at a LeetCode Hard level.

**Project Name:** `AdaptiveTrafficControl`

**Question Description:**

You are tasked with designing an adaptive traffic control system for a grid-based city. The city is represented by an `N x M` grid, where each cell can either be a road (`.`) or a building (`#`).  Traffic flows only along the roads.

The city has `K` major intersections. Each intersection is represented by its coordinates (row, col) on the grid.  Your system must dynamically adjust the traffic light timings at these intersections to minimize the average travel time for all vehicles travelling between any two intersections.

**Vehicle Traffic Simulation:**

A number of vehicles, `V`, simultaneously start their journeys from a randomly selected intersection to another randomly selected (distinct) intersection. Each vehicle takes the shortest path (in terms of number of road cells traversed) to its destination using Breadth-First Search (BFS). If multiple shortest paths exist, the vehicle will choose one uniformly at random.

**Traffic Light Control:**

At each intersection, there are traffic lights controlling the flow of traffic along the four cardinal directions (North, South, East, West). The traffic lights operate on a cycle: Green for a duration `G`, followed by Red for a duration `R`.  You have control over the `G` and `R` values at each intersection. Note that G and R should be non-negative integers.

**Constraints:**

1.  **Grid Size:** 1 <= N, M <= 50
2.  **Number of Intersections:** 2 <= K <= 10
3.  **Number of Vehicles:** 100 <= V <= 500
4.  **Traffic Light Durations:**  You can set `G` and `R` independently for each intersection.  0 <= G, R <= 20.
5.  **Waiting at Intersections:** A vehicle arriving at an intersection while the light is Red must wait until the light turns Green.  Assume a vehicle arrives at the *instant* the light changes.
6.  **Initial Light State:** At the start of the simulation (time t=0), all traffic lights are Green.
7.  **Objective:** Minimize the *average* travel time of all `V` vehicles. Travel time is measured from the moment a vehicle starts its journey until it reaches its destination. This includes waiting time at red lights.
8.  **Time Limit:** Your solution must complete within a strict time limit (e.g., 60 seconds) on a standard machine. Exceeding the time limit will result in a failed submission.
9.  **Memory Limit:** Your solution must adhere to standard memory limits (e.g., 1GB).
10. **Input Format:** The input will be provided as follows:
    *   The first line contains three integers: `N`, `M`, and `K`.
    *   The next `N` lines represent the grid, with each line containing `M` characters (`.` or `#`).
    *   The next `K` lines contain the row and column coordinates (0-indexed) of each intersection.
    *   The final line contains the number of vehicles, `V`.

11. **Output Format:** Your program should output `K` lines. Each line `i` represents the traffic light configuration for intersection `i` and contains two integers, `G_i` and `R_i`, separated by a space.

**Example:**

**Input:**

```
5 5 3
.....
.#.#.
..#..
.#.#.
.....
0 0
2 2
4 4
100
```

**Possible Output:**

```
10 5
8 2
12 3
```

**Judging:**

Your solution will be judged by running it on a series of test cases with different city layouts, intersection configurations, and vehicle counts. The score for each test case will be based on how close your average travel time is to the optimal average travel time (determined by a hidden, highly optimized solution). A small tolerance will be given, but solutions significantly deviating from the optimum will receive little or no credit.

**Hints and Challenges:**

*   **Optimization is Key:** A naive brute-force approach to explore all possible `G` and `R` values will be far too slow. You will need to employ clever optimization techniques. Consider approaches like:
    *   **Heuristics:** Develop heuristics based on traffic density and intersection proximity to guide your search for optimal `G` and `R` values.
    *   **Local Search:** Start with a random configuration and iteratively improve it by making small adjustments to the `G` and `R` values, evaluating the impact on average travel time. Techniques like hill climbing, simulated annealing, or genetic algorithms could be useful.
    *   **Dynamic Programming (Potentially):** While less obvious, exploring if dynamic programming can be applied to precompute shortest paths and then efficiently evaluate different traffic light configurations may be fruitful.
*   **Efficient Simulation:** The traffic simulation must be highly efficient.  Optimize your BFS implementation and consider caching shortest paths between intersections to avoid redundant calculations. Be aware of Python's performance limitations and consider using libraries like NumPy where appropriate.
*   **Edge Cases:** Pay careful attention to edge cases, such as:
    *   Intersections that are unreachable from other intersections.
    *   Vehicles that get "stuck" in loops due to traffic light timings.
    *   Grid layouts that lead to highly congested areas.
*   **Parallelism:**  If possible, explore using Python's multiprocessing capabilities to parallelize the simulation of different traffic light configurations. This can significantly reduce the time required to evaluate a given configuration.
*   **Time Complexity:** Analyze the time complexity of your solution and identify potential bottlenecks.  Aim for a solution with a time complexity that is polynomial in `N`, `M`, `K`, and `V`, but with a low constant factor.

This problem combines graph algorithms, simulation, and optimization, requiring a deep understanding of algorithmic techniques and efficient coding practices. Good luck!
