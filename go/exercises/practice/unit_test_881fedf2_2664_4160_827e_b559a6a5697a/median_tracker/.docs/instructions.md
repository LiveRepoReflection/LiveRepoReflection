Okay, here's a challenging coding problem designed for a high-level programming competition, keeping your constraints in mind.

## Project Name

```
Distributed-Median-Tracker
```

## Question Description

You are tasked with designing a system to track the running median of a stream of integers arriving from multiple distributed sources.  Imagine a financial trading platform where various exchanges are constantly streaming price data. You need to efficiently calculate the median price across all exchanges in real-time.

Your system must handle the following:

*   **Multiple Streams:** Data arrives as a continuous stream of integers from `N` different sources (simulated as channels in Go).  Each source can send integers at different and unpredictable rates.
*   **Dynamic Number of Sources:** The number of data sources (`N`) is provided at startup and remains constant.
*   **Real-time Median Tracking:**  After receiving each new integer from any source, the system must be able to efficiently return the *current* median of all integers received so far, across all streams.
*   **Scalability:** The solution must be scalable to handle a large number of sources (`N` up to 1000) and a large number of integers per source (up to 1,000,000).
*   **Memory Efficiency:**  Minimize the memory footprint of your solution. Storing all integers in a single list is not acceptable for large datasets.
*   **Numerical Stability:**  Handle potentially large integer values without causing overflow or precision issues when calculating the median. Consider the range of the integers.
*   **Concurrent Safety:** Given that multiple sources will be sending data concurrently, your solution must be thread-safe and avoid race conditions.
*   **Performance Requirements:**  The `GetMedian` operation must be highly performant.  Aim for a time complexity significantly better than O(n log n) for each new element, where n is the total number of integers received so far.  O(log n) per element insertion for the core data structure should be achievable.

The system should implement the following interface:

```go
type MedianTracker interface {
    AddValue(sourceID int, value int) // Adds a value from a specific source. sourceID is in [0, N-1]
    GetMedian() float64                // Returns the current median of all values received so far.
}

func NewMedianTracker(numSources int) MedianTracker // Constructor, takes the number of sources as input.

```

**Constraints:**

*   `1 <= N <= 1000` (Number of data sources)
*   Each data source will send at most 1,000,000 integers.
*   `-10^9 <= value <= 10^9` (Range of integer values)
*   The median should be calculated with a precision of at least 6 decimal places.
*   Assume the sources are numbered from 0 to N-1.
*   Implement concurrent-safe operations.

**Example Scenario:**

Let's say `N = 2`. Two sources are sending integers.

*   Source 0 sends: `1, 5, 2`
*   Source 1 sends: `3, 4`

The `GetMedian` calls after each received value should return:

*   After receiving 1: `1.0`
*   After receiving 3: `2.0`
*   After receiving 5: `3.0`
*   After receiving 4: `3.5`
*   After receiving 2: `3.0`

**Evaluation:**

Your solution will be evaluated based on:

*   **Correctness:**  Accurately calculating the median for all possible input sequences.
*   **Performance:**  Speed of the `AddValue` and `GetMedian` operations, especially for large datasets.
*   **Memory Usage:**  Efficiency in memory utilization.
*   **Code Quality:**  Readability, maintainability, and adherence to Go coding conventions.
*   **Concurrency Safety:** Correctly handling concurrent access from multiple sources.

This problem requires a good understanding of data structures, algorithms, and concurrency in Go. Think about using efficient data structures like heaps or self-balancing binary search trees to maintain the sorted order of the incoming data and efficiently calculate the median. Good luck!
