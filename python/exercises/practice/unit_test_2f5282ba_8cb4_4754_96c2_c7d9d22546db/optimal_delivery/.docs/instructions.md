Okay, here is a hard-level Python coding problem:

## Project Name

```
Optimal-Delivery-Network
```

## Question Description

A logistics company, "SwiftRoute," aims to optimize its delivery network to minimize delivery times and costs.  They operate in a city represented as a grid, where intersections are nodes and streets connecting them are edges. Each street has a 'congestion score' that represents the average delay experienced while traversing it.

You are given:

1.  `city_map`: A dictionary representing the city's road network. Keys are intersection IDs (integers), and values are lists of tuples. Each tuple represents a street connecting to another intersection and its congestion score: `(neighbor_id, congestion_score)`.  The graph is undirected (if A is a neighbor of B, B is a neighbor of A).
2.  `packages`: A list of tuples. Each tuple represents a package with a source intersection, destination intersection and a priority level: `(source_id, destination_id, priority)`. Priority is a string, either "high", "medium", or "low".
3.  `time_windows`: A dictionary representing delivery time windows for packages, where keys are source/destination pairs (represented as tuples of the form (source\_id, destination\_id)) and values are tuples containing the start and end times (integers) measured from the start of the day. If a source/destination pair does not exist in the time\_windows dictionary, it means that there is no time window constraint for that particular delivery.

Your task is to write a function `optimize_routes(city_map, packages, time_windows)` that returns a dictionary.  The keys of the dictionary are package indices (the index of the package in the `packages` list). The values are lists of intersection IDs representing the *optimal* route for that package.

**Optimality Criteria:**

The route should be chosen based on the following tiered criteria, in order of importance:

1.  **Time Window Compliance:**  If a package has a time window specified in `time_windows`, the delivery *must* occur within that time window (inclusive).  Delivery time is calculated as the sum of congestion scores along the route. If no route can satisfy the time window, the package should be marked as undeliverable and excluded from the returned dictionary.
2.  **Priority:**  High-priority packages should be delivered before medium-priority packages, and medium-priority packages before low-priority packages. This means the sum of congestion scores for the route of a higher priority package must be less than or equal to the sum of congestion scores for any lower priority packages.
3.  **Minimum Congestion:**  Among routes that satisfy the above criteria, choose the route with the lowest total congestion score.
4.  **Shortest Route:** If multiple routes exist with the same total congestion score and priority, return the one with the fewest number of intersections (shortest path).

**Constraints:**

*   The graph represented by `city_map` can be large (up to 1000 nodes and 5000 edges).
*   The number of packages can be significant (up to 100 packages).
*   Congestion scores are non-negative integers.
*   All intersection IDs are non-negative integers.
*   Time windows are valid (start <= end). Time is represented in arbitrary integer units.
*   You must return a dictionary containing ONLY the deliverable packages.
*   If a package is undeliverable because a route to the destination does not exist in the `city_map`, it should be excluded from the returned dictionary.

**Efficiency Requirements:**

Your solution must be efficient enough to handle large city maps and a significant number of packages within a reasonable time limit (e.g., under 60 seconds for a test case with 1000 nodes and 100 packages).  Consider efficient graph search algorithms and data structures.

**Edge Cases:**

*   A package's source and destination intersections might be the same. In this case, the congestion score is 0, and the route consists of only the single intersection ID. The time window must still be satisfied.
*   There might be no path between a package's source and destination.
*   Multiple packages might have the same source and destination.
*   The city map may contain disconnected components.
*   Time windows might be very small, making it difficult to find a conforming route.

Good luck!
