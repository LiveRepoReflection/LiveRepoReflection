## Project Name

`Distributed Event Stream Aggregator`

## Question Description

You are tasked with designing and implementing a distributed system to aggregate events from a high-volume stream. Imagine you are building the backend for a large-scale IoT platform, where millions of devices are constantly sending data. Each device generates "events," and you need to compute real-time aggregates (e.g., average, sum, count, min, max) over these events across all devices within a specified time window.

**Specifically, you need to implement the following:**

1.  **Event Ingestion:** Design an efficient mechanism to ingest events from multiple producers (simulated IoT devices). Each event will be a JSON object with the following structure:

```json
{
  "device_id": "unique_device_identifier",
  "timestamp": 1678886400, // Unix timestamp in seconds
  "metric_name": "temperature",
  "metric_value": 25.5
}
```

2.  **Distributed Aggregation:** Implement a distributed aggregation algorithm to compute aggregates over a sliding time window. The time window is defined in seconds. You need to support the following aggregate functions:

    *   `count`: Number of events within the window.
    *   `sum`: Sum of `metric_value` for events within the window.
    *   `avg`: Average of `metric_value` for events within the window.
    *   `min`: Minimum `metric_value` for events within the window.
    *   `max`: Maximum `metric_value` for events within the window.

    The system should be horizontally scalable, meaning adding more worker nodes should increase processing capacity.

3.  **Querying:** Provide an API endpoint to query the aggregates for a specific `metric_name` and time window. The API should return the results in JSON format:

```json
{
  "metric_name": "temperature",
  "time_window_start": 1678886400,
  "time_window_end": 1678886460,
  "count": 1000,
  "sum": 25500.0,
  "avg": 25.5,
  "min": 10.0,
  "max": 40.0
}
```

**Constraints and Requirements:**

*   **High Throughput:** The system must be able to handle a large volume of incoming events (millions per second).
*   **Low Latency:** Queries for aggregates should return results quickly (within milliseconds).
*   **Scalability:** The system should be easily scalable to handle increasing data volume and query load.
*   **Fault Tolerance:** The system should be resilient to node failures. Data loss should be minimized.
*   **Time Window Accuracy:** The aggregates should be computed with reasonable accuracy within the defined time window (some degree of approximation is acceptable to improve performance).
*   **Memory Efficiency:** The system should manage memory efficiently to avoid excessive memory consumption.
*   **Implementation Language:** Python
*   **External Libraries:** Allowed. Standard libraries + popular libraries such as Redis, Kafka, Celery, or other distributed frameworks. Pick the proper libraries as the problem requires.

**Considerations:**

*   How will you distribute the event stream across multiple worker nodes?
*   How will you handle late-arriving events?
*   How will you ensure consistency of the aggregates across different nodes?
*   What data structures will you use to store the events within the time window?
*   How will you optimize query performance?

This problem requires a good understanding of distributed systems, data structures, and algorithms. You need to carefully consider the trade-offs between accuracy, latency, and scalability.
