Okay, here's a challenging Go coding problem designed to be similar to LeetCode Hard. It aims to test a wide range of skills, including algorithm design, data structure usage, and optimization.

### Project Name

```
intercity-express
```

### Question Description

You are tasked with designing a system to manage train routes for a high-speed intercity express rail network. The network consists of a number of cities connected by rail lines. Each rail line has a specific length (in kilometers) and a maximum allowed speed (in km/h).

A train route is a sequence of rail lines connecting a starting city to a destination city.  The goal is to find the *fastest* route between any two given cities, considering both the distance and the speed limits of the rail lines along the route.

However, there's a catch:  Maintaining high-speed rail lines is expensive.  Each rail line has a *maintenance cost per kilometer* associated with it.  Your solution must also be able to compute the *minimum total maintenance cost* for all the rail lines used in the fastest route.

**Input:**

You will be given the following input data:

1.  **Cities:** A list of city names (strings).  City names are unique.

2.  **Rail Lines:** A list of rail lines, where each rail line is defined by:
    *   `start_city`: The city where the rail line begins.
    *   `end_city`: The city where the rail line ends.
    *   `length`: The length of the rail line in kilometers (positive integer).
    *   `max_speed`: The maximum allowed speed on the rail line in km/h (positive integer).
    *   `maintenance_cost_per_km`: The maintenance cost per kilometer for the rail line (positive integer).

3.  **Queries:** A list of queries, where each query consists of:
    *   `start_city`: The starting city for the route.
    *   `destination_city`: The destination city for the route.

**Output:**

For each query, your program should output a tuple:

*   `fastest_time`: The fastest possible travel time (in hours) between the start and destination cities, rounded to two decimal places. If no route exists between the two cities, return `-1.00`.
*   `minimum_maintenance_cost`: The minimum total maintenance cost (integer) for the rail lines used in the fastest route. If no route exists, return `-1`.

**Constraints:**

*   The number of cities will be in the range \[2, 1000].
*   The number of rail lines will be in the range \[1, 5000].
*   The length of each rail line will be in the range \[1, 1000].
*   The maximum speed on each rail line will be in the range \[50, 500].
*   The maintenance cost per kilometer will be in the range \[1, 100].
*   The number of queries will be in the range \[1, 100].
*   City names will consist of alphanumeric characters and spaces, and will not be longer than 50 characters.  City names are case-sensitive.
*   The graph represented by the rail lines may be directed or undirected.  Assume it's directed unless explicitly stated otherwise (e.g., a rail line from A to B does *not* imply a rail line from B to A).
*   Multiple rail lines may exist between the same two cities.
*   The graph may not be fully connected.

**Optimization Requirements:**

*   The solution must be efficient enough to handle large input datasets within a reasonable time limit (e.g., a few seconds).  Consider the algorithmic complexity of your solution.
*   Memory usage should also be considered.  Avoid unnecessary memory allocations.

**Example:**

Let's say you have these cities: "A", "B", "C"

And these rail lines:

*   A -> B, length = 100 km, max_speed = 100 km/h, maintenance_cost_per_km = 1
*   A -> C, length = 200 km, max_speed = 50 km/h, maintenance_cost_per_km = 2
*   B -> C, length = 50 km, max_speed = 100 km/h, maintenance_cost_per_km = 3

Query: A -> C

The fastest route is A -> B -> C.

*   Time A -> B: 100 km / 100 km/h = 1 hour
*   Time B -> C: 50 km / 100 km/h = 0.5 hours
*   Total Time: 1.5 hours

Maintenance Cost:

*   A -> B: 100 km * 1/km = 100
*   B -> C: 50 km * 3/km = 150
*   Total Cost: 250

Output: `(1.50, 250)`

**Judging Criteria:**

Your solution will be judged on:

1.  **Correctness:**  Accurately computing the fastest time and minimum maintenance cost for each query.
2.  **Efficiency:**  Handling large input datasets within the time and memory constraints.
3.  **Code Quality:**  Writing clean, well-documented, and maintainable code.

This problem requires a combination of graph algorithms (finding the shortest path), optimization techniques, and careful handling of floating-point numbers for time calculations.  Good luck!
