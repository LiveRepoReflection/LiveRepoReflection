## Question: Scalable Event Stream Aggregation

### Problem Description

You are tasked with building a scalable system for aggregating real-time event streams. Imagine you are working for a large social media company that needs to analyze user activity (e.g., posts, likes, comments) across various regions. The volume of data is massive, and the system must be able to handle sudden spikes in traffic while maintaining accuracy and low latency.

Specifically, you need to implement a service that receives a continuous stream of events, each containing the following information:

*   `event_type`: A string representing the type of event (e.g., "post", "like", "comment").
*   `region`: A string representing the geographical region where the event occurred (e.g., "US", "EU", "Asia").
*   `timestamp`: An integer representing the Unix timestamp of the event.

Your service should provide an API to query the aggregated event counts for a specific `event_type` and `region` within a given time window. The time window is defined by a `start_timestamp` and `end_timestamp` (inclusive).

**Requirements:**

1.  **Scalability:** The system must be able to handle a high volume of incoming events (millions per second) and a large number of concurrent queries.
2.  **Low Latency:** Queries should return results with minimal delay (ideally within milliseconds).
3.  **Accuracy:** The aggregated event counts must be accurate.
4.  **Fault Tolerance:** The system should be resilient to failures. If a node goes down, the system should continue to operate without significant data loss.
5.  **Efficient Storage:** The storage mechanism should be efficient and minimize the amount of memory and disk space used.
6.  **Time-based aggregation:** Must be able to aggregate data within the time window

**Constraints:**

*   The number of distinct `event_type` values is relatively small (e.g., < 100).
*   The number of distinct `region` values is also relatively small (e.g., < 100).
*   The time window for queries can vary, ranging from a few seconds to several days.
*   You have limited resources (memory and CPU) on each node in the system.
*   The timestamps arrive in roughly ascending order, but may not be perfectly ordered.

**Your Task:**

Design and implement a system that efficiently aggregates and queries event streams according to the specifications above. You need to provide the following functionalities:

*   `process_event(event_type, region, timestamp)`: This function is called for each incoming event.
*   `query_event_count(event_type, region, start_timestamp, end_timestamp)`: This function returns the number of events of the specified `event_type` and `region` that occurred within the given time window.

**Considerations:**

*   Choose appropriate data structures and algorithms to optimize for both ingestion and query performance.
*   Think about how to distribute the data across multiple nodes to achieve scalability and fault tolerance.
*   Consider using techniques like sharding, caching, and approximate counting to improve performance.
*   Address the challenges of out-of-order timestamps and potential data loss.

This is a system design problem as much as it is a coding problem. You should consider different architectural approaches and justify your design choices. The focus will be on the efficiency and scalability of your solution. A well-documented and commented code is expected.
