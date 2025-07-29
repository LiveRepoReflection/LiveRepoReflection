## The Celestial Cartographers

**Problem Description:**

The year is 2342. Humanity has established a sprawling network of space stations connected by wormholes. The "Celestial Cartographers" are tasked with maintaining an accurate map of this network, crucial for navigation, resource allocation, and defense.

The space station network can be modeled as a weighted, undirected graph. Each space station is a node, and each wormhole connecting two stations is an edge with a specific traversal time. Due to the unpredictable nature of space, the traversal time of a wormhole can fluctuate within a given range.

You are given:

*   `N`: The number of space stations, numbered from 0 to N-1.
*   `M`: The number of wormholes.
*   A list of wormholes, each represented by a tuple `(u, v, min_time, max_time)`, where:
    *   `u` and `v` are the IDs of the space stations connected by the wormhole.
    *   `min_time` is the minimum possible traversal time for that wormhole.
    *   `max_time` is the maximum possible traversal time for that wormhole.
*   `Q`: The number of queries.
*   A list of queries, each represented by a tuple `(start_station, end_station, allowed_time)`.

For each query, determine the **probability** that a traveler can reach `end_station` from `start_station` within the `allowed_time`.

**Assumptions:**

*   The traversal time of each wormhole follows a uniform distribution within its `[min_time, max_time]` range.
*   The traversal times of different wormholes are independent of each other.
*   The traveler will always choose the fastest path given the current wormhole traversal times.
*   If no path exist between start and end station, the probability is 0.

**Input Format:**

The input will be provided to your program as follows:

```
N M
u1 v1 min_time1 max_time1
u2 v2 min_time2 max_time2
...
uM vM min_timeM max_timeM
Q
start1 end1 allowed_time1
start2 end2 allowed_time2
...
startQ endQ allowed_timeQ
```

**Output Format:**

For each query, print the probability (as a floating-point number with at least 6 decimal places of precision) on a new line.

**Constraints:**

*   1 <= N <= 50
*   1 <= M <= N * (N - 1) / 2
*   0 <= u, v < N
*   1 <= min_time <= max_time <= 100
*   1 <= Q <= 100
*   0 <= start, end < N
*   1 <= allowed_time <= 10000

**Example:**

```
4 4
0 1 1 2
0 2 2 3
1 2 3 4
2 3 4 5
1
0 3 10
```

**Scoring:**

*   Correctness (Passing all test cases)
*   Efficiency (Solution should be able to handle the maximum input size within a reasonable time limit)

**Challanges:**

*   The number of possible wormhole traversal time combinations is exponential. Naively enumerating all combinations will not be efficient enough.
*   Calculating the probability accurately requires careful consideration of the continuous nature of the traversal time distributions and the shortest path algorithm.
*   The problem requires careful implementation of graph algorithms and probability calculations. You may want to explore sampling or approximation techniques to achieve the desired accuracy within the time limit.
