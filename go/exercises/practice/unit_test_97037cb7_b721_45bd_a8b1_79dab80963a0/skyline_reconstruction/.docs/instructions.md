## The Skyline Reconstruction Problem

**Problem Description:**

You are given the blueprint of a city skyline represented by a series of buildings. Each building is a rectangle defined by its left edge coordinate (`Li`), right edge coordinate (`Ri`), and height (`Hi`). The skyline is the outer contour formed by these buildings when viewed from a distance.

Your task is to reconstruct the skyline from the given building blueprints and represent it as a list of key points. A key point is the left endpoint of a horizontal line segment in the skyline representation. Each key point should be represented as a coordinate pair `(x, y)` where `x` is the x-coordinate and `y` is the height of the skyline at that point.

**Input:**

A list of buildings where each building is represented by a tuple `[Li, Ri, Hi]`.

**Constraints:**

*   The number of buildings `n` can be very large (up to 10^5).
*   The coordinates `Li`, `Ri`, and `Hi` are non-negative integers and can be up to 10^9.
*   Buildings may overlap horizontally.
*   Buildings are not necessarily sorted by their left edge.
*   `Li < Ri` for each building.
*   Multiple buildings can start or end at the same x-coordinate.
*   The input list can be empty.

**Output:**

A list of key points representing the skyline. The list should be sorted by x-coordinate.  Consecutive horizontal lines of the same height should be merged.  The last key point should have a height of 0.

**Example:**

**Input:** `[[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]`

**Output:** `[[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]`

**Requirements:**

*   Your solution must be implemented in Go.
*   Your solution should handle a large number of buildings efficiently.  Consider the time and space complexity of your algorithm.  Naive solutions will likely time out.
*   Pay attention to edge cases and ensure your solution is robust.
*   Optimize your solution for both time and space complexity. Solutions with high memory usage may also fail due to memory limits.
*   The output should strictly adhere to the format specified.
*   Ensure the skyline segments are merged correctly, eliminating redundant points.

This problem requires a solid understanding of algorithms and data structures, efficient coding practices, and the ability to handle a variety of edge cases. Good luck!
