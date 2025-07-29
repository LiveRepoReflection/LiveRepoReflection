## Problem: Concurrent Data Stream Analyzer

You are tasked with designing a highly efficient and concurrent system for analyzing a continuous stream of numerical data. The system must be able to handle a large volume of data points arriving at a high rate and perform real-time calculations on it.

**Specifically, you need to implement a `StreamAnalyzer` struct in Go that satisfies the following requirements:**

1.  **Data Ingestion:** The `StreamAnalyzer` should provide a method `Ingest(data float64)` that accepts a single data point as input. This method must be thread-safe, allowing concurrent ingestion of data from multiple sources.

2.  **Sliding Window:** The `StreamAnalyzer` maintains a sliding window of the last `N` data points ingested.  `N` is specified during the creation of the `StreamAnalyzer`. When a new data point is ingested and the window is full, the oldest data point should be evicted.

3.  **Concurrent Statistics:** The `StreamAnalyzer` should provide methods to calculate the following statistics over the current sliding window:

    *   `Average() float64`: Returns the average of the data points in the window.
    *   `Median() float64`: Returns the median of the data points in the window.
    *   `Percentile(p float64) float64`: Returns the p-th percentile of the data points in the window. `p` is a float between 0.0 and 1.0 (inclusive).  For example, `Percentile(0.5)` should return the median.

    These methods must be thread-safe, allowing multiple clients to query the statistics concurrently.

4.  **Zero Allocation Queries:** The `Average()`, `Median()`, and `Percentile()` methods must strive to minimize memory allocations. Allocations are expensive and can severely impact the performance of a high-throughput system.  Ideally, these methods should operate on the underlying data structure without creating intermediate copies unless absolutely necessary.

5.  **High Throughput:** The system should be optimized for high ingestion and query throughput.  Consider the trade-offs between different data structures and algorithms to achieve the best possible performance.

6.  **Error Handling:** The `Percentile()` method should return an error if the input `p` is not within the range [0.0, 1.0]. The `Average()`, `Median()`, and `Percentile()` methods should return a value (e.g., 0.0) and no error if the sliding window is empty.

7.  **Fixed Size:** The sliding window size `N` is fixed at the time of `StreamAnalyzer` creation and cannot be changed afterwards.

**Constraints:**

*   `N` (sliding window size) will be a positive integer up to 1,000,000.
*   The data points ingested will be floating-point numbers.
*   The system must be designed to handle a very high rate of data ingestion and concurrent statistical queries.
*   Minimizing memory allocations during queries is crucial.
*   Correctness and thread-safety are paramount.

**Considerations:**

*   Think about the appropriate data structure to store the sliding window.  Arrays, linked lists, and specialized data structures like circular buffers each have different performance characteristics.
*   Consider using appropriate synchronization primitives (e.g., mutexes, read-write locks) to ensure thread-safety.
*   Explore efficient algorithms for calculating the median and percentiles.  Sorting the entire window on each query is likely too slow.  Consider using approximation algorithms or specialized data structures.
*   Think about the trade-offs between memory usage and performance.
*   Consider the impact of garbage collection on the system's performance.

This problem requires a deep understanding of concurrent programming in Go, data structures, and algorithms. Success will depend on choosing the right tools and techniques to achieve high throughput, low latency, and minimal memory allocations. Good luck!
