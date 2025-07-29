## Project Name

`Advanced Network Packet Analyzer`

## Question Description

You are tasked with building an advanced network packet analyzer that can efficiently process and analyze a large stream of network packets in real-time. The system should be able to identify and flag potentially malicious or anomalous network activity based on a combination of packet characteristics and pre-defined rules.

**Input:**

The input is a continuous stream of network packets represented as strings. Each packet string contains the following comma-separated fields:

*   `timestamp`: A long integer representing the packet's timestamp in milliseconds since the epoch.
*   `source_ip`: A string representing the source IP address (e.g., "192.168.1.1").
*   `destination_ip`: A string representing the destination IP address (e.g., "10.0.0.5").
*   `source_port`: An integer representing the source port.
*   `destination_port`: An integer representing the destination port.
*   `protocol`: A string representing the network protocol (e.g., "TCP", "UDP", "ICMP").
*   `packet_size`: An integer representing the packet size in bytes.
*   `flags`: A string representing TCP flags (e.g., "SYN", "ACK", "SYN-ACK", "NONE"). Can be "NONE" if not a TCP packet.

Example Packet:

```
1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN
```

**Rules:**

The analyzer should apply the following rules to each packet:

1.  **Blacklisted IPs:** Check if either the `source_ip` or `destination_ip` is present in a provided blacklist of IP addresses.
2.  **Port Scanning:** Detect potential port scanning activity.  A source IP is considered to be port scanning if it attempts to connect to more than `N` distinct destination ports within a sliding window of `T` milliseconds.
3.  **Large Packet Size:** Flag packets exceeding a size threshold `S` bytes.
4.  **SYN Flood Detection:**  Detect SYN floods. A destination IP is considered to be under a SYN flood if it receives more than `M` SYN packets within a sliding window of `T` milliseconds.
5.  **Unusual Protocol/Port Combinations:** Flag packets where the `protocol` and `destination_port` combination is considered unusual, based on a provided set of "normal" combinations.

**Output:**

The analyzer should output a list of strings, where each string represents a flagged packet. Each flagged packet string should be the original packet string prepended with the flag reason, separated by a colon.  The flag reasons should be the strings: "BLACKLIST", "PORTSCAN", "LARGESIZE", "SYNFLOOD", and "UNUSUAL".

Example Output:

```
[
"BLACKLIST:1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN",
"PORTSCAN:1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN",
"LARGESIZE:1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN",
"SYNFLOOD:1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN",
"UNUSUAL:1678886400000,192.168.1.10,10.0.0.20,54321,80,TCP,1024,SYN"
]
```

**Constraints and Requirements:**

*   **Real-time Performance:**  The analyzer must be able to process a large volume of packets efficiently, with minimal latency.  Assume the packet stream is continuous and potentially very large.
*   **Memory Efficiency:**  The analyzer should use memory efficiently, especially for the port scanning and SYN flood detection rules, which require maintaining state over time.  Avoid storing entire packet histories.
*   **Scalability:**  The design should be scalable to handle increasing packet volumes and rule complexity.
*   **Accuracy:** The analyzer must accurately identify malicious or anomalous activity based on the defined rules.  False positives should be minimized.
*   **Thread Safety:**  The analyzer might be deployed in a multi-threaded environment, so thread safety is crucial (although you don't have to explicitly demonstrate multi-threading in your solution).
*   **Parameterization:** The values for `N`, `T`, `S`, the blacklist, and the "normal" protocol/port combinations should be configurable.

**Input Data Details:**

*   Packets arrive in chronological order based on the `timestamp`.
*   The `timestamp` values are monotonically increasing.

**Example Configuration Data:**

*   `N` (Port Scan Threshold): 10
*   `T` (Time Window): 60000 milliseconds (1 minute)
*   `S` (Large Packet Size Threshold): 1500 bytes
*   `blacklist`: `["192.168.1.100", "10.0.0.50"]`
*   `normal_combinations`: `[("TCP", 80), ("TCP", 443), ("UDP", 53)]`

**Considerations:**

*   Think about efficient data structures to store and retrieve data needed for the port scanning and SYN flood detection rules (e.g., to track destination ports and SYN packet counts within the time window).
*   Consider using appropriate algorithms to maintain the sliding windows efficiently.
*   Assume that the input data is well-formed and conforms to the specified format.
*   Handle edge cases gracefully.

This problem is designed to test your understanding of data structures, algorithms, system design principles, and your ability to write efficient and scalable code. Good luck!
