Okay, here's a challenging C++ coding problem designed to be similar to a LeetCode Hard level question, incorporating advanced data structures, optimization, and real-world scenarios.

**Problem Title:** Dynamic Skyline Maintenance

**Problem Description:**

Imagine you are building a city simulation. The city is represented as a 2D plane. Buildings are added to the city dynamically. Each building is a rectangle defined by its left coordinate `L`, right coordinate `R`, and height `H`.  These buildings are axis-aligned.

Your task is to maintain the **skyline** of the city as buildings are added. The skyline is a list of critical points `(x, y)` where the height of the skyline changes.  Specifically, the skyline should be represented as a sorted list of `(x, y)` pairs, where `x` represents the x-coordinate and `y` represents the height of the skyline at that point.

**Input:**

The input consists of a series of operations. Each operation is one of the following:

1.  **`add L R H`**: Adds a new building with left coordinate `L`, right coordinate `R`, and height `H`.  It is guaranteed that `L < R` and `H > 0`.
2.  **`query`**:  Returns the current skyline as a list of `(x, y)` pairs, sorted by `x` coordinate.

The input will be provided via standard input.  The first line will indicate the number of operations, `N`.  The following `N` lines will each represent an operation, as described above.

**Constraints:**

*   `1 <= N <= 10^5` (Number of operations)
*   `0 <= L, R <= 10^9` (Building coordinates)
*   `1 <= H <= 10^9` (Building height)
*   The number of buildings added will not exceed `10^4`.
*   All input values are integers.
*   The skyline must be stored in a sorted manner by x-coordinate.
*   You must maintain the skyline efficiently, such that each `add` and `query` operation can be performed in a reasonable amount of time.  Solutions with O(N^2) time complexity (where N is the number of buildings) will likely time out.

**Output:**

For each `query` operation, print the skyline to standard output. The skyline should be formatted as a space-separated list of `(x, y)` pairs, where `x` and `y` are integers.  For example:

`(1, 10) (5, 0) (7, 15) (12, 0)`

**Example Input:**

```
5
add 1 5 10
add 7 12 15
query
add 5 7 12
query
```

**Example Output:**

```
(1, 10) (5, 0) (7, 15) (12, 0)
(1, 10) (5, 12) (7, 15) (12, 0)
```

**Challenge:**

The main challenge lies in efficiently maintaining the skyline as buildings are added. A naive approach of recomputing the entire skyline after each building addition will likely be too slow.  You will need to explore data structures and algorithms that allow for efficient updates and queries. Consider how to handle overlapping buildings and how to merge skyline segments effectively.  The optimization requirement is crucial for passing all test cases within the time limit.
