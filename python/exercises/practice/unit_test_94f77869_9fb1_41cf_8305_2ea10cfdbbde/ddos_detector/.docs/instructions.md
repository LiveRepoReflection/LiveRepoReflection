## Question: Network Anomaly Detection

**Description:**

You are tasked with building a real-time network anomaly detection system. You are given a stream of network packets, each represented as a dictionary with the following keys:

*   `timestamp`: An integer representing the time the packet was observed (Unix timestamp).
*   `source_ip`: A string representing the source IP address.
*   `destination_ip`: A string representing the destination IP address.
*   `source_port`: An integer representing the source port number.
*   `destination_port`: An integer representing the destination port number.
*   `packet_size`: An integer representing the size of the packet in bytes.

Your system needs to identify potential Distributed Denial-of-Service (DDoS) attacks targeting specific destination IPs.  A DDoS attack, in this context, is characterized by a sudden surge in traffic from many distinct source IPs to a single destination IP within a short time window.

**Specific Requirements:**

1.  **Real-time Processing:** The system must process packets as they arrive in a stream. It cannot afford to store all packets and analyze them later.
2.  **Sliding Window:** Analyze the traffic within a sliding time window of `W` seconds.
3.  **Anomaly Score:** For each destination IP within the sliding window, calculate an anomaly score. The anomaly score for a destination IP is defined as the number of distinct source IPs that have sent packets to that destination IP within the sliding window.
4.  **Thresholding:** Report a destination IP as a potential DDoS target if its anomaly score exceeds a predefined threshold `T`.
5.  **Memory Constraints:**  The system has limited memory. The number of destination IPs being monitored can be very large, but the number of active connections (source IP to destination IP) within the sliding window at any given time is significantly smaller.  You need to design your data structures to minimize memory usage while still allowing for efficient anomaly score calculation.  Consider using approximate data structures if necessary to meet the memory constraint.
6.  **Throughput:** The system must be able to handle a high packet arrival rate.  Optimize your code for speed.
7.  **Time Decay:** Implement a mechanism to decay the influence of older packets within the sliding window. You can achieve this by using a weighted counting approach, where each source IP's contribution to the anomaly score decays exponentially over time. The weight of a source IP is calculated as `exp(-lambda * (current_time - first_packet_time))`, where `lambda` is a decay factor and `first_packet_time` is the timestamp of the first packet received from that source IP to the destination IP within the current sliding window.

**Input:**

A stream of network packets (dictionaries) arriving one at a time.

**Output:**

A list of destination IPs that are identified as potential DDoS targets. The list should be updated in real-time as new packets are processed.

**Constraints:**

*   `W` (sliding window size): 60 seconds
*   `T` (anomaly score threshold): 1000
*   `lambda` (decay factor): 0.1
*   Packet arrival rate: Up to 100,000 packets per second.
*   Memory limit: 1 GB

**Example:**

Let's say you receive the following packets (simplified for brevity):

```python
packet1 = {'timestamp': 1678886400, 'source_ip': '1.1.1.1', 'destination_ip': '10.0.0.1', 'source_port': 12345, 'destination_port': 80, 'packet_size': 100}
packet2 = {'timestamp': 1678886401, 'source_ip': '1.1.1.2', 'destination_ip': '10.0.0.1', 'source_port': 12346, 'destination_port': 80, 'packet_size': 100}
# ... hundreds of packets from different source IPs to 10.0.0.1
packetN = {'timestamp': 1678886459, 'source_ip': '1.1.1.999', 'destination_ip': '10.0.0.1', 'source_port': 12345, 'destination_port': 80, 'packet_size': 100}
packetNplus1 = {'timestamp': 1678886460, 'source_ip': '1.1.1.1000', 'destination_ip': '10.0.0.1', 'source_port': 12345, 'destination_port': 80, 'packet_size': 100}

# After processing these packets, if the anomaly score for 10.0.0.1 exceeds T=1000, the system should output:
# ['10.0.0.1']

# If, after processing more packets, the anomaly score for another destination IP, say 10.0.0.2, also exceeds T, the system should output:
# ['10.0.0.1', '10.0.0.2']
```

**Note:** The order of destination IPs in the output list is not important. The primary goal is to accurately identify potential DDoS targets in real-time while adhering to the memory and throughput constraints.
