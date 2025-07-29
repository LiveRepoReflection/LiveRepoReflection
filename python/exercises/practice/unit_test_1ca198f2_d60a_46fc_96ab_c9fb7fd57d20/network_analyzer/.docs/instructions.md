## Project Name

**NetworkTrafficAnalyzer**

## Question Description

You are tasked with building a network traffic analyzer that can identify and classify network flows based on various packet characteristics.  The input is a massive stream of network packets, and your goal is to efficiently identify and flag potentially malicious or anomalous network flows. Due to the scale of the traffic, your solution must be highly optimized for both time and space complexity.

Specifically, you need to implement a system that performs the following:

1.  **Flow Aggregation:** Define a network flow as a 5-tuple: `(source IP, destination IP, source port, destination port, protocol)`. Aggregate packets belonging to the same flow.

2.  **Feature Extraction:** For each flow, extract the following features within a fixed time window (e.g., 60 seconds):
    *   Total number of packets
    *   Total bytes transferred
    *   Average packet size
    *   Packet rate (packets per second)
    *   Byte rate (bytes per second)
    *   Number of unique destination ports contacted by the source IP within this flow.
    *   Ratio of SYN packets to total packets (for TCP flows only, otherwise 0)

3.  **Anomaly Detection:** Implement an anomaly detection mechanism.  Assume you are given a pre-trained anomaly detection model (represented by a function `is_anomalous(features)` that takes a dictionary of the extracted features and returns `True` if the flow is anomalous, and `False` otherwise). You do *not* need to implement the anomaly detection model itself; you only need to use the provided function.

4.  **Rate Limiting:** To prevent overwhelming the system with flagged anomalies, implement a rate limiter. Only report a maximum of *K* anomalous flows per *T* seconds (e.g., K=10, T=60).  If more than *K* anomalous flows are detected within the time window *T*, only report the first *K* and discard the rest.  Important: The rate limiting should apply *globally* across all flows.

5.  **Memory Management:** Given the massive scale of network traffic, memory usage is a critical concern.  Implement a mechanism to evict inactive flows from memory.  A flow is considered inactive if no packets belonging to it have been seen for a certain period (e.g., 300 seconds). Use an appropriate data structure that minimizes the overhead of tracking flow activity.

6.  **Concurrency:** The packet stream arrives at a high rate.  Your solution should be designed to handle concurrent packet processing efficiently.  Consider using appropriate threading or asynchronous techniques to maximize throughput.

**Input:**

*   A stream of network packets represented as a sequence of dictionaries. Each dictionary has the following keys:
    *   `timestamp` (float): The time the packet was received (in seconds since epoch).
    *   `src_ip` (str): Source IP address.
    *   `dst_ip` (str): Destination IP address.
    *   `src_port` (int): Source port.
    *   `dst_port` (int): Destination port.
    *   `protocol` (str): Protocol (e.g., "TCP", "UDP").
    *   `packet_size` (int): Size of the packet in bytes.
    *   `flags` (dict): Dictionary of TCP flags (e.g., `{'SYN': True, 'ACK': False}`).  Only present for TCP packets; otherwise, `flags` is an empty dict.

*   `is_anomalous(features)`: A function (provided externally) that takes a dictionary of flow features and returns `True` if the flow is anomalous, and `False` otherwise.

*   `K` (int): The maximum number of anomalous flows to report per `T` seconds.
*   `T` (int): The time window for rate limiting anomalous flows (in seconds).
*   `inactivity_timeout` (int):  The time after which an inactive flow is evicted from memory (in seconds).
*   `feature_window` (int): The size of the time window (in seconds) used to extract features.

**Output:**

*   A list of anomalous network flows, where each flow is represented by its 5-tuple `(source IP, destination IP, source port, destination port, protocol)`.  The list should be rate-limited according to the specified parameters.

**Constraints and Considerations:**

*   **Performance:** The solution must be able to process a very large volume of packets in real-time.  Optimize for both time and space complexity. Avoid unnecessary computations or data copies.
*   **Scalability:** The solution should be designed to handle a large number of concurrent flows.
*   **Accuracy:** Ensure that the flow aggregation and feature extraction are accurate.
*   **Real-time Processing:** The solution should be able to analyze the packet stream as it arrives, with minimal delay.
*   **Edge Cases:** Consider edge cases such as:
    *   Packets arriving out of order (based on timestamp).
    *   Flows with very few packets.
    *   Flows that span multiple time windows.
    *   Network protocols other than TCP and UDP.
    *   SYN packets without ACK packets.

This is a challenging problem that requires a combination of data structure knowledge, algorithmic optimization, and an understanding of network traffic analysis. Good luck!
