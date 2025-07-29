## Project Name

```
Distributed-Median-Stream
```

## Question Description

You are tasked with designing a system to efficiently calculate the running median of a massive stream of numerical data distributed across multiple servers. Each server receives a portion of the data stream in real-time. Your goal is to compute the global median as new data arrives on each server, minimizing communication overhead and maximizing efficiency.

**Specifics:**

1.  **Data Stream:** A continuous flow of numerical data (integers) arrives at `N` servers. Each server receives its own independent sub-stream. The overall stream size is too large to be stored on a single machine.
2.  **Real-time Median:** At any point in time, you need to be able to efficiently query the current global median of all the numbers received by all servers so far.  The median does not need to be perfectly accurate. A tolerance is accepted.
3.  **Distributed System:** The system consists of `N` worker servers and a central coordinator.
4.  **Communication Constraints:**  Minimize the amount of data transferred between servers and the coordinator.  Bandwidth is a scarce resource.
5.  **Accuracy Requirement:** The reported median must be within a specified error tolerance `epsilon` of the true median.  `epsilon` will be a floating point number between 0 and 0.5 exclusive (0 < `epsilon` < 0.5).
6.  **Efficiency:** The system must be efficient in terms of both computation time and memory usage. The processing of new data on each server should not significantly impact its performance.
7.  **Query Frequency:** Queries for the current median can arrive at any time and with potentially high frequency.
8.  **Scalability:** The system should be designed to handle a large number of servers (`N`) and a high data ingestion rate.

**Your Task:**

Design and implement a Python solution that simulates this distributed system. You will need to implement the following components:

*   **Worker Server:**
    *   Receives a stream of numerical data.
    *   Maintains a data structure to track the approximate distribution of the numbers it has received.
    *   Periodically sends a summary of its data distribution to the central coordinator.
    *   Must be efficient in memory usage.
*   **Central Coordinator:**
    *   Receives data distribution summaries from all worker servers.
    *   Merges these summaries to create a global view of the data distribution.
    *   Efficiently calculates the approximate global median based on the merged data distribution.
    *   Handles queries for the current median, returning a value within the specified `epsilon` tolerance.

**Input:**

*   `N`: The number of worker servers (integer).
*   `epsilon`: The error tolerance for the median calculation (float, 0 < `epsilon` < 0.5).
*   `data_streams`: A list of `N` lists, where each inner list represents the data stream received by a worker server.  Each number stream is a list of integers.
*   `queries`: A list of timestamps (integers), representing the points in time when a median query is received.  Assume that the data stream is processed sequentially, so a query at time `t` means to consider all data up to time `t` from all streams. The length of the queries list is `Q`.

**Output:**

*   A list of `Q` floating-point numbers, where each number is the approximate global median at the corresponding query time.

**Constraints:**

*   1 <= `N` <= 100
*   0 < `epsilon` < 0.5
*   1 <= Length of each `data_stream` <= 1000
*   1 <= `queries[i]` <= sum(len(stream) for stream in `data_streams`)
*   All numbers within the data streams are integers within the range [-10000, 10000].
*   You should aim to minimize the amount of data sent from the workers to the coordinator while maintaining the accuracy requirement.
*   The frequency of summary updates sent from workers to the coordinator will impact both accuracy and bandwidth usage. Choose an appropriate strategy.

**Considerations:**

*   Think about efficient data structures for representing the data distribution on each worker server.  Histograms, quantile sketches (like GK sketches or t-digests), or other similar techniques could be useful.
*   Consider the trade-offs between accuracy, communication overhead, and computational complexity when designing your system.
*   How frequently should worker servers send updates to the coordinator? What information should be included in these updates?
*   How can the coordinator efficiently merge the data distributions from all worker servers?
*   How can the median be efficiently estimated from the merged data distribution, while respecting the `epsilon` tolerance?

This problem requires a deep understanding of distributed systems, data structures, and algorithms. Good luck!
