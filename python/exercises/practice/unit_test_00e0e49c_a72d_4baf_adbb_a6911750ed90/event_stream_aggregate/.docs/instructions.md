Okay, here's a challenging Python coding problem, designed to be at the LeetCode Hard level.

**Problem Title: Scalable Event Stream Aggregation**

**Problem Description:**

You are tasked with designing and implementing a system to aggregate real-time event data. Imagine a high-volume stream of events coming from various sources (e.g., IoT devices, web servers, financial trading platforms). Each event contains a timestamp (in milliseconds since the epoch), an event type (a string), and a numerical value.

Your system needs to efficiently answer the following types of queries in real-time:

1.  **Total Value:** Given a time window (start timestamp, end timestamp) and an event type, calculate the sum of all numerical values for events of that type within the specified time window.

2.  **Average Value:** Given a time window (start timestamp, end timestamp) and an event type, calculate the average of all numerical values for events of that type within the specified time window.

3.  **Top K Events:** Given a time window (start timestamp, end timestamp), return the K event types with the highest total numerical value within the time window, sorted in descending order of total value.

**Input:**

Your code will interact with a stream of events and a stream of queries.

*   **Event Stream:** Events arrive continuously. Each event is a tuple: `(timestamp, event_type, value)`.
    *   `timestamp`: Integer representing milliseconds since the epoch.
    *   `event_type`: String representing the event type.
    *   `value`: Float representing the numerical value associated with the event.

*   **Query Stream:** Queries arrive intermittently. Each query is a tuple: `(query_type, start_timestamp, end_timestamp, event_type=None, K=None)`.
    *   `query_type`: String, either "total", "average", or "topk".
    *   `start_timestamp`: Integer representing the start of the time window (inclusive).
    *   `end_timestamp`: Integer representing the end of the time window (inclusive).
    *   `event_type`: String (optional, only for "total" and "average" queries).
    *   `K`: Integer (optional, only for "topk" queries).

**Constraints:**

*   **High Volume:** The event stream can have millions of events per second.
*   **Real-Time:** Queries must be answered with minimal latency (ideally within milliseconds).
*   **Memory Constraints:** The system should not consume excessive memory, especially as the event stream grows over time.  The amount of memory used should be sublinear to the total number of events received.
*   **Out-of-Order Events:** Events may arrive out of order (timestamps are not strictly increasing).  However, assume the out-of-order events are within a reasonable tolerance compared to the current time (e.g., no more than a few minutes "behind").
*   **Non-Uniform Event Types:** The number of distinct event types can be very large (potentially hundreds of thousands or millions).
*   **Time Window Size:** Time windows in queries can vary significantly, from milliseconds to hours or even days.
*   Assume `start_timestamp` is always less than or equal to `end_timestamp`.
*   K will always be positive and reasonable small, i.e., less than 100.

**Output:**

For each query, return the result:

*   **"total"**:  A float representing the sum of values.
*   **"average"**: A float representing the average of values.  Return 0.0 if no events match the query criteria.
*   **"topk"**: A list of tuples `[(event_type1, total_value1), (event_type2, total_value2), ...]`, sorted in descending order of `total_value`, representing the top K event types with the highest total value within the time window. If fewer than K event types exist, return all existing event types.

**Example:**

```python
# Example Usage (Illustrative)

# Assume a hypothetical EventStreamAggregator class

aggregator = EventStreamAggregator()

# Simulate event stream
aggregator.process_event(1678886400000, "temperature", 25.5)
aggregator.process_event(1678886400005, "humidity", 60.2)
aggregator.process_event(1678886400010, "temperature", 26.0)
aggregator.process_event(1678886400015, "pressure", 1013.25)
aggregator.process_event(1678886400020, "temperature", 26.5)
aggregator.process_event(1678886400025, "humidity", 61.5)

# Simulate query stream
total_temp = aggregator.handle_query("total", 1678886400000, 1678886400020, "temperature") # Returns approximately 78.0 (25.5 + 26.0 + 26.5)
print(f"Total Temperature: {total_temp}")

avg_temp = aggregator.handle_query("average", 1678886400000, 1678886400020, "temperature") # Returns approximately 26.0
print(f"Average Temperature: {avg_temp}")

top_2 = aggregator.handle_query("topk", 1678886400000, 1678886400025, K=2) # Might return [("temperature", 78.0), ("humidity", 121.7)] or [("humidity", 121.7), ("temperature", 78.0)] depending on internal implementation details
print(f"Top 2 Event Types: {top_2}")
```

**Requirements:**

*   Implement a class `EventStreamAggregator` with the following methods:
    *   `__init__(self)`: Initializes the aggregator.
    *   `process_event(self, timestamp, event_type, value)`: Processes an incoming event.
    *   `handle_query(self, query_type, start_timestamp, end_timestamp, event_type=None, K=None)`: Handles an incoming query and returns the result.

This problem requires careful consideration of data structures, algorithms, and system design to meet the performance constraints. Good luck!
