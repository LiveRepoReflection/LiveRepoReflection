Okay, here's a challenging Go programming problem designed to be at the LeetCode Hard level.

## Project Name

`ConcurrentMedian`

## Question Description

You are tasked with designing a system that efficiently calculates the running median of a continuous stream of unsorted integers. Your system must handle a large volume of incoming data and provide low-latency access to the current median.

Specifically, you need to implement a `MedianCalculator` struct with the following methods:

*   `NewMedianCalculator() *MedianCalculator`: Constructor that initializes the calculator.

*   `Insert(num int)`:  Inserts a new integer into the stream. This method should be thread-safe.

*   `GetMedian() float64`: Returns the current median of the numbers seen so far. If the number of inserted elements is zero, return 0.0. This method should be thread-safe.

**Constraints and Requirements:**

1.  **Concurrency:** The `Insert` and `GetMedian` methods must be safe for concurrent access from multiple goroutines.  Assume a high rate of concurrent insertions and frequent median requests.

2.  **Performance:**  `Insert` and `GetMedian` should be highly optimized for speed.  Aim for logarithmic time complexity for `Insert` and constant time complexity for `GetMedian` where possible, given the need for concurrency safety. Naive solutions with linear time median calculations will likely time out in test cases with large input sizes.

3.  **Memory:** The system should be memory-efficient.  Avoid storing unnecessary data.

4.  **Large Input:** The system must be able to handle a very large stream of integers (e.g., billions of numbers).

5.  **No External Libraries:** You can use the standard Go library (the `std` package) only. Do not use any external libraries.

6.  **Edge Cases:** Handle the following edge cases correctly:

    *   Empty stream (return 0.0 for the median).
    *   Stream with only one element.
    *   Stream with an even number of elements.
    *   Stream with an odd number of elements.
    *   Duplicate numbers in the stream.

**Evaluation:**

Your solution will be evaluated based on:

*   **Correctness:**  Does it accurately calculate the running median for all test cases?
*   **Performance:**  How quickly does it process insertions and median requests, especially under high concurrency?
*   **Code Quality:**  Is the code well-structured, readable, and maintainable?  Is concurrency handled correctly and efficiently?
*   **Memory Usage:** Does it use memory efficiently, especially with large datasets?

**Hints:**

*   Consider using two heaps (a min-heap and a max-heap) to maintain the numbers seen so far. The max-heap stores the smaller half of the numbers, and the min-heap stores the larger half.
*   Use appropriate synchronization primitives (e.g., `sync.Mutex`, `sync.RWMutex`) to ensure thread safety. Consider the trade-offs between `Mutex` and `RWMutex` for read-heavy vs. write-heavy scenarios.
*   Pay careful attention to edge cases and boundary conditions when balancing the heaps.

This problem requires a good understanding of data structures, algorithms, concurrency, and performance optimization in Go. Good luck!
