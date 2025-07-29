Okay, here's a challenging coding problem:

**Project Name:**

```
Distributed-Event-Stream-Analytics
```

**Question Description:**

You are tasked with building a highly scalable and fault-tolerant system for analyzing a continuous stream of events in a distributed environment.  Imagine you are working for a large IoT platform that receives sensor data from millions of devices around the world. Your system needs to perform complex analytical queries on this data in real-time.

Each event in the stream is a JSON object with the following structure:

```json
{
    "device_id": "unique_device_identifier",
    "timestamp": 1678886400, // Unix timestamp in seconds
    "type": "sensor_type", // e.g., "temperature", "pressure", "humidity"
    "value": 25.5, // Sensor reading
    "location": {
        "latitude": 34.0522,
        "longitude": -118.2437
    },
    "metadata": {
        //Optional metadata, can be any key-value pairs
    }
}
```

Your system must support the following analytical queries:

1.  **Average Value by Time Window:** Calculate the average `value` for a given `device_id` and `type` within a specified time window (start and end timestamps). The time window can range from minutes to days.

2.  **Top K Devices by Event Count:** Determine the top `K` `device_id`s that have generated the most events of a specific `type` within a given time window.

3.  **Geospatial Aggregation:** Calculate the average `value` for a given `type` within a specified geographical region (defined by a bounding box: min_latitude, max_latitude, min_longitude, max_longitude) and time window.

**Constraints and Requirements:**

*   **Scalability:** The system must be able to handle millions of events per second.
*   **Fault Tolerance:** The system must be able to recover from node failures without losing data or interrupting service.
*   **Real-Time Analysis:** Queries should return results with minimal latency (ideally within seconds).
*   **Data Persistence:** All incoming events must be durably stored.
*   **Distributed Architecture:** The solution must be designed to run on a cluster of machines.  Assume you have access to a distributed message queue (like Kafka or RabbitMQ) for receiving events and a distributed database (like Cassandra or a time-series database like InfluxDB or TimescaleDB) for storing data.
*   **Efficient Querying:** The system should be optimized for the specified analytical queries. Naive approaches that scan the entire dataset for each query will not be accepted.
*   **Memory Constraint**: Assume the program runs on a machine with limited memory and can't load all the data into memory at once.
*   **Event Ordering**: The events are not guaranteed to arrive in timestamp order.
*   **Data Skew**: The distribution of events across devices and types can be highly skewed. Some devices may generate significantly more events than others.

**Deliverables:**

1.  **System Design Document:** A detailed description of your system architecture, including the components used, the data flow, and the rationale behind your design choices.  Address scalability, fault tolerance, and real-time requirements.  Consider trade-offs between different architectural options. Be specific about how you are handling the data skew.
2.  **Code Implementation:** Implement the core logic for ingesting events from the message queue, storing them in the database, and executing the analytical queries. While a full production-ready implementation is not required, the code should be well-structured, documented, and demonstrate the key concepts of your design. You can use Python and any relevant libraries (e.g., `kafka-python`, database drivers).  Focus on the efficiency of the querying logic.

**Bonus Points:**

*   Implement a caching mechanism to further reduce query latency.
*   Implement a mechanism for detecting and handling late-arriving data (events with timestamps significantly older than the current time).
*   Implement a mechanism for automatically scaling the system based on the event ingestion rate.
*   Provide a benchmark comparing the performance of your system with different data volumes and query parameters.

This problem requires a solid understanding of distributed systems, data structures, algorithms, and database technologies. Good luck!
