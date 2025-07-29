## Question: Optimized Network Router Routing Table Lookup

### Question Description

You are tasked with designing and implementing a highly optimized routing table lookup mechanism for a network router. The router needs to forward packets based on their destination IP address. Due to the high volume of traffic, the routing table lookup must be extremely fast.

**The Routing Table:**

The routing table consists of entries, each representing a route to a specific IP address range. Each entry contains:

*   **Prefix:** An IP address prefix (e.g., "192.168.1.0/24"). This specifies a range of IP addresses.  The "/24" indicates the prefix length, meaning the first 24 bits of the IP address must match the prefix for the route to be considered.
*   **Next Hop:** The IP address of the next hop router to forward packets matching the prefix to.

**The Task:**

Implement a function `find_best_route(routing_table, destination_ip)` that takes a routing table (a list of prefix/next-hop pairs) and a destination IP address as input, and returns the best matching next hop.

**"Best" matching route means the route with the *longest* matching prefix length.**  If no route matches, return `None`.

**Input:**

*   `routing_table`: A list of tuples. Each tuple represents a routing table entry and contains two strings: `(prefix, next_hop)`. The prefix is in CIDR notation (e.g., "10.0.0.0/8"). The next_hop is a valid IPv4 address string (e.g. "192.168.0.1").
*   `destination_ip`: A string representing the destination IPv4 address (e.g., "10.1.2.3").

**Output:**

*   A string representing the next hop IP address for the best matching route, or `None` if no route matches.

**Constraints:**

1.  **Scale:** The routing table can contain up to 1,000,000 entries.
2.  **Speed:** The `find_best_route` function must execute very quickly (target: sub-millisecond average lookup time).  Consider algorithmic efficiency and data structure choices carefully.
3.  **Correctness:** The function must always return the correct next hop based on the longest prefix match rule.
4.  **Valid IP Addresses:** You can assume all IP addresses and prefixes are valid IPv4 addresses in standard dot-decimal notation and CIDR notation, respectively.
5.  **No External Libraries**: You can only use built-in python libraries. The use of external libraries such as `ipaddress` or `netaddr` is forbidden.

**Example:**

```python
routing_table = [
    ("10.0.0.0/8", "192.168.1.1"),
    ("10.1.0.0/16", "192.168.2.1"),
    ("10.1.2.0/24", "192.168.3.1"),
    ("0.0.0.0/0", "192.168.0.1"), # Default route
]
destination_ip = "10.1.2.3"

next_hop = find_best_route(routing_table, destination_ip)
print(next_hop)  # Output: 192.168.3.1
```

**Optimization Hints:**

*   Converting IP addresses and prefixes to integers can significantly speed up comparisons.
*   Consider using a data structure that allows for efficient prefix matching (e.g., a Trie, also known as a prefix tree). However implementing your own is necessary as external libraries are not allowed.
*   Pre-processing the routing table to build an optimized data structure can be beneficial, even if it adds some initial overhead.
*   Be mindful of memory usage, given the potential size of the routing table.

This problem requires careful consideration of data structures and algorithms to achieve the required performance. Good luck!
