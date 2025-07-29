## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an efficient route planning system for a delivery service operating in a large, densely populated urban environment. The city can be represented as a weighted directed graph, where nodes represent delivery locations (addresses) and edges represent roads connecting them. The weight of an edge signifies the time (in minutes) it takes to travel between two locations.

The delivery service has a fleet of vehicles, each with a limited capacity `C` (number of packages) and a maximum travel time `T` (in minutes) per delivery route.  You are given a list of delivery requests, each specifying a source location, a destination location, and the number of packages to be delivered.

Your goal is to design an algorithm that optimally assigns delivery requests to vehicles and determines the delivery routes, minimizing the total number of vehicles used.

**Input:**

*   `N`: The number of locations in the city (nodes in the graph). Locations are represented by integers from `0` to `N-1`.
*   `graph`: A weighted directed graph represented as a dictionary where keys are source locations and values are dictionaries of destination locations with corresponding travel times (e.g., `graph = {0: {1: 10, 2: 15}, 1: {3: 20}}` means there is a road from location 0 to location 1 taking 10 minutes, and from location 0 to location 2 taking 15 minutes).
*   `requests`: A list of delivery requests, where each request is a tuple `(source, destination, packages)`.
*   `C`: The maximum capacity (number of packages) per vehicle.
*   `T`: The maximum travel time (in minutes) per vehicle route.

**Constraints:**

*   `1 <= N <= 500`
*   `1 <= number of requests <= 1000`
*   `1 <= C <= 50`
*   `1 <= T <= 600`
*   `0 <= source, destination < N` for each request
*   `1 <= packages <= C` for each request
*   The graph is guaranteed to be strongly connected.
*   Assume that loading and unloading times are negligible. The travel time `T` only refers to the time spent travelling between locations.

**Output:**

The minimum number of vehicles required to fulfill all delivery requests.

**Optimization Requirements:**

*   The solution must be efficient enough to handle large inputs within a reasonable time limit (e.g., under 2 minutes).
*   The algorithm should aim to minimize the total number of vehicles used.

**Edge Cases and Considerations:**

*   Some requests may need to be combined into a single route if the vehicle has enough capacity and time.
*   Consider the shortest path between the source and destination for each request.
*   Think about how to handle situations where a vehicle can deliver multiple requests along its route.

**Example:**

```python
N = 5
graph = {
    0: {1: 10, 2: 15},
    1: {3: 20},
    2: {4: 25},
    3: {4: 10},
    4: {}
}
requests = [(0, 1, 5), (2, 3, 10), (1, 4, 15)]
C = 20
T = 60

# One possible solution:
# Vehicle 1: Route 0 -> 1 (5 packages, 10 minutes)
# Vehicle 2: Route 2 -> 3 -> 4 (10 packages, 25+10 = 35 minutes) and 1->4 (15 packages, 20+10=30 minutes)

#Optimal number of vehicles is 2
```
