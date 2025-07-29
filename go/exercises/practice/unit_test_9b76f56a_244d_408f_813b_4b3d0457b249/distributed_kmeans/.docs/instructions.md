## Project Name

```
distributed-k-means
```

## Question Description

You are tasked with implementing a distributed k-means clustering algorithm. You will simulate a system with multiple worker nodes and a central coordinator. The goal is to efficiently cluster a large dataset distributed across these worker nodes.

**Scenario:** Imagine a large sensor network where each sensor node collects data points (e.g., temperature, humidity). These data points need to be clustered to identify patterns and anomalies. Due to the sheer volume of data, processing it on a single machine is not feasible. Thus, you need a distributed solution.

**Input:**

1.  **`num_workers` (int):** The number of worker nodes in the distributed system.
2.  **`k` (int):** The number of clusters to find.  `k > 0`.
3.  **`data_points` (\[][]float64):** A slice of slices, representing the entire dataset. Each inner slice represents a data point with numerical features. The length of all inner slices (the number of features) must be consistent. This dataset is conceptually divided among the worker nodes, but for simplicity of testing, you'll receive the whole dataset.
4.  **`initial_centroids` (\[][]float64):** A slice of slices representing the initial centroids for the k clusters. The length of `initial_centroids` must be equal to `k`. Each centroid must have the same number of features as each data point.

**Distribution:**

Your algorithm should simulate distributing the `data_points` evenly among the `num_workers`. Note that the amount of data points may not be divisible by the number of workers so the last worker may have less data than other workers.

**K-Means Algorithm:**

1.  **Initialization:** The coordinator initializes `k` centroids (provided as `initial_centroids`).

2.  **Assignment (Worker Nodes):** Each worker node receives a subset of the data points and the current centroids.  Each worker then assigns each of its data points to the nearest centroid based on Euclidean distance. Each worker sends its local cluster assignments (data point index and cluster index) and the sum of data points that are assigned to each cluster with the number of data points in that cluster to the coordinator.

3.  **Update (Coordinator):** The coordinator receives the cluster assignments and the cluster sums from all worker nodes. The coordinator recomputes the centroids by averaging all the data points assigned to each cluster across all workers.

4.  **Convergence:** Repeat steps 2 and 3 until the centroids converge. Convergence can be determined by measuring the change in centroids' positions between iterations. If the maximum change in any centroid's position is below a threshold (e.g., 0.0001), the algorithm has converged.

**Output:**

Return a slice of slices (\[][]float64) representing the final centroids after the k-means algorithm has converged.

**Constraints:**

*   **Efficiency:** The algorithm should be reasonably efficient. Consider the time complexity of your distance calculations and centroid updates.  Avoid unnecessary data copying.  The number of iterations to convergence should be minimized.
*   **Handling Empty Clusters:** Your algorithm must handle the case where a cluster has no data points assigned to it during an iteration.  A simple approach is to re-initialize that centroid to a random data point from the entire dataset.
*   **Euclidean Distance:** Use Euclidean distance to determine the nearest centroid.
*   **Maximum Iterations:** To prevent infinite loops, implement a maximum iteration count (e.g., 100). If the algorithm doesn't converge within the maximum iterations, return the centroids from the last iteration.
*   **Data Size:** The dataset can be very large (e.g., millions of data points). Design your solution to handle such large datasets without exceeding memory limits.
*   **Floating Point Precision:** Be aware of potential floating-point precision issues when summing and averaging large numbers of data points.

**Bonus:**

*   Implement a method to choose initial centroids that are less likely to result in empty clusters or slow convergence (e.g., k-means++).
*   Explore different convergence criteria.
*   Add logging or debugging output to track the progress of the algorithm.
*   Implement a mechanism to detect and handle outliers in the data.
