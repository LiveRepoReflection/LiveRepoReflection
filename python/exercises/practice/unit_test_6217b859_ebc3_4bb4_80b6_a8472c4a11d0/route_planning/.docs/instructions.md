## Question: Optimal Multi-Hop Route Planning with Capacity Constraints

### Description:

You are tasked with designing an optimal route planning algorithm for a delivery network. The network consists of `N` cities, numbered from `0` to `N-1`. Deliveries need to be made from a central warehouse (city `0`) to various destination cities.

The network is represented as a directed graph where edges represent transportation routes between cities. Each edge `(u, v)` has:

*   A **travel time** `time(u, v)` representing the time taken to travel from city `u` to city `v`.
*   A **capacity** `capacity(u, v)` representing the maximum number of delivery vehicles that can travel this route simultaneously.

You are given a list of `M` delivery requests. Each request `i` specifies:

*   A **destination city** `destination(i)`.
*   A **number of vehicles** `vehicles(i)` required to fulfill the request.
*   A **delivery deadline** `deadline(i)` by which the vehicles must arrive at the destination city.

Your goal is to determine a set of routes for each delivery request such that:

1.  **All delivery requests are fulfilled.**
2.  **The number of vehicles traveling on any edge at any given time does not exceed the edge's capacity.**
3.  **All vehicles for a given delivery request arrive at their destination city before the specified deadline.**
4.  **The total travel time across all delivery requests is minimized.**

**Input:**

*   `N`: The number of cities.
*   `edges`: A list of tuples `(u, v, time, capacity)` representing the directed edges in the network.
*   `requests`: A list of tuples `(destination, vehicles, deadline)` representing the delivery requests.

**Output:**

A list of lists representing the routes for each request. The i-th inner list represents the route (sequence of cities) for the i-th request, or `None` if no feasible solution exists.

**Constraints and Considerations:**

*   `1 <= N <= 500`
*   `1 <= M <= 100`
*   `1 <= time(u, v) <= 100`
*   `1 <= capacity(u, v) <= 100`
*   `1 <= vehicles(i) <= 100`
*   `1 <= deadline(i) <= 1000`
*   The graph might not be fully connected.
*   Multiple routes might exist between two cities, each with different travel times and capacities.
*   A city can appear multiple times in a single route.
*   You must find the *optimal* solution that minimizes the total travel time.
*   Assume vehicles leave the warehouse (city 0) at time 0.
*   If multiple optimal solutions exist, any one of them is acceptable.

**Example:**

```
N = 4
edges = [
    (0, 1, 5, 10),
    (0, 2, 8, 5),
    (1, 3, 6, 8),
    (2, 3, 4, 7)
]
requests = [
    (3, 3, 15),  # Destination 3, 3 vehicles, deadline 15
    (3, 2, 18)   # Destination 3, 2 vehicles, deadline 18
]

# Possible optimal output (routes for each request):
[
    [0, 1, 3],   # Request 1: Route from 0 to 3 via 1 (total time 5 + 6 = 11 <= 15)
    [0, 2, 3]    # Request 2: Route from 0 to 3 via 2 (total time 8 + 4 = 12 <= 18)
]
```

**Grading:**

Your solution will be evaluated based on correctness, efficiency (time complexity), and optimality (minimizing total travel time). Solutions that fail to meet the constraints or do not find a feasible route will be penalized. Solutions that find a feasible solution but not the optimal one will receive partial credit.
