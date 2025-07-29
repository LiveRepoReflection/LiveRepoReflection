## Question: Optimal Meeting Point

**Problem Description:**

Imagine a city represented as a weighted, undirected graph. The nodes represent locations, and the edges represent roads connecting those locations, with weights representing the time it takes to travel between them.

A group of software engineers lives in this city. They want to hold a meeting at a location that minimizes the *total travel time* for everyone. The total travel time is the sum of the shortest path distances from each engineer's home to the meeting point.

You are given:

*   `n`: The number of locations in the city (numbered from 0 to n-1).
*   `roads`: A list of roads represented as triplets `[location1, location2, travel_time]`.
*   `engineer_locations`: A list of integers representing the locations where the engineers live. There may be duplicates if multiple engineers live at the same location.

Your task is to find the location that minimizes the total travel time for all engineers to attend the meeting.

**Constraints:**

1.  The graph is connected.
2.  `1 <= n <= 200`
3.  `0 <= location1, location2 < n`
4.  `1 <= travel_time <= 1000`
5.  `1 <= len(engineer_locations) <= n`
6.  Engineers can choose to meet at any location, including locations where no one lives.
7.  If multiple locations result in the same minimum total travel time, return the location with the smallest index.

**Optimization Requirement:**

Your solution should be efficient enough to handle graphs with up to 200 nodes and a reasonable number of edges (e.g., O(n^3) is acceptable, but significantly slower approaches might time out). Consider using appropriate algorithms to compute shortest paths.

**Edge Cases:**

*   Ensure your solution handles cases where all engineers live in the same location.
*   Ensure your solution handles cases with very sparse or very dense graphs.
*   Ensure your solution handles potential integer overflow when calculating total travel time (consider using `long` if necessary).

**Example:**

```java
n = 4
roads = [[0, 1, 2], [0, 2, 5], [1, 2, 1], [1, 3, 10], [2, 3, 1]]
engineer_locations = [0, 2, 3]

// Optimal meeting point: Location 2
// Total travel time:
// - Engineer 0: shortest path to 2 is 5
// - Engineer 2: shortest path to 2 is 0
// - Engineer 3: shortest path to 2 is 1
// Total: 5 + 0 + 1 = 6

//Meeting point 1:
// Total travel time:
// - Engineer 0: shortest path to 1 is 2
// - Engineer 2: shortest path to 1 is 1
// - Engineer 3: shortest path to 1 is 11 (2+1+10 = 13 or 5+1+1 = 7 or 1+10=11)
// Total: 2+1+11 = 14

//Meeting point 0:
// Total travel time:
// - Engineer 0: shortest path to 0 is 0
// - Engineer 2: shortest path to 0 is 5
// - Engineer 3: shortest path to 0 is 6
// Total: 0+5+6 = 11

//Meeting point 3:
// Total travel time:
// - Engineer 0: shortest path to 3 is 6
// - Engineer 2: shortest path to 3 is 1
// - Engineer 3: shortest path to 3 is 0
// Total: 6+1+0 = 7

// Output: 2
```

Good luck!
