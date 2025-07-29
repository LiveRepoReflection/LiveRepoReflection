Okay, here's a challenging problem designed for a high-level programming competition, focusing on algorithmic efficiency, advanced data structures, and real-world constraints.

### Project Name

```
Distributed-Median-Tracker
```

### Question Description

You are tasked with designing a system for tracking the median of a stream of numbers distributed across multiple data centers. Imagine a large e-commerce company monitoring the prices of a particular product across various vendors located in different geographic regions. Each vendor reports their price updates to their nearest data center. Your system needs to efficiently maintain a global median price, even with frequent updates and potential data center outages.

Specifically, you need to implement the following functionality:

1.  **`add_data_center(data_center_id)`:**  Adds a new data center to the system. Each data center is uniquely identified by `data_center_id` (a string).

2.  **`report_price(data_center_id, price)`:** A vendor reports a price update to a specific data center. `price` is a non-negative integer.  Assume price reports arrive frequently.

3.  **`remove_data_center(data_center_id)`:** Simulates a data center outage. All price data from this data center should be removed from the global median calculation.

4.  **`get_global_median()`:** Returns the current global median of all prices across all active data centers. If the total number of prices is even, return the lower of the two middle values. If no prices exist return -1.

**Constraints:**

*   The number of data centers can be large (up to 100,000).
*   The number of price reports per data center can also be very large (potentially millions).
*   Price values are non-negative integers in the range \[0, 1,000,000,000].
*   `get_global_median()` needs to be efficient, as it might be called frequently to monitor price trends. Aim for a solution with significantly better time complexity than re-calculating the median from scratch every time.
*   Data center outages should be handled gracefully and efficiently. The impact on `get_global_median()` call should be minimal.
*   Memory usage is a consideration. Avoid storing all individual prices in a single massive list. Consider using data structures that allow for efficient updates and median calculation without excessive memory overhead.
*   The system should be designed to be resilient. Data center outages shouldn't corrupt the global median tracking.
*   Assume that the system is single-threaded, meaning you don't need to worry about thread safety.

**Requirements:**

*   Provide a Python implementation that meets the above functionality and constraints.
*   Prioritize correctness and efficiency.
*   Clearly explain the data structures and algorithms used, justifying the choices made considering the constraints. Describe the time and space complexity of each operation (`add_data_center`, `report_price`, `remove_data_center`, `get_global_median`).
*   Consider multiple valid approaches, outlining the trade-offs between them (e.g., memory vs. speed, ease of implementation vs. performance).
*   Think about possible edge cases and how your solution handles them (e.g., empty data, all data in one data center, frequent data center additions/removals).
*   Assume test cases will include large datasets and frequent operations, so performance is critical.

This problem requires careful consideration of data structures and algorithms to achieve the required performance and scalability.  Good luck!
