Okay, here's a challenging Rust coding problem designed to test advanced data structures, algorithmic efficiency, and edge-case handling.

### Project Name

```
distributed-k-means
```

### Question Description

You are tasked with implementing a distributed k-means clustering algorithm.  You'll simulate a simplified distributed environment where data is partitioned across multiple nodes. Your goal is to efficiently calculate the final cluster centroids after a fixed number of iterations.

**Input:**

*   `data: Vec<Vec<f64>>`:  A vector of data points. Each data point is represented as a vector of `f64` values (coordinates). The data represents the combined data across all nodes.
*   `num_nodes: usize`: The number of nodes in the distributed system.  The `data` is assumed to be evenly distributed across these nodes (or as close to even as possible).
*   `k: usize`: The number of clusters to form.
*   `iterations: usize`: The number of k-means iterations to perform.
*   `initial_centroids: Vec<Vec<f64>>`: A vector of initial centroids. These are provided to ensure deterministic test cases. The length of this vector will always be equal to `k`.

**Requirements:**

1.  **Partitioning:**  Simulate the data partitioning by dividing the `data` vector into `num_nodes` roughly equal chunks.  Each chunk represents the data held by a single node.

2.  **Local Computation:** Each simulated node performs k-means clustering on its local data partition. In each iteration, each node:
    *   Assigns each of its data points to the nearest centroid (based on Euclidean distance).
    *   Calculates the new centroid for each cluster based *only* on the data points assigned to it in the local partition.

3.  **Global Aggregation:** After each iteration, the updated centroids from all nodes must be aggregated to compute the *global* centroids.  This is the most challenging part.  To simulate a distributed environment efficiently, you *cannot* simply collect all data points into a single vector and recalculate the centroids from scratch.  Instead, you must efficiently combine the local centroids from each node, considering the number of points each local centroid represents. Think about how to compute a *weighted* average efficiently.

4.  **Convergence (Implicit):**  You will run the k-means algorithm for a fixed number of `iterations`.  You do *not* need to explicitly check for convergence (i.e., when the centroids stop moving significantly).

5.  **Euclidean Distance:**  Use Euclidean distance to calculate the distance between data points and centroids.

6.  **Edge Cases:**
    *   Handle the case where a node has no data points assigned to a particular cluster during an iteration. In this case, the node should contribute *nothing* to the global centroid calculation for that cluster in that iteration.
    *   Handle cases where `k` is larger than the number of data points.
    *   Handle edge cases where `num_nodes` is 0 or 1.
    *   Handle the case where `data` is empty.
    *   Handle the case where dimensions are zero.

7.  **Efficiency:**
    *   The algorithm must be efficient in terms of both time and memory.  Avoid unnecessary data copying.
    *   Consider using appropriate data structures to optimize the distance calculations.
    *   Minimize communication (simulated by data movement) between nodes.

**Output:**

*   `Vec<Vec<f64>>`: A vector of the final `k` cluster centroids after `iterations` iterations.

**Constraints:**

*   `0 <= num_nodes <= 100`
*   `1 <= k <= data.len() if data.len() > 0,  k = 0 if data.len() == 0`
*   `1 <= iterations <= 50`
*   The dimensions of all data points and centroids will be consistent.
*   The data can be multi-dimensional (i.e., each data point can have an arbitrary number of coordinates).

This problem requires a strong understanding of k-means, distributed algorithms, and efficient Rust programming. Good luck!
