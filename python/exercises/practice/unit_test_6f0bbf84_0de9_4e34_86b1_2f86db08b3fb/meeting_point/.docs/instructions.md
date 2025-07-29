## Project Name

`OptimalMeetingPoint`

## Question Description

Imagine a city represented as a weighted undirected graph where nodes are locations and edges represent roads with associated travel times. You are tasked with finding the optimal meeting point for a group of friends, minimizing the maximum travel time any friend has to endure to reach the meeting point.

Each friend resides at a specific location (node) in the city. You are given:

*   `n`: The number of locations (nodes) in the city, numbered from `0` to `n-1`.
*   `edges`: A list of tuples representing the roads in the city. Each tuple `(u, v, w)` signifies an undirected road between location `u` and location `v` with a travel time of `w`.
*   `friends`: A list of integers representing the locations (nodes) where each friend lives.

Your task is to determine the location (node) that minimizes the *maximum* travel time from any friend's location to the meeting point.  In other words, if `dist(friend_i, meeting_point)` is the shortest distance between `friend_i` and the `meeting_point`, you want to find the `meeting_point` that minimizes `max(dist(friend_1, meeting_point), dist(friend_2, meeting_point), ..., dist(friend_k, meeting_point))`, where `k` is the number of friends.

If multiple locations achieve the same minimum maximum travel time, return the location with the smallest node number.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= edges.length <= n * (n - 1) / 2` (The graph can be dense)
*   `edges[i].length == 3`
*   `0 <= u, v < n`
*   `1 <= w <= 1000`
*   The graph is connected.
*   `1 <= friends.length <= n`
*   All values in `friends` are unique and within the range `[0, n-1]`.

**Optimization Requirements:**

Your solution should be efficient enough to handle graphs with up to 1000 nodes and a reasonable number of edges (up to n*(n-1)/2). Inefficient solutions might time out.

**Edge Cases:**

*   Consider the case where all friends live in the same location.
*   Consider the case where the optimal meeting point is the location of one of the friends.
*   Consider cases with varying graph densities.

**Example:**

```
n = 4
edges = [[0, 1, 1], [0, 2, 5], [1, 2, 2], [1, 3, 1]]
friends = [0, 3]

Optimal meeting point: 1
Explanation:
- Distance from friend 0 to 0: 0, to 1: 1, to 2: 5, to 3: 2
- Distance from friend 3 to 0: 2, to 1: 1, to 2: 3, to 3: 0

- If meeting point is 0: max(0, 2) = 2
- If meeting point is 1: max(1, 1) = 1
- If meeting point is 2: max(5, 3) = 5
- If meeting point is 3: max(2, 0) = 2

Therefore, 1 is the optimal meeting point.
```
