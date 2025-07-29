## Project Name

`OptimalMeetingPoint`

## Question Description

You are tasked with designing a system to determine the optimal meeting point for a group of friends. The friends are scattered across a city represented as a weighted graph. Each vertex in the graph represents a location, and each edge represents a road connecting two locations with an associated travel time (weight).

Given the graph of the city and the locations of each friend in the city, find the location in the city that minimizes the *maximum* travel time any friend has to travel to reach the meeting point.

**Input:**

*   `graph`: A weighted undirected graph represented as an adjacency list. The keys of the adjacency list are the location IDs (integers), and the values are lists of `Edge` structs/objects. An `Edge` connects the location to a neighboring location and includes the travel time (`weight`).
    ```go
    type Edge struct {
        To     int // Destination location ID
        Weight int // Travel time
    }
    ```
*   `friendLocations`: A slice of integers, where each integer represents the location ID of a friend.

**Output:**

*   The location ID (integer) of the optimal meeting point. If the `graph` is empty or `friendLocations` is empty, return -1. If no meeting point can be determined (e.g., graph is disconnected), return -1.

**Constraints:**

*   The graph can be large (up to 10,000 locations and 50,000 roads).
*   The travel times (weights) are positive integers.
*   The number of friends can be up to 100.
*   Your solution should be efficient enough to handle large graphs within a reasonable time limit (e.g., under 10 seconds).
*   The graph might not be fully connected.
*   Friend locations are guaranteed to be present in the graph.
*   Handle the case where the graph contains negative-weight cycles appropriately (return -1 if detected).

**Optimization Requirements:**

*   Minimize the time complexity of your solution. Brute-force approaches will likely time out.
*   Consider using appropriate data structures and algorithms to optimize performance.

**Edge Cases:**

*   Empty graph.
*   Empty list of friend locations.
*   Graph is disconnected.
*   A single friend.
*   All friends are at the same location.
*   Negative-weight cycles in the graph.

**Example:**

```
graph := map[int][]Edge{
    1: {{To: 2, Weight: 10}, {To: 3, Weight: 15}},
    2: {{To: 1, Weight: 10}, {To: 4, Weight: 12}},
    3: {{To: 1, Weight: 15}, {To: 4, Weight: 20}},
    4: {{To: 2, Weight: 12}, {To: 3, Weight: 20}},
}
friendLocations := []int{1, 4}

OptimalMeetingPoint(graph, friendLocations) // Should return 2 (or 3, as they are equivalent)
```

**Explanation for the Example:**

*   If the meeting point is 1: Friend at 1 travels 0, friend at 4 travels 20 (to 3) or 12 (to 2), max travel time is 20.
*   If the meeting point is 2: Friend at 1 travels 10, friend at 4 travels 12, max travel time is 12.
*   If the meeting point is 3: Friend at 1 travels 15, friend at 4 travels 20, max travel time is 20.
*   If the meeting point is 4: Friend at 1 travels 15 (to 3) or 10+12 = 22 (to 2), friend at 4 travels 0, max travel time is 22.

Therefore, locations 2 or 3 are optimal with a maximum travel time of 12.

**Clarification:**

The goal is to minimize the *maximum* travel time among all friends. This is different from minimizing the sum of travel times, which would be a different problem (and a different optimal meeting point).
