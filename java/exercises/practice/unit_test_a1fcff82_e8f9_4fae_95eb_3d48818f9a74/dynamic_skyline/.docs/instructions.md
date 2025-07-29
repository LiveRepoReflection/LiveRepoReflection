Okay, here's a challenging Java coding problem, designed to test advanced data structures, algorithmic efficiency, and handling of complex constraints.

**Problem Title:**  Dynamic Skyline Aggregation

**Problem Description:**

Imagine a city planning application that needs to efficiently manage and query the skyline of a dynamic city.  The city is represented as a 2D plane where buildings are rectangular and axis-aligned. Each building is defined by its left x-coordinate (`left`), right x-coordinate (`right`), and height (`height`).  The skyline is the outline of the city when viewed from a distance.  It can be represented as a list of key points, where each key point `(x, y)` indicates that the skyline changes its height at position `x` to height `y`.

Your task is to implement a system that dynamically maintains the city skyline as buildings are added and removed. The system must efficiently support the following operations:

1.  **`addBuilding(left, right, height)`:** Adds a new building to the city.  It is guaranteed that `left < right` and `height > 0`. Buildings may overlap.

2.  **`removeBuilding(left, right, height)`:** Removes a building from the city.  It is guaranteed that a building with the given `left`, `right`, and `height` exists in the city. Buildings may overlap. Multiple buildings can share the same dimensions.

3.  **`getSkyline()`:** Returns the current skyline as a list of key points `List<List<Integer>> skyline`. Each key point is a list of two integers `[x, y]`.  The skyline should be sorted in ascending order of `x`.  Consecutive horizontal lines in the skyline should be merged (e.g., `[[2, 3], [4, 3], [7, 3]]` should be simplified to `[[2, 3], [7, 3]]`). The skyline should start at x = -infinity and end at x = +infinity, both with height of 0 if the first or last buildings don't start/end at -/+infinity.

**Constraints:**

*   `1 <= Number of addBuilding operations <= 10^5`
*   `1 <= Number of removeBuilding operations <= 10^5`
*   `1 <= Number of getSkyline operations <= 10^2`
*   `0 <= left < right <= 10^9`
*   `1 <= height <= 10^9`
*   The total number of buildings added will not exceed 10^5 at any given time.
*   `addBuilding` and `removeBuilding` operations are interleaved.
*   The `getSkyline` operation must be efficient.  Naive solutions that recompute the skyline from scratch for each query will likely time out.

**Optimization Requirements:**

*   The `addBuilding` and `removeBuilding` operations should be optimized to minimize the impact on subsequent `getSkyline` queries.
*   The `getSkyline` operation itself should be efficient, aiming for a sublinear time complexity if possible.
*   Consider the memory footprint of your data structures, especially when dealing with a large number of buildings.

**Edge Cases:**

*   Buildings with identical coordinates and heights.
*   Buildings completely contained within other buildings.
*   Buildings partially overlapping with other buildings.
*   Empty city (no buildings).
*   Removing a building that doesn't exist (should throw exception).

**Considerations for Evaluation:**

*   **Correctness:**  The skyline should accurately reflect the current state of the city after each operation.
*   **Efficiency:** The time complexity of `addBuilding`, `removeBuilding`, and `getSkyline` will be a major factor. Solutions with quadratic or higher complexity will likely not pass.
*   **Code Quality:**  The code should be well-structured, readable, and maintainable.
*   **Error Handling:**  The code should gracefully handle edge cases and invalid inputs.

This problem requires a solid understanding of data structures like segment trees, balanced trees (e.g., TreeMap), or priority queues, combined with careful algorithmic design to achieve the required performance. Good luck!
