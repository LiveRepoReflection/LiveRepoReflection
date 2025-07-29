## Question: Optimized Data Stream Median Calculation

**Problem Description:**

You are tasked with designing and implementing a system to efficiently calculate the median of a continuously flowing stream of numerical data. This system will receive a potentially unbounded sequence of integers and must provide the current median value at any given point in time with optimal performance.

**Specific Requirements:**

1.  **Data Input:** The system will receive a stream of integers through a function `ProcessData(int data)`. Each call to this function represents a new data point arriving in the stream.

2.  **Median Calculation:** After each call to `ProcessData(int data)`, the system must be able to return the current median value of all the data points received so far via a function `GetMedian() float64`.

3.  **Performance Constraints:**
    *   `ProcessData(int data)` must have an average time complexity of O(log n), where n is the number of elements seen so far.
    *   `GetMedian()` must have a time complexity of O(1).
    *   Memory usage should be optimized to avoid unnecessary overhead.

4.  **Data Range:** The input integers can be any 64-bit integers (both positive and negative).

5.  **Edge Cases:**
    *   Handle the case where no data has been received yet. In this case, `GetMedian()` should return 0.0.
    *   Handle the case where the number of data points is even. In this case, the median is the average of the two middle elements.

6.  **Scalability:**  The system should be able to handle a very large stream of data (billions of numbers) without significant performance degradation.

7.  **Concurrency (Optional):**  If possible, design the system in a way that allows concurrent calls to `ProcessData(int data)` from multiple goroutines. If concurrency is implemented, ensure proper synchronization to maintain data consistency.

**Constraints:**

*   You must use standard Go libraries only. No external packages are allowed.
*   You must provide a clear explanation of the data structures and algorithms used.
*   Your solution should be well-documented and easy to understand.
*   Consider memory optimization.
*   Consider the trade-offs between different data structures and algorithms.

**Challenge:**

The main challenge lies in maintaining a data structure that allows for efficient insertion of new elements and quick retrieval of the median value.  The optimal solution will involve a clever use of data structures and algorithms to meet the stringent performance requirements, particularly as the data stream grows very large.  Think about how to balance the need for efficient insertion with the need for constant-time median retrieval. Consider using multiple data structures working together.
