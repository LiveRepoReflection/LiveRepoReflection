Okay, here's a challenging Go coding problem designed to be at LeetCode Hard difficulty.

**Project Name:** `EfficientRouter`

**Question Description:**

Imagine you are building a highly efficient network router. The router needs to forward packets based on a complex routing table. The routing table consists of a set of rules. Each rule has the following attributes:

*   **Prefix:** A string representing an IP address prefix in CIDR notation (e.g., "192.168.1.0/24", "10.0.0.0/8", "0.0.0.0/0").
*   **NextHop:** A string representing the IP address of the next hop router.
*   **Metric:** An integer representing the cost associated with using this route. Lower values indicate preferred routes.

Given a large set of routing rules and a stream of incoming IP addresses, your task is to determine the optimal next hop for each incoming IP address. "Optimal" means the next hop associated with the rule that:

1.  **Matches the Longest Prefix:** Among all rules that match the destination IP address, the rule with the *most specific* prefix (i.e., the longest prefix) is preferred. For example, "192.168.1.0/24" is more specific than "192.168.1.0/16".
2.  **Lowest Metric Tiebreaker:** If multiple rules match with the same longest prefix length, the rule with the *lowest* metric is preferred.

**Input:**

*   A list of routing rules, each containing a Prefix, NextHop, and Metric. The number of rules can be large (e.g., 100,000+). The prefixes may overlap.
*   A stream of IP addresses to be routed. The number of IP addresses in the stream can also be large.

**Output:**

*   For each incoming IP address, output the NextHop associated with the optimal routing rule (as described above). If no rule matches the IP address, output "DROP".

**Constraints and Requirements:**

*   **Efficiency is paramount:** The solution must be highly efficient in terms of both time and memory usage. Naive solutions (e.g., iterating through all rules for each IP address) will likely time out. Consider the data structures and algorithms you choose very carefully.
*   **Scalability:** The solution should scale well to handle a large number of routing rules and a large stream of IP addresses.
*   **Correctness:** The solution must correctly implement longest prefix matching and metric-based tiebreaking.
*   **IP Address Format:** IP addresses will be in standard IPv4 dotted-decimal notation (e.g., "192.168.1.1").
*   **CIDR Notation:** Prefixes will be in standard CIDR notation. You'll need to parse this notation to determine the network address and prefix length.
*   **Error Handling:** The input data is guaranteed to be well-formed and valid, so you don't need to worry about handling malformed IP addresses or invalid CIDR notations.

**Example:**

**Routing Rules:**

```
Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10
Prefix: "192.168.1.0/16", NextHop: "RouterB", Metric: 20
Prefix: "0.0.0.0/0", NextHop: "RouterC", Metric: 30
Prefix: "192.168.1.5/32", NextHop: "RouterD", Metric: 5
```

**Incoming IP Addresses:**

```
192.168.1.1
10.0.0.1
192.168.1.5
```

**Output:**

```
RouterA
RouterC
RouterD
```

**Explanation:**

*   For 192.168.1.1: Both "192.168.1.0/24" and "192.168.1.0/16" match. "192.168.1.0/24" is the longest prefix match, so RouterA is the correct next hop.
*   For 10.0.0.1: Only "0.0.0.0/0" matches, so RouterC is the correct next hop.
*   For 192.168.1.5:  "192.168.1.5/32", "192.168.1.0/24" and "192.168.1.0/16" match. "192.168.1.5/32" is the longest prefix match, so RouterD is the correct next hop.

This problem requires a good understanding of IP addressing, CIDR notation, and efficient data structures for searching and matching. Good luck!
