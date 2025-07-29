Okay, here's a challenging Go programming problem description, designed to be similar in difficulty to a LeetCode Hard problem.

### Project Name

```
DistributedMedianStream
```

### Question Description

You are tasked with designing a system to efficiently calculate the running median of a stream of integers arriving from multiple distributed sources.  Imagine a sensor network continuously reporting temperature readings, and you want to track the median temperature in real-time.

Specifically, you need to implement a `DistributedMedianStream` struct with the following capabilities:

1.  **`AddValue(sourceID string, value int)`:** This method receives a new integer `value` from a specific `sourceID`. The `sourceID` is a string that uniquely identifies the data source. There can be many different sources, each sending potentially unsorted values.

2.  **`GetMedian() float64`:** This method calculates and returns the current median of *all* integers received so far from *all* sources.

**Requirements and Constraints:**

*   **Real-time Performance:**  The `GetMedian()` operation should be as efficient as possible, as it will be called frequently.  Avoid re-sorting the entire data set on every call.  Aim for a time complexity significantly better than O(n log n) for `GetMedian()`, where 'n' is the total number of values received.
*   **Scalability:** The system must be able to handle a large number of `sourceID`s (up to 100,000) and a large number of total values (up to 10,000,000). Memory usage should be considered.
*   **Distribution:**  The data is inherently distributed across different sources. Your solution should gracefully handle this distributed nature.
*   **Edge Cases:**
    *   Handle the case where no values have been received yet.  Return 0.0 in this case.
    *   Handle duplicate values correctly when calculating the median.
    *   Handle both even and odd numbers of total values.
*   **Concurrency:**  The `AddValue()` method can be called concurrently from multiple goroutines, each representing a different data source. Ensure thread-safety.
*   **Accuracy:** The returned median should be accurate to at least 6 decimal places.

**Considerations:**

*   Think carefully about the data structures you choose.  A naive approach of storing all values in a single slice and sorting it repeatedly will not meet the performance requirements.
*   Consider using multiple data structures in combination to achieve the desired performance. For example, you might use a combination of heaps, trees, or other data structures.
*   Focus on minimizing the work required by the `GetMedian()` operation, even if it means doing more work in the `AddValue()` operation.
*   The relative frequency of `AddValue` vs `GetMedian` will vary and is unknown.

**Scoring:**

Solutions will be evaluated based on:

1.  **Correctness:**  Does the solution correctly calculate the running median for all test cases, including edge cases?
2.  **Performance:**  How quickly does the solution calculate the median, especially as the number of values and sources increases?
3.  **Memory Usage:**  How much memory does the solution consume, especially as the number of values and sources increases?
4.  **Code Quality:**  Is the code well-structured, readable, and maintainable? Is it thread-safe?

This problem requires a good understanding of data structures, algorithms, and concurrency in Go. Good luck!
