## Project Name:

```
NetworkAnomalyDetection
```

## Question Description:

You are tasked with building a real-time anomaly detection system for network traffic. You are given a continuous stream of network flow records. Each record contains the following information:

*   `timestamp` (in seconds since epoch): Integer representing the time the flow was recorded.
*   `source_ip`: String representing the source IP address.
*   `destination_ip`: String representing the destination IP address.
*   `source_port`: Integer representing the source port.
*   `destination_port`: Integer representing the destination port.
*   `protocol`: String representing the network protocol (e.g., "TCP", "UDP").
*   `packet_size`: Integer representing the size of the packet in bytes.
*   `packet_count`: Integer representing the number of packets in the flow.

Your system must be able to detect network anomalies based on deviations from normal traffic patterns. "Normal" traffic patterns can evolve over time, so the system must be adaptive.

**Requirements:**

1.  **Real-time Processing:** The system must process each network flow record as it arrives, with minimal latency.  The system must be able to handle a high volume of network traffic (e.g., 100,000 records per second).
2.  **Adaptive Learning:**  The system should adapt to changes in network traffic patterns over time.  Anomalies are defined as significant deviations from recent historical traffic.
3.  **Anomaly Scoring:**  For each network flow record, the system should calculate an anomaly score. The anomaly score should be a floating-point number between 0 and 1, where 0 indicates normal traffic and 1 indicates a severe anomaly. The anomaly score should reflect the degree of deviation of the current flow from the learned traffic pattern.
4.  **Customizable Features:** The anomaly detection system should be designed to easily incorporate new features to improve detection accuracy.  Specifically, you must implement at least two features beyond the basic flow information (e.g., entropy of source ports for a given destination IP over a time window, ratio of TCP SYN packets to total packets).
5.  **Efficient Data Structures:** The system should use efficient data structures to store and process the historical network traffic data. Memory usage should be reasonable given the high traffic volume.
6.  **Clear Output:** The system should output the timestamp, source IP, destination IP, and anomaly score for each record.
7.  **Scalability**: The code should be written in such a way that it could be parallelized to handle even larger traffic volumes. Focus on minimizing shared state and maximizing modularity.

**Constraints:**

*   You are limited to using standard Python libraries and the `numpy` library for numerical computation. You can also use the `datasketch` library for minhash implementation. No other external libraries are allowed.
*   The system must be memory-efficient.  Storing all historical data is not feasible.
*   The anomaly detection algorithm must be computationally efficient for real-time processing.
*   The algorithm should be robust to noisy data and occasional spikes in traffic.

**Example Input:**

A stream of network flow records represented as dictionaries:

```python
[
    {"timestamp": 1678886400, "source_ip": "192.168.1.100", "destination_ip": "8.8.8.8", "source_port": 50000, "destination_port": 53, "protocol": "UDP", "packet_size": 512, "packet_count": 1},
    {"timestamp": 1678886401, "source_ip": "192.168.1.101", "destination_ip": "8.8.8.8", "source_port": 50001, "destination_port": 53, "protocol": "UDP", "packet_size": 512, "packet_count": 1},
    {"timestamp": 1678886402, "source_ip": "192.168.1.100", "destination_ip": "8.8.8.8", "source_port": 50000, "destination_port": 53, "protocol": "UDP", "packet_size": 512, "packet_count": 1},
    {"timestamp": 1678886403, "source_ip": "10.0.0.1", "destination_ip": "172.217.160.142", "source_port": 44444, "destination_port": 80, "protocol": "TCP", "packet_size": 1500, "packet_count": 10}, #Possible anomaly
    # ... more records
]
```

**Example Output:**

```
1678886400 192.168.1.100 8.8.8.8 0.05
1678886401 192.168.1.101 8.8.8.8 0.02
1678886402 192.168.1.100 8.8.8.8 0.03
1678886403 10.0.0.1 172.217.160.142 0.85
# ... more records
```

**Evaluation Criteria:**

*   **Correctness:** The accuracy of the anomaly detection system. Higher accuracy in detecting true anomalies and minimizing false positives is better.
*   **Efficiency:** The processing time per network flow record. Lower latency is better.
*   **Memory Usage:** The amount of memory used by the system. Lower memory usage is better.
*   **Scalability:** The ability of the system to handle high volumes of network traffic.
*   **Code Quality:** The clarity, organization, and maintainability of the code.
*   **Feature Engineering:** The relevance and effectiveness of the custom features implemented.
*   **Adaptive Learning**: The system's ability to adapt to changing traffic patterns
