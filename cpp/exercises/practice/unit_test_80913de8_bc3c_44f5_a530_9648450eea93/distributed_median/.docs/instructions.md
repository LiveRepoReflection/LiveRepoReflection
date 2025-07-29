Okay, challenge accepted! Here's a problem designed to be a significant test of skill, drawing on several advanced concepts.

### Project Name

```
distributed-median
```

### Question Description

You are building a distributed system for real-time analytics of sensor data. The system consists of a network of `N` sensor nodes and a central aggregator node. Each sensor node continuously generates numerical data points. Your task is to efficiently compute the running median of all data points observed across the entire network.

**System Constraints:**

1.  **Limited Bandwidth:** Communication between sensor nodes and the aggregator is expensive and has limited bandwidth. Minimize the amount of data transferred.
2.  **Real-time Requirements:** The system must provide an estimate of the median with minimal delay.
3.  **Unbalanced Data Streams:** Sensor nodes may generate data at different rates and with different distributions.
4.  **Memory Constraints:** The aggregator node has limited memory. Storing all data points is not feasible.
5.  **Dynamic Network:** Sensor nodes may join or leave the network dynamically.

**Specific Requirements:**

*   Implement a data structure and algorithm at the aggregator node to maintain an estimate of the median of all data points received from the sensor nodes.
*   Each sensor node can only send aggregated statistics (e.g., quantiles, histograms, counts) to the aggregator, **not** the raw data.
*   The aggregator should provide a function `get_median()` that returns the current median estimate.
*   The aggregator should provide a function `update(node_id, data)` that receives the data from a sensor node.  The `data` will be a precomputed summary of the data points observed at that node since the last update. The format of the `data` is as follows, this is an array of floating point numbers:
    *   `data[0]` : `count` - the number of data points observed at the sensor node since the last update.
    *   `data[1]` : `min` - The minimum value observed at the sensor node since the last update.
    *   `data[2]` : `max` - The maximum value observed at the sensor node since the last update.
    *   `data[3]` : `q1` - The 25th percentile value (first quartile)
    *   `data[4]` : `median` - The 50th percentile value (second quartile, the median of the sensor's data)
    *   `data[5]` : `q3` - The 75th percentile value (third quartile)

*   Your solution should strive to balance accuracy, communication cost, and memory usage.  A perfect median is not required; a good approximation is sufficient.
*   The system must be able to handle a large number of nodes (up to 10,000) and a high data arrival rate.
*   The median estimate should be reasonably accurate even with skewed data distributions and varying data rates across nodes.

**Constraints:**

*   `1 <= N <= 10000` (Number of sensor nodes)
*   Data points are floating-point numbers within a reasonable range (e.g., -1000.0 to 1000.0).
*   The `update` function should have a time complexity significantly better than `O(N)` where N is the total number of data points, considering the constraints.
*   Memory usage at the aggregator should be limited (e.g., no more than a few megabytes).

**Judging Criteria:**

*   Correctness: The `get_median()` function returns a reasonable approximation of the true median.
*   Efficiency: The `update()` function runs quickly, and the communication cost (amount of data transferred) is minimized.
*   Scalability: The system can handle a large number of nodes and a high data arrival rate.
*   Memory Usage: The aggregator does not exceed its memory limit.
*   Code Quality: The code is well-structured, readable, and maintainable.

This problem challenges candidates to design a distributed system that balances accuracy, communication cost, and memory usage. It requires knowledge of data structures, algorithms, statistics, and distributed systems concepts. Good luck!
