## Project Name

`OptimalMerger`

## Question Description

You are tasked with optimizing the merger of multiple sorted data streams into a single, globally sorted data stream. This problem has direct applications in large-scale data processing systems where data is often partitioned and sorted independently before being merged for further analysis.

Specifically, you are given `k` sorted data streams, each represented as an infinite iterator of integers. Your goal is to implement a function that efficiently merges these `k` streams into a single, sorted output stream, also represented as an iterator.

The challenge lies in the following constraints:

1.  **Infinite Streams:** The input streams are conceptually infinite. You can only retrieve the next element from a stream using a `Next()` function (defined below). You cannot access elements at arbitrary positions or determine the length of a stream beforehand.

2.  **Minimizing Comparisons:** The number of comparisons should be minimized. Each call to the `Next()` function of a stream is considered a costly operation.

3.  **Memory Constraints:** The memory usage of your solution should be limited. Storing all elements from all streams is not feasible. You should aim for a solution with a memory footprint that scales sub-linearly with `k`.

4.  **Handling Stalls:** Input streams can "stall," meaning they may temporarily cease providing new integers. A stream that stalls should not block the merger indefinitely. The merger should proceed with the available data from other active streams. A stalled stream may or may not resume providing data later.

5. **Error handling:** The implementation must handle cases where the input streams might contain duplicate values and should still produce a correctly sorted output. In addition, invalid stream inputs (e.g., nil or empty) should be gracefully handled without causing the program to crash.

You need to implement a `MergeKSortedStreams` function with the following signature:

```go
// Stream is an interface representing a sorted data stream.
type Stream interface {
	Next() (int, bool) // Returns the next integer in the stream and a boolean indicating if a value was successfully retrieved.  False indicates end of stream/stall.
}

// MergeKSortedStreams merges k sorted streams into a single sorted stream.
// Returns a Stream.
func MergeKSortedStreams(streams []Stream) Stream {
    // Your implementation here
}
```

Your solution will be evaluated based on:

*   **Correctness:** The output stream must be correctly sorted and contain all elements from all input streams in their proper order.
*   **Efficiency:** The number of calls to the `Next()` function of the input streams should be minimized.
*   **Memory Usage:** The memory footprint of your solution should be small.
*   **Robustness:** Your solution should handle edge cases such as empty input, streams with duplicate values, stalled streams, and streams of varying speeds.
*   **Concurrency Safety:** Your implementation should be concurrent-safe if you are making it concurrent.

This is a challenging problem that requires careful consideration of data structures, algorithms, and concurrency patterns. Think about how to efficiently track the current state of each stream, how to handle stalled streams, and how to minimize the number of comparisons needed to determine the next element in the merged stream.
