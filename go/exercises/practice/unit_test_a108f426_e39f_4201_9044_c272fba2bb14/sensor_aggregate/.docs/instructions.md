Okay, I'm ready to create a challenging Go coding problem. Here it is:

### Project Name

```
distributed-data-aggregation
```

### Question Description

You are tasked with building a distributed system to efficiently aggregate data from a large number of sensors. Each sensor periodically sends data samples in the form of key-value pairs to a central aggregator. Your solution must handle the following:

*   **Sensor Data:** Each sensor sends data as JSON objects of the form `{"sensor_id": "sensor1", "timestamp": 1678886400, "data": {"metric1": 10, "metric2": 20, ...}}`. The number of metrics per sensor can vary, and new metrics can be introduced at any time. The values of metrics are always integers.
*   **Data Aggregation:** The aggregator needs to compute the sum of each metric across all sensors within a specific time window. For example, calculate the total "metric1" for all sensors between timestamps T1 and T2.
*   **Distributed Architecture:** The system must consist of multiple worker nodes that receive data from sensors, perform partial aggregation, and then send the results to a central coordinator.
*   **Scalability:** The system should be able to handle a large number of sensors (millions) and a high data ingestion rate (thousands of messages per second).
*   **Fault Tolerance:** The system should be resilient to worker node failures. Data loss should be minimized.
*   **Time Windows:** The aggregation should be performed over configurable, non-overlapping time windows. The coordinator will specify the start and end timestamps for each window. The worker nodes should only aggregate data falling within the specified window.
*   **Data Ordering:** Sensor data may arrive out of order. The system must handle late-arriving data points that fall within the current time window. It does not need to handle data points that fall outside completed time windows.
*   **Efficiency:** Minimize network traffic between worker nodes and the coordinator. Minimize memory usage on both worker nodes and the coordinator.
*   **Real-time Aggregation:** The coordinator needs to be able to query the aggregated data for a completed time window with minimal latency.

**Constraints:**

*   Assume a fixed number of worker nodes.
*   You can use any suitable data structures and algorithms.
*   You can use the standard Go library and common concurrency primitives.
*   Consider using gRPC or similar technologies for communication between workers and the coordinator.
*   The system should be designed to be easily extendable to support other aggregation functions (e.g., average, min, max) in the future.

**Task:**

Implement the worker node and coordinator components in Go. The coordinator should be able to:

1.  Configure the time window duration.
2.  Instruct worker nodes to start aggregating data for a specific time window.
3.  Query the aggregated data for a completed time window, receiving the sum of each metric across all sensors.

The worker nodes should:

1.  Receive data from sensors.
2.  Perform partial aggregation of data within the current time window.
3.  Send the partial aggregation results to the coordinator when the time window closes.

**Bonus Challenges:**

*   Implement a mechanism for detecting and handling worker node failures.
*   Implement data persistence to minimize data loss in case of failures.
*   Optimize the system for even higher data ingestion rates and lower query latency.
*   Allow dynamic adjustment of the number of worker nodes.

This problem requires a good understanding of distributed systems principles, concurrency, data structures, and algorithms. It also involves practical considerations such as scalability, fault tolerance, and efficiency. Successfully solving this problem would be a significant achievement.
