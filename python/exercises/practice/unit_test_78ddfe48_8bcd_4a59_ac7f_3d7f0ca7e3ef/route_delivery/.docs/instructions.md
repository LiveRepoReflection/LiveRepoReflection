## Question: Optimal Multi-Hop Route Planning with Capacity Constraints

**Description:**

You are tasked with designing an optimal route planning system for a delivery network. The network consists of `N` cities, numbered from 0 to `N-1`. Deliveries must be routed from a source city `S` to a destination city `D`.

The delivery network is represented as a directed graph where:

*   Nodes represent cities.
*   Edges represent delivery routes between cities. Each route has a maximum capacity `C` representing the maximum number of delivery units that can be sent along it at a given time. Each route also has a latency `L` (in seconds) representing the time it takes for a delivery unit to travel along the route.

You are given the following inputs:

*   `N`: The number of cities.
*   `S`: The source city.
*   `D`: The destination city.
*   `edges`: A list of tuples, where each tuple `(u, v, C, L)` represents a directed edge from city `u` to city `v` with capacity `C` and latency `L`.
*   `delivery_units`: The number of delivery units that need to be sent from `S` to `D`.
*   `max_latency`: The maximum acceptable total latency for a single delivery unit to travel from `S` to `D`.  If no path exists with total latency less than or equal to `max_latency`, return -1.

Your goal is to determine the **minimum** number of trips required to deliver all `delivery_units` from city `S` to city `D` such that:

1.  Each trip follows a valid path in the directed graph from `S` to `D`.
2.  The number of delivery units sent on each edge in each trip does not exceed the edge's capacity.
3.  The total latency of each trip (sum of latencies of edges in the path) does not exceed `max_latency`.

**Constraints:**

*   1 <= `N` <= 100
*   0 <= `S`, `D` < `N`
*   `S` != `D`
*   1 <= len(edges) <= 200
*   0 <= `u`, `v` < `N`
*   1 <= `C` <= 100
*   1 <= `L` <= 100
*   1 <= `delivery_units` <= 10000
*   1 <= `max_latency` <= 10000

**Optimization Requirement:**

The solution should be optimized for time complexity. A naive approach will likely result in a timeout for larger test cases. Efficient pathfinding and capacity management are crucial.

**Edge Cases:**

*   No path exists from `S` to `D` with latency <= `max_latency`.
*   The total capacity of paths from `S` to `D` is less than `delivery_units`.
*   `delivery_units` is very large, requiring numerous trips.

**Multiple Valid Approaches:**

Consider the trade-offs between different pathfinding algorithms (e.g., Dijkstra's vs. Bellman-Ford with modifications for capacity). How does the choice of algorithm impact the overall time complexity, especially for large graphs?  How would you handle negative latency values (if allowed)?

**Input Format:**

```python
def min_trips(N: int, S: int, D: int, edges: list[tuple[int, int, int, int]], delivery_units: int, max_latency: int) -> int:
    # Your code here
    pass
```

Good luck!
