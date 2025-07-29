## Project Name

`OptimalPacketRouter`

## Question Description

You are designing a core component of a high-throughput network router. The router needs to efficiently forward packets based on a routing table. The routing table contains destination network prefixes (CIDR notation) and the corresponding output interface. Your task is to implement an algorithm that, given a packet's destination IP address and a routing table, finds the best matching route and returns the output interface.

**Specifics:**

1.  **Routing Table:** The routing table is a list of entries, each containing a destination network prefix (in CIDR notation, e.g., "192.168.1.0/24") and an output interface (an integer representing the interface number). The routing table can be very large (millions of entries).

2.  **Longest Prefix Match:** The router uses the "longest prefix match" algorithm. This means that among all routes that match the destination IP address, the route with the longest (most specific) prefix wins. For example, if the routing table contains "192.168.1.0/24" and "192.168.0.0/16", and the destination IP address is "192.168.1.5", then "192.168.1.0/24" is the best match because the prefix length (24) is longer than the prefix length of "192.168.0.0/16" (16).

3.  **IP Address Representation:** Represent IP addresses as unsigned 32-bit integers. Convert CIDR notation prefixes to their integer representation and prefix length separately. For example, "192.168.1.0/24" would be represented as the integer `3232235776` (192.168.1.0 in decimal) and the prefix length `24`.

4.  **Efficiency Requirements:**
    *   The algorithm must be highly efficient, as it will be executed millions of times per second. Memory usage should also be optimized.
    *   Pre-processing of the routing table is allowed (and encouraged) to build an efficient data structure for lookups.  The pre-processing time should be reasonable (e.g., completed within a few seconds for a million-entry table).
    *   The lookup time (finding the best matching route for a single IP address) is the most critical performance metric.

5.  **Edge Cases:**
    *   The routing table may be empty.
    *   No route in the table may match the destination IP address.
    *   The routing table may contain overlapping prefixes (e.g., "10.0.0.0/8" and "10.0.0.0/24"). The longest prefix match rule must still apply.
    *   Invalid CIDR notations (e.g., prefix length > 32, invalid IP addresses) should be gracefully handled during routing table loading (either ignored or raise an error).

6.  **Input:**
    *   Routing Table: A list of strings, where each string represents a routing table entry in the format "IP_ADDRESS/PREFIX_LENGTH INTERFACE_NUMBER" (e.g., "192.168.1.0/24 1").
    *   Destination IP Address: A string representing the destination IP address (e.g., "192.168.1.5").

7.  **Output:**
    *   The output interface (an integer) of the best matching route. If no route matches, return -1.

**Constraints:**

*   The number of routing table entries can be up to 1,000,000.
*   The prefix length can be any integer between 0 and 32 inclusive.
*   The output interface number can be any non-negative integer.
*   Optimize for lookup speed.

**Bonus:**

*   Implement a mechanism to update the routing table dynamically (adding or removing entries) while minimizing disruption to packet forwarding.
*   Implement a mechanism to measure and report the lookup latency.

This problem requires a good understanding of IP addressing, CIDR notation, data structures (particularly those suitable for range queries), and algorithmic optimization techniques. Good luck!
