## Project Name

**Network Anomaly Detection**

## Question Description

You are a security engineer tasked with building a near real-time anomaly detection system for a large-scale distributed network. The network consists of numerous interconnected nodes (servers, routers, IoT devices, etc.). Each node periodically sends network traffic data to a central monitoring system.

The network traffic data is represented as a stream of records. Each record contains the following information:

*   **timestamp (int):** The time the traffic data was recorded (Unix timestamp in seconds).
*   **source_node (str):** Unique identifier of the node sending the traffic.
*   **destination_node (str):** Unique identifier of the node receiving the traffic.
*   **packet_size (int):** The size of the network packet in bytes.
*   **protocol (str):** The network protocol used (e.g., TCP, UDP, HTTP).
*   **flags (int):** Bit field representing network flags.

Your goal is to implement an anomaly detection algorithm that can identify suspicious traffic patterns based on deviations from the historical baseline. Specifically, you need to detect anomalies based on the **packet size** for each **source-destination node pair** and **protocol**.

**Requirements:**

1.  **Real-time processing:** The system should be able to process the incoming stream of traffic data with minimal latency.
2.  **Adaptive baseline:** The historical baseline for each (source\_node, destination\_node, protocol) combination should be updated continuously as new data arrives. A sliding window approach is recommended.
3.  **Anomaly scoring:** Implement an anomaly scoring function that quantifies the degree of deviation from the baseline. Use the Z-score method (number of standard deviations from the mean) as the anomaly score.
4.  **Thresholding:** Define a threshold for the anomaly score. If the score exceeds the threshold, the traffic record is flagged as anomalous.
5.  **Memory Constraints:** Due to the large number of nodes and connections, you must design your solution to be memory-efficient. Avoid storing the entire history of packet sizes for each connection.
6.  **Scalability:** The solution should be designed to handle a growing number of network nodes and increasing traffic volume. Consider using appropriate data structures and algorithms to ensure scalability.
7.  **Edge Cases:** Handle new (source\_node, destination\_node, protocol) combinations gracefully. Initialize their baselines appropriately. Also, handle cases where the standard deviation is zero (e.g., due to insufficient data).

**Input:**

A stream of traffic records, represented as a list of dictionaries.

**Output:**

A list of traffic records that are flagged as anomalous, with an additional field `anomaly_score` indicating the anomaly score.

**Example Input:**

```python
[
    {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
    {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1100, "protocol": "TCP", "flags": 1},
    {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1200, "protocol": "TCP", "flags": 1},
    {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 5000, "protocol": "TCP", "flags": 1}, # Anomaly
    {"timestamp": 1678886404, "source_node": "C", "destination_node": "D", "packet_size": 500, "protocol": "UDP", "flags": 0},
    {"timestamp": 1678886405, "source_node": "C", "destination_node": "D", "packet_size": 600, "protocol": "UDP", "flags": 0},
    {"timestamp": 1678886406, "source_node": "C", "destination_node": "D", "packet_size": 700, "protocol": "UDP", "flags": 0},
    {"timestamp": 1678886407, "source_node": "C", "destination_node": "D", "packet_size": 100, "protocol": "UDP", "flags": 0}, # Anomaly
]
```

**Constraints:**

*   The number of traffic records can be very large (millions or billions).
*   The number of unique (source\_node, destination\_node, protocol) combinations can also be large (thousands or millions).
*   The solution should be implemented in Python and optimized for performance.
*   Use a sliding window of a fixed size (e.g., 1000 data points) to maintain the historical baseline.
*   Set the anomaly score threshold to a reasonable value (e.g., 3 standard deviations).

This problem challenges you to combine knowledge of data structures, algorithms, statistics, and system design principles to build a practical anomaly detection system. Good luck!
