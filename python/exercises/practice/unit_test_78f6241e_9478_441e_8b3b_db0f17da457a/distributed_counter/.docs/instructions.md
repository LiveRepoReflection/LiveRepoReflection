## Project Name

`DistributedKeyCounter`

## Question Description

You are tasked with building a distributed key-value counter service. This service receives a stream of events, each containing a key and a delta (an integer, which can be positive or negative). The service must maintain the sum of all deltas for each key and provide an efficient way to query the current count for any given key.

**System Requirements:**

1.  **Distributed Architecture:** The service should be designed to run across multiple nodes (think microservices). You don't need to *implement* multiple nodes, but your data structures and algorithms should be designed with distribution in mind.  Consider how data might be sharded or replicated across nodes in a real-world deployment. Assume that each node has limited memory (e.g., a few GB).
2.  **High Throughput:** The service needs to handle a high volume of incoming events (millions per second).  Processing each event should be as efficient as possible.
3.  **Low Latency:** Querying the count for a key should be fast.  Users expect near real-time counts.
4.  **Eventual Consistency:** Strict consistency is not required. Slight discrepancies in counts across nodes are acceptable, but the system should converge towards accurate counts over time.
5.  **Memory Efficiency:** Given the memory constraints on each node, the service should be memory-efficient.  Consider that the number of unique keys could be very large (billions).
6.  **Key Expiry (Optional):** Implement an optional mechanism to expire keys that haven't been updated in a while (e.g., after a week of inactivity). This can help manage memory usage.  This must be configurable. Expired keys should return a count of 0 when queried.
7.  **Handling of negative values:** The counter should be able to count negative values as well.

**Input:**

The service receives events in the following format:

```python
class Event:
    def __init__(self, key: str, delta: int):
        self.key = key
        self.delta = delta
```

**Output:**

The service must provide a `get_count(key: str) -> int` method that returns the current count for a given key.  If the key doesn't exist, it should return 0.

**Constraints:**

*   You can use standard Python libraries.
*   Consider the trade-offs between data structures (e.g., dictionaries, trees, probabilistic data structures like Bloom filters or Count-Min Sketch).
*   Assume that network communication between nodes (if you were to implement it) is the bottleneck.
*   Focus on the core data structures and algorithms for counting and querying.  You don't need to implement the actual network communication or distributed consensus mechanisms.
*   Pay attention to algorithmic complexity and memory usage. Aim for solutions with optimal or near-optimal performance.
*   The solution should be thread-safe. Multiple threads could be calling `process_event` and `get_count` simultaneously.

**Bonus:**

*   Implement a mechanism to periodically flush the counts to persistent storage (e.g., a file or database) to prevent data loss in case of node failure. How would you ensure this process does not block the normal operation of `process_event` and `get_count`?
*   Explain how your solution would scale horizontally (adding more nodes) and the challenges involved.
*   Evaluate the time and space complexity of your solution.
*   Describe how you would monitor the health and performance of the service in a production environment.

This problem requires careful consideration of data structures, algorithms, and system design principles to create a highly performant and scalable solution. Good luck!
