## Question: Optimized Network Flow Allocation

**Problem Description:**

You are tasked with designing an efficient algorithm for managing network bandwidth allocation in a data center. The data center consists of `n` servers and `m` communication links between them. Each server can generate data (source) and consume data (sink). Each communication link has a limited bandwidth capacity.

Specifically, you are given the following:

*   `n`: The number of servers, numbered from 0 to `n-1`.
*   `m`: The number of communication links.
*   `capacity`: A list of tuples `(u, v, c)`, where `u` and `v` are server indices (0-based) representing a directed communication link from server `u` to server `v`, and `c` is the bandwidth capacity of that link.  Note that there can be multiple links between two servers and self-loops are possible.
*   `sources`: A list of tuples `(s, amount)`, where `s` is the server index that generates data and `amount` is the amount of data it needs to send.
*   `sinks`: A list of tuples `(t, amount)`, where `t` is the server index that consumes data and `amount` is the amount of data it needs to receive.

Your goal is to determine the maximum amount of data that can be successfully transmitted from the sources to the sinks, respecting the bandwidth capacities of the communication links. You need to allocate flows to each link in the network such that:

1.  For each link `(u, v)`, the flow from `u` to `v` does not exceed the link's capacity.
2.  For each server (except source and sink servers), the total incoming flow equals the total outgoing flow (flow conservation).
3.  The total amount of data sent from sources is equal to the total amount of data received by sinks (overall conservation).
4.  The total flow is maximized.

**Input:**

*   `n` (integer): The number of servers. `1 <= n <= 200`
*   `m` (integer): The number of communication links. `1 <= m <= 5000`
*   `capacity` (list of tuples): A list of `(u, v, c)` tuples representing the communication links. `0 <= u < n`, `0 <= v < n`, `1 <= c <= 10^6`.
*   `sources` (list of tuples): A list of `(s, amount)` tuples representing the source servers. `0 <= s < n`, `1 <= amount <= 10^7`.
*   `sinks` (list of tuples): A list of `(t, amount)` tuples representing the sink servers. `0 <= t < n`, `1 <= amount <= 10^7`.
*   The sum of all source `amount` equals the sum of all sink `amount`.

**Output:**

*   (integer): The maximum amount of data that can be successfully transmitted from the sources to the sinks.

**Constraints:**

*   The solution must efficiently handle large inputs.  The time complexity is crucial.
*   The solution must be able to handle multiple sources and sinks.
*   The network may not be fully connected.
*   The solution must correctly handle cases where the total source amount cannot be fully delivered to the sinks due to bandwidth limitations.
*   Your code should use standard libraries. You are expected to come up with the most optimized data structure and algorithm to solve this problem.
