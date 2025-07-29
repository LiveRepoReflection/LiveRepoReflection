## Question: Optimal Meeting Point

**Description:**

Imagine a city represented as a weighted, undirected graph where nodes are locations and edges are roads connecting them. Each road has a 'congestion score' representing the difficulty of traversing it. You are given:

*   `n`: The number of locations in the city, numbered from 0 to n-1.
*   `roads`: A list of roads represented as `[location1, location2, congestion_score]`.
*   `meeting_participants`: An array of integers representing the locations of meeting participants. There will be at least one participant.

The goal is to find the *optimal* meeting location in the city to minimize the *maximum* 'congestion cost' any participant has to endure to reach the meeting point.

The 'congestion cost' for a participant is defined as the *sum of congestion scores* along the shortest path from their location to the meeting point. If no path exists, the 'congestion cost' is considered to be Infinity.

The 'optimal' meeting location is the location that minimizes the *maximum* congestion cost among all participants.

**Constraints:**

1.  The city may not be fully connected.
2.  The graph can have cycles.
3.  `1 <= n <= 1000`
4.  `1 <= roads.length <= n * (n - 1) / 2`
5.  `0 <= location1, location2 < n`
6.  `1 <= congestion_score <= 1000`
7.  `1 <= meeting_participants.length <= n`
8.  All elements in `meeting_participants` are unique.
9.  Your solution should have a time complexity better than O(n^3).  Solutions that time out for larger inputs will not be accepted.

**Example:**

Let's say:

```javascript
n = 5;
roads = [[0, 1, 5], [0, 2, 2], [1, 2, 3], [1, 3, 1], [2, 3, 4], [3, 4, 6]];
meeting_participants = [0, 4];
```

*   If the meeting point is location 0, participant 0 has congestion cost 0, and participant 4 has congestion cost of 13 (0 -> 2 -> 3 -> 4, cost: 2+4+6). Max congestion cost = 13.
*   If the meeting point is location 1, participant 0 has congestion cost 5, and participant 4 has congestion cost of 7 (1 -> 3 -> 4, cost: 1+6). Max congestion cost = 7.
*   If the meeting point is location 2, participant 0 has congestion cost 2, and participant 4 has congestion cost of 10 (2 -> 3 -> 4, cost: 4+6). Max congestion cost = 10.
*   If the meeting point is location 3, participant 0 has congestion cost 6 (0 -> 2 -> 3, cost: 2+4), and participant 4 has congestion cost 6. Max congestion cost = 6.
*   If the meeting point is location 4, participant 0 has congestion cost 13 (0 -> 2 -> 3 -> 4, cost: 2+4+6), and participant 4 has congestion cost 0. Max congestion cost = 13.

The optimal meeting location is location 3, as it minimizes the maximum congestion cost (6).

**Return Value:**

Return the location number (0-indexed) of the optimal meeting point. If there are multiple optimal locations, return the smallest location number.
