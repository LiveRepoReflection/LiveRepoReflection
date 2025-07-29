## Question: Scalable Median Tracking

**Problem Description:**

Design and implement a data structure, `MedianTracker`, that efficiently tracks the median of a dynamically changing stream of numbers. The `MedianTracker` must support the following operations:

*   `insert(num: i64)`: Inserts a new number `num` into the stream.
*   `remove(num: i64)`: Remove an existing number `num` from the stream. If the `num` does not exist, do nothing. If there are multiple instances of num, remove **only one** of them.
*   `get_median() -> Option<f64>`: Returns the current median of the stream. If the stream is empty, return `None`.

**Constraints:**

1.  The stream can contain duplicate numbers.
2.  The stream can contain a very large number of elements (up to 10^9).
3.  `insert` and `remove` operations should be optimized for speed. Achieving `O(log n)` time complexity is highly desirable, where `n` is the number of elements in the stream. `get_median` should be O(1).
4.  Memory usage should be carefully considered, especially for large streams.
5.  Assume all incoming numbers (`num`) are within the range of `i64`.

**Optimization Challenge:**

*   Consider the impact of duplicate numbers on performance. Your solution should handle duplicates efficiently.

**Edge Cases:**

*   Empty stream.
*   Stream with only one element.
*   Stream with an even number of elements.
*   Stream with an odd number of elements.
*   Insertion of duplicate numbers.
*   Removal of non-existent numbers.
*   Removal of duplicate numbers (removing only one instance).

**Real-world Scenario:**

This problem is relevant to real-time data analysis, where you need to track the median of a constantly changing dataset, such as:

*   Tracking the median price of a stock in a high-frequency trading system.
*   Monitoring the median latency of a network service.
*   Analyzing the median age of users in a rapidly growing online platform.
