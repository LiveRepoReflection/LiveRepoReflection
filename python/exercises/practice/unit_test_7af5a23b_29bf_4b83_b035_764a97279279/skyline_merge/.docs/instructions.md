Okay, here's a challenging coding problem designed to be similar to a LeetCode Hard level question.

**Project Title:** Efficient Skyline Merge

**Problem Description:**

You are given a list of buildings in a 2D city, represented as an array `buildings` where `buildings[i] = [left_i, right_i, height_i]`:

*   `left_i` is the x-coordinate of the left edge of the i-th building.
*   `right_i` is the x-coordinate of the right edge of the i-th building.
*   `height_i` is the height of the i-th building.

The skyline of the city is the outer contour of the silhouette formed by all the buildings when viewed from a distance. The skyline should be represented as a list of key points sorted by their x-coordinate. Each key point is represented as `[x, height]`, where `x` is the x-coordinate and `height` is the height of the skyline at that point.

However, there's a twist: the city is experiencing rapid construction, and new buildings are being added frequently. Your task is to implement a class `SkylineMerger` that efficiently maintains the skyline as buildings are added one by one.

The `SkylineMerger` class should have the following methods:

*   `__init__()`: Initializes an empty skyline.
*   `add_building(left, right, height)`: Adds a new building to the city. The building's information is given as `left`, `right`, and `height`. The skyline should be updated efficiently after adding each building.
*   `get_skyline()`: Returns the current skyline as a list of key points, sorted by their x-coordinate. The skyline should not contain consecutive horizontal lines of the same height.

**Constraints:**

*   `1 <= Number of Buildings <= 10^5`
*   `0 <= left_i < right_i <= 10^9`
*   `0 <= height_i <= 10^9`
*   The number of calls to `add_building` and `get_skyline` can be up to `10^5`.
*   The solution must be efficient in terms of both time and space complexity, especially the `add_building` operation. A naive solution that recalculates the entire skyline after each `add_building` will likely time out.
*   The input `buildings` may be unsorted. Overlapping buildings should be properly handled.

**Optimization Requirements:**

*   The `add_building` operation should have a time complexity better than O(N), where N is the current number of buildings affecting the skyline. Aim for a logarithmic or amortized logarithmic time complexity.
*   The `get_skyline` operation should be reasonably efficient.

**Edge Cases:**

*   Empty city (no buildings).
*   Buildings with the same `left` or `right` coordinates.
*   Buildings completely overlapping other buildings.
*   Buildings contained within other buildings.
*   Adding buildings that don't affect the existing skyline.

**Hint:**

Consider using advanced data structures like segment trees, ordered sets (e.g., using `sortedcontainers` library), or a balanced binary search tree to efficiently manage the skyline and handle overlaps.  Divide and Conquer is also a suitable approach. The challenge lies in efficiently merging the new building into the existing skyline without recalculating everything from scratch each time. Handle the "discontinuity" points carefully.
