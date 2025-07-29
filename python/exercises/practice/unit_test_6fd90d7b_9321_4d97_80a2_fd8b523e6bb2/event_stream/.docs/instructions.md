## Question Title: Scalable Event Stream Aggregation

### Question Description

You are building a real-time analytics platform to process a massive stream of events. Each event is represented as a tuple: `(timestamp, entity_id, event_type, value)`.

*   `timestamp`: A Unix timestamp (integer, seconds since epoch) representing when the event occurred.
*   `entity_id`: A string representing the entity that generated the event (e.g., user ID, device ID).
*   `event_type`: A string representing the type of event (e.g., "click", "purchase", "login").
*   `value`: An integer value associated with the event (e.g., purchase amount, click count).

Your task is to design and implement a system that can efficiently aggregate these events and answer the following queries in real-time:

**Query:** Given a time range (`start_time`, `end_time`), a set of `entity_ids`, and a specific `event_type`, calculate the sum of the `value` for all events that fall within the time range, belong to one of the specified entities, and match the specified event type.

**Constraints:**

1.  **High Throughput:** The system must be able to handle a very high volume of incoming events (millions per second).
2.  **Low Latency:** Queries should be answered as quickly as possible (ideally, within milliseconds).
3.  **Scalability:** The system should be able to scale horizontally to handle increasing data volume and query load.
4.  **Memory Efficiency:** Minimize memory usage, as the system will be deployed on resource-constrained servers.
5.  **Time Range Overlap:** Time ranges in queries can overlap.
6.  **Entity ID Cardinality:** The number of unique `entity_ids` can be very large.
7.  **Immutable Data:** The event stream is append-only. You do not need to support updates or deletes.
8.  **Precision:** The aggregation must be accurate. Floating-point approximations are not allowed, particularly when summing a very large number of small integer values.
9.  **Out-of-Order Events:** Events may not arrive in perfect timestamp order. Implement a reasonable strategy to handle slight timestamp variations (e.g., within a small window).
10. **Real-world data distribution:** Event timestamps and entity IDs may not be uniformly distributed. Some entities or time periods may have significantly more events than others. The solution should perform well under skewed distributions.

**Input:**

*   A stream of events represented as a list of tuples `(timestamp, entity_id, event_type, value)`. Assume the stream is virtually infinite and events are arriving continuously.
*   A list of queries, where each query is a tuple `(start_time, end_time, entity_ids, event_type)`.

**Output:**

*   For each query, return the sum of the `value` for all events that match the query criteria.

**Example:**

```python
events = [
    (1678886400, "user1", "click", 1),
    (1678886401, "user2", "purchase", 100),
    (1678886402, "user1", "click", 1),
    (1678886403, "user3", "login", 1),
    (1678886404, "user2", "click", 1),
    (1678886405, "user1", "purchase", 50),
]

queries = [
    (1678886400, 1678886402, ["user1"], "click"),  # Expected: 2
    (1678886400, 1678886405, ["user2"], "purchase"), # Expected: 100
    (1678886403, 1678886404, ["user1", "user2"], "click"), # Expected: 1
    (1678886400, 1678886405, ["user1", "user2", "user3"], "login") # Expected: 1
]
```

**Grading Criteria:**

*   **Correctness:** The solution must produce the correct aggregation results for all queries.
*   **Efficiency:** The solution must meet the performance requirements for high throughput and low latency.
*   **Scalability:** The solution must be able to scale horizontally to handle large data volumes.
*   **Memory Usage:** The solution should minimize memory consumption.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.

This problem challenges the solver to consider various data structures and algorithms for efficient data storage and retrieval, indexing strategies for fast query processing, and techniques for handling real-world data distributions and out-of-order events. The scalability and performance requirements push the solver to think about system design aspects and optimization strategies.
