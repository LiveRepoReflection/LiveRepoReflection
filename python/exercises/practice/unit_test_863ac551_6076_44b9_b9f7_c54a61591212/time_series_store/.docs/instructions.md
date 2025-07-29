Okay, I'm ready to craft a challenging programming competition problem. Here it is:

**Problem Title:** Time-Based Key-Value Store with Aggregation

**Problem Description:**

Design a time-based key-value store system with the ability to efficiently aggregate values within specified time ranges.  This system will be used to store and analyze sensor data collected over time.

The system must support the following operations:

1.  **`set(key, value, timestamp)`:** Stores the given `value` associated with the `key` at the specified `timestamp`. `key` is a string, `value` is an integer, and `timestamp` is a positive integer representing seconds since the epoch.  Multiple values can be stored for the same key at different timestamps.  Timestamps for the same key are strictly increasing.

2.  **`get(key, timestamp)`:** Retrieves the value associated with the given `key` at or before the specified `timestamp`. If no value exists for the given `key` at or before the given `timestamp`, return -1.  If multiple values exist, return the value with the largest timestamp that is less than or equal to the target `timestamp`.

3.  **`aggregate(key, startTime, endTime, aggregationType)`:**  Calculates an aggregated value for the given `key` across the time range `[startTime, endTime]` (inclusive).  `startTime` and `endTime` are positive integers representing seconds since the epoch.  `aggregationType` is a string specifying the type of aggregation to perform.  The supported aggregation types are:

    *   `"SUM"`: Calculate the sum of all values associated with the `key` within the time range.

    *   `"AVG"`: Calculate the average of all values associated with the `key` within the time range. If no values exist within the range, return 0.

    *   `"MAX"`: Find the maximum value associated with the `key` within the time range. If no values exist within the range, return -1.

    *   `"MIN"`: Find the minimum value associated with the `key` within the time range. If no values exist within the range, return -1.

**Constraints:**

*   `1 <= timestamp <= 10^9`
*   `1 <= startTime <= endTime <= 10^9`
*   Number of calls to `set`, `get`, and `aggregate` combined: up to `10^5`
*   Number of distinct keys: up to `10^4`
*   Values are integers in the range: `-10^9 <= value <= 10^9`
*   Memory usage is limited to 256 MB.
*   The system should be optimized for both time and space efficiency, especially for the `aggregate` operation. Inefficient solutions that lead to timeouts will not pass the test cases.

**Example:**

```
TimeBasedKeyValueStore store = new TimeBasedKeyValueStore();
store.set("sensor1", 10, 1);
store.set("sensor1", 20, 5);
store.set("sensor1", 30, 10);

store.get("sensor1", 3);  // Returns 10
store.get("sensor1", 6);  // Returns 20
store.get("sensor1", 12); // Returns 30
store.get("sensor2", 5);  // Returns -1 (key not found)

store.aggregate("sensor1", 2, 8, "SUM"); // Returns 20 + 20 = 40
store.aggregate("sensor1", 2, 8, "AVG"); // Returns (10 + 20) / 2 = 15
store.aggregate("sensor1", 2, 8, "MAX"); // Returns 20
store.aggregate("sensor1", 2, 8, "MIN"); // Returns 10
store.aggregate("sensor1", 11, 15, "SUM"); // Returns 30
store.aggregate("sensor1", 1, 100, "AVG"); // Returns (10 + 20 + 30) / 3 = 20
store.aggregate("sensor2", 1, 10, "SUM"); // Return 0
store.aggregate("sensor2", 1, 10, "MAX"); // Return -1
```

**Judging Criteria:**

Solutions will be judged on:

*   Correctness (passing all test cases)
*   Time complexity (efficient implementations are crucial)
*   Space complexity (within the memory limit)
*   Code clarity and readability

**Hints and Considerations:**

*   Consider using appropriate data structures to store the key-value pairs and their associated timestamps for efficient retrieval and aggregation. A naive approach might lead to timeouts.
*   Think about how to efficiently perform range queries for the aggregation operation. Binary search or similar techniques might be helpful.
*   Pay attention to edge cases, such as empty ranges, missing keys, and division by zero when calculating the average.
*   The strictly increasing timestamp constraint for each key can be leveraged for optimization.
*   Consider trade-offs between memory usage and query performance.
*   The optimal solution should aim for O(log N) time complexity for `get` and `aggregate` operations, where N is the number of timestamps for a given key.

This problem requires a solid understanding of data structures, algorithms, and optimization techniques, making it suitable for a high-level programming competition. Good luck!
