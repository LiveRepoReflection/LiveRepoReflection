## Project Name

```
SkylineOptimizer
```

## Question Description

Imagine you are tasked with optimizing the skyline of a city. The city is represented as a series of buildings placed along a horizontal axis. Each building is a rectangle defined by its left edge `Li`, right edge `Ri`, and height `Hi`.

You are given a list of buildings represented as tuples: `(Li, Ri, Hi)`.

Your task is to implement an algorithm that outputs the skyline formed by these buildings. The skyline should be represented as a list of key points, where each key point is a tuple `(x, y)` indicating the x-coordinate and the height at that point. The skyline should be the *outer contour* of the buildings when viewed from a distance.

**Constraints and Optimizations:**

1.  **Input Size:** The number of buildings can be very large (up to 10^5). A naive O(n^2) solution will likely time out.
2.  **Merge Overlapping Skylines:** The core challenge lies in efficiently merging skylines formed by different subsets of buildings. Think about how to divide and conquer this problem.
3.  **Horizontal Line Segments:** The skyline should not contain consecutive horizontal line segments of the same height. For example, `[(1, 5), (3, 5), (5, 5)]` should be simplified to `[(1, 5), (5, 5)]`.
4.  **Sorted Output:** The output list of key points must be sorted by their x-coordinate.
5.  **No Redundant Points:** The output should not contain any redundant key points. A point is redundant if it doesn't contribute to the shape of the skyline. Example, `[(1,3), (2,3), (3,4)]` should not keep (2,3).
6.  **Edge Cases:** Handle edge cases gracefully, such as an empty list of buildings, buildings with zero height, and buildings that are completely contained within other buildings.
7.  **Efficiency:** Aim for a solution with a time complexity of O(n log n), where n is the number of buildings.

**Example:**

**Input:** `[(2, 9, 10), (3, 7, 15), (5, 12, 12), (15, 20, 10), (19, 24, 8)]`

**Output:** `[(2, 10), (3, 15), (7, 12), (12, 0), (15, 10), (20, 8), (24, 0)]`

**Explanation:**

The input represents five buildings. The output represents the skyline formed by these buildings, as a series of key points. Notice how overlapping segments are merged and redundant points are removed.

**Your Task:**

Write a function `get_skyline(buildings)` that takes a list of building tuples as input and returns a list of key point tuples representing the skyline.
