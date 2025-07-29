Okay, here's a challenging problem designed to test a programmer's skills in algorithm design, data structures, and optimization.

### Project Name

```
DistributedMedian
```

### Question Description

Imagine you are building a large-scale distributed system to process streaming numerical data. The data arrives continuously from various geographically dispersed sources. Each source represents a shard and is essentially an unbounded stream of numbers. Due to network latency and processing constraints, it's impractical to centralize all data for real-time calculations. Your task is to design and implement a system that can efficiently compute the running median of all numbers seen so far across all shards.

Specifically, you need to implement the following:

1.  **Shard Ingestion:** Design a method to ingest incoming numerical data from multiple shards. The system should be able to handle a dynamically changing number of shards (sources).

2.  **Local Median Calculation:** Each shard should maintain its local view of the data stream and efficiently calculate its local median.

3.  **Global Median Approximation:** Develop a mechanism to approximate the global median across all shards. It's crucial to minimize communication between shards to achieve low latency and high throughput. Since getting a perfectly accurate median across a distributed system is very expensive, you are allowed to have some approximation error, but you must make sure that the result is still meaningful.

4.  **Scalability and Fault Tolerance:** Your solution should be designed to handle a large number of shards and be resilient to shard failures. While you don't need to implement actual fault tolerance, describe how your design would address this concern.

5.  **Optimization:** Consider optimizing for both space and time complexity. Think about the trade-offs between accuracy, communication overhead, and computational resources.

**Constraints:**

*   The number of shards can vary dynamically.
*   Each shard receives data in an unbounded stream.
*   Communication between shards should be minimized.
*   The system needs to provide a running median approximation with reasonable accuracy.
*   The memory footprint of each shard should be reasonable.
*   The data streams are not sorted.
*   The values in the streams are floating point numbers.

**Requirements:**

*   Describe your chosen data structures and algorithms, justifying your design choices.
*   Analyze the time and space complexity of your solution.
*   Discuss the trade-offs between accuracy, communication overhead, and computational resources.
*   Outline potential fault-tolerance strategies.
*   Explain how your design would scale to handle a very large number of shards.

This problem challenges the candidate to think about distributed systems design, streaming data processing, approximation algorithms, and resource optimization, all critical aspects of building modern large-scale applications. Good luck!
