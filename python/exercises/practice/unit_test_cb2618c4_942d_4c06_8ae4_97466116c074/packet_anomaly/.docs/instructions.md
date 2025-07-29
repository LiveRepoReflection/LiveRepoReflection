## Project Name

**Network Packet Anomaly Detection**

## Question Description

You are tasked with building a network packet anomaly detection system. You will be provided with a stream of network packet data, and your system needs to identify anomalous packets in real-time.

The packet data consists of the following features:

*   `timestamp` (integer): Represents the time the packet was captured (in milliseconds since epoch).
*   `source_ip` (string): The source IP address of the packet.
*   `destination_ip` (string): The destination IP address of the packet.
*   `source_port` (integer): The source port used by the packet.
*   `destination_port` (integer): The destination port used by the packet.
*   `protocol` (string): The network protocol used (e.g., "TCP", "UDP").
*   `packet_size` (integer): The size of the packet in bytes.

You will receive packets in chronological order. Your system should maintain a model of "normal" network behavior and flag packets that deviate significantly from this model as anomalous.

**Constraints and Requirements:**

1.  **Real-time Performance:** The system must process packets with minimal latency. Aim for an average processing time of less than 1 millisecond per packet.
2.  **Adaptive Learning:** The system should continuously learn from the incoming packet stream and adapt to changes in network traffic patterns.  The definition of "normal" might change over time.
3.  **Scalability:** The system should be able to handle a high volume of network traffic (e.g., 100,000 packets per second).
4.  **Limited Memory:** The system should have a memory footprint of no more than 1GB.
5.  **Anomaly Scoring:** For each packet, the system must output an anomaly score between 0 and 1 (inclusive). Higher scores indicate a higher likelihood of the packet being anomalous.
6.  **Edge Cases:** Consider and handle potential edge cases, such as:
    *   Sudden spikes in traffic volume.
    *   New, previously unseen IP addresses and ports.
    *   Changes in the distribution of packet sizes.
7.  **Optimization:** You are encouraged to optimize your solution for both speed and memory usage. Profiling your code and identifying bottlenecks is crucial. Consider using techniques like caching, approximate algorithms, or optimized data structures.
8.  **Multiple Approaches:** There are multiple valid approaches to solving this problem, each with different trade-offs. Your choice of algorithm and data structures will significantly impact performance.  Think about statistical methods, machine learning techniques, and rule-based approaches.
9.  **Reproducibility:** Your solution should be deterministic and reproducible. Given the same input, it should always produce the same output.
10. **Justification**: Include a brief comment explaining the anomaly scoring method and what the score represents.

**Input:**

A stream of dictionaries, where each dictionary represents a network packet and contains the fields described above.

**Output:**

For each input packet, output a floating-point number representing the anomaly score for that packet.
