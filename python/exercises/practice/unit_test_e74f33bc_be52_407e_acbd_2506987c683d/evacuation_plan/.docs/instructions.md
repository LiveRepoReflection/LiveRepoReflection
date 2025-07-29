## Question: Optimal Evacuation Planning

### Question Description

A city is represented as a weighted, undirected graph where nodes represent locations and edges represent roads connecting them. Each location has a certain number of residents. In the event of a disaster, the city needs to evacuate its residents to a set of designated safe zones.  Each road has a capacity, representing the maximum number of residents that can travel along it within a given time unit.

Your task is to design an optimal evacuation plan that minimizes the total evacuation time for all residents to reach a safe zone.

**Specifically:**

*   **Input:**
    *   `n`: The number of locations in the city (numbered from 0 to n-1).
    *   `roads`: A list of tuples, where each tuple `(u, v, capacity)` represents an undirected road between location `u` and location `v` with a given `capacity`.
    *   `residents`: A list of integers, where `residents[i]` represents the number of residents at location `i`.
    *   `safe_zones`: A list of integers representing the indices of locations designated as safe zones.

*   **Output:**
    *   The minimum time (in time units) required to evacuate all residents to the safe zones. If evacuation is impossible return -1.

**Constraints and Considerations:**

*   The graph can be large (up to 1000 locations).
*   The number of residents at each location can be significant (up to 10<sup>6</sup>).
*   Road capacities can vary.
*   Multiple safe zones can exist.
*   Residents can be evacuated to any of the safe zones.
*   The evacuation time is determined by the maximum flow required to move all residents to the safe zones, considering road capacities.
*   You must provide a solution that is reasonably efficient (consider the time complexity of your algorithm).
*   If it's impossible to evacuate all residents to the safe zones (e.g., due to disconnected components), return -1.
*   Residents can be split and travel via different routes to different safe zones.
*   Assume that each location and safe zone can hold unlimited number of residents.
*   Assume that all the residents can start evacuating simultaneously.
*   The graph is not necessarily complete.
*   The graph can have cycles.
*   The road capacity will always be a non-negative integer.

**Example:**

```
n = 4
roads = [(0, 1, 10), (0, 2, 5), (1, 2, 15), (1, 3, 20), (2, 3, 10)]
residents = [5, 10, 8, 0] # Location 0: 5 residents, Location 1: 10 residents, etc.
safe_zones = [3]

# Expected Output: 1 (All residents can be evacuated in one time unit)
```

**Explanation:**

In the example, all residents need to reach location 3. We can send 5 residents from location 0 to location 1, then to location 3. We can send 8 residents from location 2 to location 1, then to location 3. And send 2 residents from location 2 to location 3. Also send 2 residents from location 1 to location 3. The total residents reach 3 are 20, hence all of them are evacuated.

**Challenge:**  Consider how to efficiently handle large graphs and large numbers of residents while optimizing for evacuation time. You need to find the bottleneck in the evacuation process and optimize around it. A correct but inefficient solution may time out on larger test cases.
