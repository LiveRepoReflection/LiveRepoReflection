Okay, here's a challenging Java coding problem designed to be at the LeetCode Hard level, incorporating elements of advanced data structures, optimization, edge cases, and real-world scenarios.

## Project Name

`ScalableEventAggregator`

## Question Description

You are tasked with designing and implementing a scalable event aggregator system. This system receives a continuous stream of events from various sources, each event having a timestamp (in milliseconds since the epoch) and a type.  The system needs to efficiently answer queries about the number of events of a specific type within a given time range.

**Event Structure:**

```java
class Event {
    long timestamp; // Milliseconds since epoch
    String type;     // Event type (e.g., "login", "purchase", "click")

    public Event(long timestamp, String type) {
        this.timestamp = timestamp;
        this.type = type;
    }
}
```

**Requirements:**

1.  **`EventAggregator` Interface:**

    ```java
    interface EventAggregator {
        void recordEvent(Event event);
        long getEventCount(String eventType, long startTime, long endTime);
    }
    ```

    *   `recordEvent(Event event)`: Records a new event into the system.  This method will be called frequently and concurrently from multiple threads.
    *   `getEventCount(String eventType, long startTime, long endTime)`: Returns the number of events of the specified `eventType` that occurred within the time range `[startTime, endTime]` (inclusive).  This method will also be called frequently.

2.  **Scalability and Performance:**

    *   The system should handle a large volume of events (millions per second) and a high query rate efficiently.  Minimize latency for both `recordEvent` and `getEventCount` operations.
    *   Optimize for read operations (i.e., `getEventCount`). Read operations are expected more often than write operations.
    *   Consider the potential for data skew (some event types might be much more frequent than others).
    *   The system should be designed to scale horizontally (i.e., can be distributed across multiple machines).  While you don't need to implement the distributed aspect, your design should be conducive to it.

3.  **Memory Management:**

    *   The system should efficiently manage memory usage.  Events older than a specified retention period (e.g., 24 hours) should be automatically purged to prevent the system from running out of memory.  This retention period should be configurable.

4.  **Concurrency:**

    *   The implementation must be thread-safe.  Multiple threads will concurrently call `recordEvent` and `getEventCount`.

5.  **Time Complexity:**

    *   Aim for a time complexity of O(log N) or better for `getEventCount` where N is the number of events within the retention period, for a single event type.
    *   `recordEvent` should ideally be O(1) or O(log N).

6.  **Edge Cases:**

    *   Handle invalid `startTime` and `endTime` values (e.g., `startTime > endTime`).
    *   Handle cases where the requested `eventType` does not exist.
    *   Handle empty event streams gracefully.

**Constraints:**

*   Implement the `EventAggregator` interface.
*   Assume events arrive in arbitrary order (not necessarily sorted by timestamp).
*   You *cannot* use external databases or caching services (e.g., Redis, Memcached).  You must implement the data storage and retrieval mechanisms yourself, using in-memory data structures.

**Bonus Challenges:**

*   Implement a mechanism to persist the aggregated data to disk periodically for recovery purposes.
*   Implement a more sophisticated purging strategy that prioritizes retaining more recent events.
*   Implement support for complex queries (e.g., count events matching multiple types within a time range).

This problem is designed to assess your understanding of data structures, algorithms, concurrency, and system design principles.  Good luck!
