## Question: Scalable Event Stream Aggregation

### Problem Description

You are tasked with designing a system to efficiently aggregate real-time event streams. Imagine a massive online game where millions of players are constantly generating events (e.g., item purchases, monster kills, player interactions). Your system needs to process these events and provide aggregated statistics within strict latency constraints.

Specifically, you will receive a stream of event records. Each event record consists of:

*   `timestamp`: A 64-bit integer representing the Unix timestamp (seconds since epoch) when the event occurred.
*   `event_type`: A string representing the type of event (e.g., "item_purchase", "monster_kill", "player_interaction").
*   `user_id`: A 32-bit integer representing the ID of the user who triggered the event.
*   `value`: A 64-bit floating-point number representing a numerical value associated with the event (e.g., the cost of an item, the damage dealt).

Your system must implement a method `aggregate_events` that takes a list of these event records as input. The `aggregate_events` method must calculate and return the following statistics for each `event_type` within a sliding time window:

*   `count`: The total number of events of this type within the window.
*   `sum`: The sum of the `value` field for all events of this type within the window.
*   `average`: The average of the `value` field for all events of this type within the window (sum / count).
*   `min`: The minimum `value` for all events of this type within the window. If no events of that type exist in the window, return infinity.
*   `max`: The maximum `value` for all events of this type within the window. If no events of that type exist in the window, return negative infinity.

The sliding time window is defined by a `window_size` parameter (in seconds). Only events whose `timestamp` falls within the current window (relative to the latest timestamp seen so far) should be included in the aggregation. The window slides forward as new events arrive, and older events expire.

### Input

A list of event records, where each record is a tuple/struct containing `timestamp`, `event_type`, `user_id`, and `value`.

### Output

A dictionary/map where the keys are the `event_type` strings and the values are tuples/structs containing the calculated `count`, `sum`, `average`, `min`, and `max` statistics for that event type within the sliding time window.

### Constraints

*   **Scale:** The system must handle a very high volume of events (millions per second).
*   **Latency:** The `aggregate_events` method must return results within a tight latency budget (e.g., under 10 milliseconds).
*   **Memory:** Memory usage should be minimized, especially when handling a large number of event types.
*   **Time Window:** The `window_size` can be large (e.g., several hours or days).
*   **Real-time:** The system should be designed to process events as they arrive, without requiring batch processing.
*   **Order:** Events may not arrive in strictly increasing timestamp order. You must account for out-of-order events within the window.
*   The number of distinct `event_type` values can be very large.
*   The input list of events is not sorted by timestamp.

### Optimization Requirements

*   Minimize computational complexity to achieve the required latency.
*   Optimize memory usage to handle a large number of event types and a large time window.
*   Consider using appropriate data structures and algorithms for efficient event storage and retrieval.

### Edge Cases

*   Empty input list of events.
*   `window_size` is zero or negative.
*   Events with identical timestamps.
*   Events with extremely large or small `value` fields.
*   A large number of distinct `event_type` values, where some event types are much more frequent than others.

### Example

```python
events = [
    (1678886400, "item_purchase", 123, 10.0),
    (1678886401, "monster_kill", 456, 20.0),
    (1678886402, "item_purchase", 123, 15.0),
    (1678886403, "player_interaction", 789, 0.0),
    (1678886404, "monster_kill", 456, 25.0),
    (1678886405, "item_purchase", 123, 12.0),
]
window_size = 5

result = aggregate_events(events, window_size)

# Expected Result (order may vary, floating point comparison should be within reasonable tolerance):
# {
#     "item_purchase": {
#         "count": 3,
#         "sum": 37.0,
#         "average": 12.333333,
#         "min": 10.0,
#         "max": 15.0
#     },
#     "monster_kill": {
#         "count": 2,
#         "sum": 45.0,
#         "average": 22.5,
#         "min": 20.0,
#         "max": 25.0
#     },
#     "player_interaction": {
#         "count": 1,
#         "sum": 0.0,
#         "average": 0.0,
#         "min": 0.0,
#         "max": 0.0
#     }
# }

```

### System Design Considerations

Think about how your solution could be scaled horizontally to handle even larger event streams. Could your solution be easily distributed across multiple machines? What trade-offs would you need to make?
