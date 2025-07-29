Okay, here's a challenging C++ coding problem designed to be LeetCode Hard level, focusing on efficiency, data structures, and edge case handling.

**Problem Title:  Optimal Meeting Point**

**Problem Description:**

Imagine a city represented as a 2D grid.  Each cell in the grid can either be empty (represented by 0) or contain a building (represented by 1).  You are given a grid `grid` of size `m x n` representing this city.

The people living in these buildings want to schedule a meeting. To minimize travel time, they want to find the *optimal* meeting point. The optimal meeting point is the cell in the grid that minimizes the *total Manhattan distance* to all buildings.

The Manhattan distance between two cells (r1, c1) and (r2, c2) is calculated as `|r1 - r2| + |c1 - c2|`.

Your task is to write a function that takes the `grid` as input and returns the *minimum total Manhattan distance* to reach any building from the optimal meeting point.  If no meeting point can be found (e.g., the grid is empty or contains no buildings), return -1.

**Constraints and Requirements:**

1.  `m == grid.length`
2.  `n == grid[i].length`
3.  `1 <= m, n <= 200`
4.  `grid[i][j]` is either 0 or 1.
5.  There will be at least one building in the grid.
6.  Your solution must achieve a time complexity better than O(m\*n\*number of buildings). An O(m\*n) or better solution is desirable.  Solutions with higher time complexity will likely time out in the hidden test cases.
7.  Space complexity should be optimized. Avoid storing intermediate results unnecessarily.
8.  Handle edge cases gracefully:
    *   Empty grid.
    *   Grid with no buildings.
    *   Grid where all cells are buildings.
9. The grid can be very sparse (few buildings) or very dense (many buildings). Your solution should perform well in both scenarios.
10. Integer overflow might be a concern when calculating the sum of Manhattan distances.

**Example:**

```
Input: grid = [[1,0,2,0,1],[0,0,0,0,0],[0,0,1,0,0]]
Output: 8

Explanation:
There are three people living at (0,0), (0,4), and (2,2):
The point (0,2) is an ideal meeting point, as the total travel distance
of 2 + 2 + 2 = 6 is minimal. So return 6.
```

**Clarifications:**

*   You are looking for the *cell* that minimizes the total Manhattan distance, not necessarily a cell that contains a building.  The meeting point can be any cell (i, j) within the grid boundaries.
*   You must return the *minimum total distance*, not the coordinates of the meeting point itself.
*   The problem is designed to force you to think about optimizing your algorithm.  A naive brute-force solution will not pass.

This problem requires careful consideration of data structures, algorithms, and optimization techniques to achieve the required performance. Good luck!
