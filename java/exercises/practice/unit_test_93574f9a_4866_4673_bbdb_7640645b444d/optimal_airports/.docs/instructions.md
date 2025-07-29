## Question: Optimal Airport Placement for Package Delivery Network

### Question Description

A global logistics company, "SwiftRoute," is designing a new air-based package delivery network. They have identified `N` potential locations for airports across the globe. Each location is represented by its latitude and longitude. SwiftRoute needs to determine the optimal set of `K` airport locations (where `K <= N`) to minimize the maximum delivery time between any two locations in the network.

**Data Representation:**

*   **Locations:** The `N` potential airport locations are represented as a list of coordinate pairs `locations = [(latitude1, longitude1), (latitude2, longitude2), ..., (latitudeN, longitudeN)]`. Latitude and longitude are floating-point numbers.
*   **Delivery Time:** The delivery time between two locations is directly proportional to the great-circle distance (the shortest distance over the earth’s surface) between them. You are given a function `distance(location1, location2)` that efficiently calculates this distance in kilometers.
*   **Airport Network:** An airport network is a subset of `K` locations chosen from the `N` potential locations.
*   **Maximum Delivery Time:** For a given airport network, the maximum delivery time is determined by considering all pairs of locations (potential airport locations, *not* just the K selected ones). For each pair of locations, if *neither* location is an airport, the delivery time between them is considered infinite. If at least one of the two locations is an airport, the delivery time is the shortest path distance between them, considering only the K selected airports as intermediate nodes. Your task is to minimize the *maximum* delivery time across *all* pairs of locations.

**Objective:**

Your task is to write a function `findOptimalAirports(locations, K)` that takes the list of `N` locations and the number `K` of airports to select as input. The function should return a list of the indices (0-based) of the `K` locations that form the optimal airport network, minimizing the maximum delivery time between any two locations. If there are multiple optimal solutions, you can return any one of them.

**Constraints:**

*   `1 <= N <= 100` (Number of potential airport locations)
*   `1 <= K <= min(20, N)` (Number of airports to select)
*   The latitude and longitude values are within the valid range (e.g., -90 to 90 for latitude, -180 to 180 for longitude).
*   Assume the `distance(location1, location2)` function is already implemented and has O(1) time complexity. *You do NOT need to implement the `distance` function.*

**Optimization Requirements:**

*   The solution should be efficient, considering the constraints on `N` and `K`. A brute-force approach of checking all possible combinations of `K` airports might be too slow. Consider using techniques like pruning, heuristics, or approximation algorithms to improve performance.

**Edge Cases:**

*   If `K` is equal to `N`, return a list containing all indices from 0 to `N-1`.
*   If `K` is 1, select the airport location that minimizes the maximum distance to all other locations.
*   Ensure your solution handles cases where some locations are very close to each other (distance close to zero).

**Example:**

```java
// Assume distance(location1, location2) is a predefined function.

List<Pair<Double, Double>> locations = new ArrayList<>();
locations.add(new Pair<>(34.0522, -118.2437)); // Los Angeles
locations.add(new Pair<>(40.7128, -74.0060));  // New York
locations.add(new Pair<>(51.5074, 0.1278));   // London
locations.add(new Pair<>(-33.8688, 151.2093)); // Sydney

int K = 2;

List<Integer> optimalAirports = findOptimalAirports(locations, K);

// Possible output (order may vary): [0, 1] or [0,2] or etc, depending on which combination
// minimizes the maximum delivery time.
```

**Note:** This problem emphasizes algorithmic thinking, data structure selection, and optimization techniques. The core challenge is to efficiently explore the search space of possible airport combinations and determine the optimal one based on the maximum delivery time metric. The problem requires a solid understanding of graph algorithms (shortest path), combinatorial optimization, and careful consideration of edge cases.
