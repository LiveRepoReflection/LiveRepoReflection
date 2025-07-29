## Project Name

```
distributed-k-means
```

## Question Description

You are tasked with implementing a distributed version of the k-means clustering algorithm.  Imagine you have a massive dataset of user activity logs stored across multiple machines (nodes) in a distributed system.  Each node holds a subset of the data. Your goal is to efficiently compute the k-means clusters for this entire dataset without centralizing the data on a single machine.

**Input:**

*   **`data_fragments`:** A list of lists. Each inner list represents a data fragment residing on a different node. Each element within a data fragment is a data point represented as a list of numerical features (e.g., `[[1.0, 2.0], [1.5, 1.8], [5.0, 8.0]]`). The data points are multi-dimensional.  Assume that each data fragment contains at least one data point, however, data fragments can have different lengths.
*   **`k`:** An integer representing the desired number of clusters. `k` > 0 and `k` <= total number of data points across all data fragments.
*   **`initial_centroids`:** A list of lists, where each inner list represents the initial coordinates of a centroid. The length of the list should equal `k`, and the dimensionality of each centroid should match the dimensionality of the data points. Assume that the initial centroids are distinct.

**Output:**

*   A list of lists, where each inner list represents the coordinates of the final centroids after convergence.  The length of the list should equal `k`, and the dimensionality of each centroid should match the dimensionality of the data points.

**Algorithm:**

Implement the following distributed k-means algorithm:

1.  **Initialization:** You are given `initial_centroids`.
2.  **Assignment (Distributed):** Each node (represented by a data fragment in `data_fragments`) independently assigns each of its data points to the nearest centroid based on Euclidean distance. Each node outputs a list of (centroid_index, data_point) pairs.
3.  **Aggregation and Centroid Update (Centralized):**  Collect all (centroid_index, data_point) pairs from all nodes. For each centroid, calculate the mean of all data points assigned to it.  These means become the new centroids.
4.  **Convergence Check:**  Calculate the sum of squared distances between the old centroids and the new centroids. If this sum is below a given threshold (`convergence_threshold`), the algorithm has converged.
5.  **Iteration:** Repeat steps 2-4 until convergence or a maximum number of iterations (`max_iterations`) is reached.

**Constraints:**

*   You **must** implement the distributed assignment step.  You cannot simply concatenate all data fragments into a single list.
*   You **must** use Euclidean distance as the distance metric.
*   You **must** implement the convergence check as described above.
*   The dimensionality of the data points and centroids can be arbitrary (but consistent).
*   Data points can be any numerical value, including negative numbers and decimals.
*   Optimize for performance. The algorithm should be efficient, especially when dealing with a large number of data points and a large number of nodes. Think about the computational complexity of your solution, and how to reduce the amount of work/data that needs to be communicated/computed.
*   Handle edge cases gracefully.

**Error Handling:**

*   If `k` is not a positive integer or if `k` is greater than the total number of data points, raise a `ValueError`.
*   If the dimensionality of the data points and centroids do not match, raise a `ValueError`.
*   If the `data_fragments` list is empty, raise a `ValueError`.

**Parameters:**

*   `convergence_threshold = 1e-6`
*   `max_iterations = 100`
