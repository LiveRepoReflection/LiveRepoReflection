## Question: Optimal Meeting Point

### Description

Imagine a city represented as a weighted, undirected graph. Each node in the graph represents a location, and each edge represents a road connecting two locations with a specific travel time.

A group of friends are scattered across this city and want to meet at a single location.  They want to choose the meeting point that minimizes the *maximum* travel time any one of them has to endure.  In other words, they want to minimize the time it takes for the friend who has to travel the *longest* distance to reach the meeting point. This is a typical minimax problem.

**Specifics:**

You are given:

*   `n`: The number of locations in the city, numbered from 0 to `n-1`.
*   `roads`: A list of roads represented as `int[][] roads`, where each `roads[i] = [u, v, w]` indicates an undirected road between location `u` and location `v` with a travel time of `w`.
*   `friends`: An array of integers representing the locations where the friends are currently located.

Your task is to write a function that finds the optimal meeting point (location) that minimizes the *maximum* travel time for any friend to reach that location.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= roads.length <= n * (n - 1) / 2`
*   `roads[i].length == 3`
*   `0 <= u, v < n`
*   `1 <= w <= 1000`
*   There are no self-loops or duplicate edges in `roads`.
*   `1 <= friends.length <= n`
*   `0 <= friends[i] < n`
*   All `friends[i]` are unique.

**Optimization Requirement:**

The solution must be efficient enough to handle larger graphs within reasonable time limits.  Consider using appropriate graph algorithms and data structures for optimal performance.  Solutions with high time complexity may not pass all test cases.

**Edge Cases:**

*   The graph may not be fully connected.
*   The number of friends could be small or large relative to the number of locations.
*   The optimal meeting point might be the location of one of the friends.

**Output:**

Return the *minimum possible maximum* travel time for any friend to reach the optimal meeting point. If no meeting point is possible (e.g., the graph is disconnected and friends are in different components), return `-1`.
