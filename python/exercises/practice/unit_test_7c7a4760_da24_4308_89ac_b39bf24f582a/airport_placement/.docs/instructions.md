## Question: Optimal Airport Placement

### Question Description

You are tasked with optimizing the placement of a new airport within a country to minimize the average travel time for its citizens. The country can be represented as a weighted graph where cities are nodes and the roads connecting them are edges. Each edge has a weight representing the travel time between the two cities.

The country has *N* cities, numbered from 1 to *N*. You are given a list of roads, where each road is represented as a tuple `(city1, city2, travel_time)`. The population of each city is also known.

The new airport can only be built in one of the existing cities.

Your goal is to determine the city where the new airport should be built to minimize the *weighted average travel time* for all citizens in the country to reach the airport. The travel time from a city to the airport is defined as the shortest path between them on the road network.

**Specifically, you need to:**

1.  Calculate the shortest travel time from each city to every other city (all-pairs shortest paths).
2.  For each city, consider it as a potential airport location.
3.  Calculate the weighted average travel time to the airport if it were built in that city. This is calculated as:

    `sum(population[i] * shortest_path[i][airport_city] for i in range(N)) / total_population`

    where:

    *   `population[i]` is the population of city *i*.
    *   `shortest_path[i][airport_city]` is the shortest travel time from city *i* to the potential airport city.
    *   `total_population` is the sum of the populations of all cities.
4.  Return the city number that results in the minimum weighted average travel time. If there are multiple cities with the same minimum weighted average travel time, return the city with the smallest city number.

**Input:**

*   `N`: An integer representing the number of cities.
*   `roads`: A list of tuples, where each tuple `(city1, city2, travel_time)` represents a road between `city1` and `city2` with the given `travel_time`.  Cities are numbered from 1 to N.
*   `population`: A list of integers, where `population[i]` represents the population of city `i+1`.

**Output:**

An integer representing the city number where the airport should be built to minimize the weighted average travel time.

**Constraints:**

*   `1 <= N <= 1000`
*   `0 <= len(roads) <= N * (N - 1) / 2`  (No more than all possible edges)
*   `1 <= city1, city2 <= N`
*   `1 <= travel_time <= 1000`
*   `1 <= population[i] <= 1000`
*   The graph is guaranteed to be connected.
*   There are no self-loops (i.e., `city1 != city2` for all roads).
*   There can be multiple roads between the same pair of cities. Choose the shortest travel time.

**Example:**

```
N = 4
roads = [(1, 2, 5), (1, 3, 9), (2, 3, 3), (2, 4, 6), (3, 4, 4)]
population = [1000, 1500, 800, 1200]

Output: 2
```

**Explanation:**

You need to calculate the all-pairs shortest paths. Then, for each city, calculate the weighted average travel time if the airport was built there.  City 2 will yield the smallest weighted average travel time.

**Note:**

*   Pay close attention to time complexity. Inefficient solutions might time out.
*   Be mindful of potential integer overflow issues (although the constraints mitigate this, it's good practice).
*   Consider appropriate data structures for representing the graph and distances efficiently.
