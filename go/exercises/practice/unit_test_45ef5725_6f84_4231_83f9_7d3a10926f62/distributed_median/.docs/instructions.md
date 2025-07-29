Okay, here's a challenging Go programming competition problem:

**Project Name:** `DistributedMedian`

**Question Description:**

You are tasked with designing a system for efficiently calculating the median of a large, distributed stream of integers.  Imagine you have `N` worker nodes, each receiving a subset of the overall integer stream. These worker nodes cannot directly communicate with each other.  A central coordinator node is responsible for collecting information from the workers and determining the global median.

Each worker node has limited memory and can only store a small, fixed-size buffer of `K` integers. When a worker receives a new integer, it must decide whether to keep it in its buffer, potentially replacing an existing integer, or discard it. The goal is for each worker to maintain a representative sample of its local stream within its limited buffer such that the coordinator can accurately estimate the global median.

**Requirements:**

1.  **Worker Node Implementation:** Implement a `WorkerNode` in Go that receives integers one at a time. The `WorkerNode` maintains a buffer of size `K`.  The `WorkerNode` must implement a strategy to decide which elements to keep in its buffer.  Consider strategies like:
    *   Random Replacement: Replace a random element in the buffer.
    *   Reservoir Sampling: A more sophisticated approach to maintain a representative sample.
    *   Min/Max Heaps: Maintain separate heaps for smaller and larger values, potentially discarding extreme values.
    *   Other more optimized strategies.

    The `WorkerNode` should provide a method to return its current buffer contents to the coordinator.

2.  **Coordinator Node Implementation:** Implement a `CoordinatorNode` in Go.  The `CoordinatorNode` receives the buffers from all `N` worker nodes.  It must then calculate an estimate of the global median based on the collected data.

    The Coordinator must be able to handle a large number of nodes and must be as performant as possible when calculating the median.

3.  **Communication:** Assume a simple communication mechanism where each `WorkerNode` periodically sends its buffer to the `CoordinatorNode`. You can simulate this with channels or other suitable Go concurrency primitives. The frequency of sending buffers can be a parameter.

4.  **Edge Cases and Constraints:**

    *   `N` (number of worker nodes) can be very large (e.g., up to 1000).
    *   `K` (buffer size per worker) is relatively small (e.g., 100-1000).  This is the key constraint.
    *   The integer stream is unbounded and may contain duplicates.
    *   The integer stream can be skewed (e.g., more small values than large values).
    *   The Coordinator cannot store the entire stream of integers.
    *   Worker nodes operate independently.
    *   Minimize communication between worker nodes and the coordinator.

5.  **Optimization:**

    *   The primary goal is to minimize the error in the median estimate calculated by the `CoordinatorNode`.
    *   Consider the trade-off between the complexity of the worker node's sampling strategy and the accuracy of the median estimate.
    *   Optimize the coordinator's median calculation for speed.  Consider using efficient sorting or selection algorithms.
    *   Explore ways to reduce the amount of data transmitted from workers to the coordinator.  For example, instead of sending the entire buffer, workers could send summary statistics or quantiles.

6.  **Evaluation:**

    *   Your solution will be evaluated based on the accuracy of the median estimate and the execution time.  You will be provided with a test dataset of integers and the correct median value.
    *   The lower the error in your median calculation and the faster your algorithm the better.

**Write a go program that implements the `WorkerNode` and `CoordinatorNode` as described above, and accurately and efficiently calculates the median of a large distributed data stream.**
