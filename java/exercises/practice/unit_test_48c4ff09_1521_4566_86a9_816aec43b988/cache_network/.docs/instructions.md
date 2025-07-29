## Question: Optimizing Network Latency in a Distributed Cache

**Problem Description:**

You are designing a distributed caching system for a large-scale online service. The system consists of `N` cache nodes, each with a limited storage capacity. Requests arrive at a central load balancer which distributes them to the cache nodes. Due to network topology and node processing capabilities, the latency of accessing each cache node from the load balancer varies.

Your goal is to design an efficient request routing strategy that minimizes the average latency experienced by the requests, while also considering cache hit rates.

**Specifics:**

1.  **Cache Nodes:** You are given an array `capacities` of length `N`, where `capacities[i]` represents the storage capacity (in MB) of the i-th cache node.
2.  **Latency:** You are given a 2D array `latencies` of size `N x N`. `latencies[i][j]` represents the latency (in milliseconds) of accessing cache node `j` *from* cache node `i`. `latencies[i][i]` represents latency of accessing cache node `i` from the load balancer. Note that the latency matrix is not necessarily symmetric.
3.  **Requests:** Requests arrive one at a time. Each request is for a specific data item.
4.  **Cache Hit/Miss:** When a request arrives at a cache node, there are two possible outcomes:
    *   **Cache Hit:** The data item is present in the cache node. The request is served with the corresponding latency.
    *   **Cache Miss:** The data item is not present in the cache node. The cache node fetches the item from the origin server (which has a fixed latency of `originLatency` ms), stores it in its cache (if capacity allows, potentially evicting other items based on Least Recently Used(LRU) policy to make space), and serves the request.
5.  **Eviction Policy:**  Each cache node uses an LRU (Least Recently Used) eviction policy when its capacity is full.  New items are added to the cache, and the least recently used item is evicted if space is needed.
6.  **Load Balancer:** The load balancer needs to decide which cache node to route each incoming request to. The decision must be made *before* knowing whether the request will result in a cache hit or a cache miss.
7.  **Objective:** Minimize the average latency of all requests processed by the system.
8.  **Constraints:**
    *   `1 <= N <= 100` (Number of cache nodes)
    *   `1 <= capacities[i] <= 1000` (Capacity of each cache node in MB)
    *   `1 <= latencies[i][j] <= 100` (Latency in milliseconds)
    *   `1 <= originLatency <= 200` (Latency of accessing the origin server)
    *   The size of each data item is 1 MB.
    *   You will be given a sequence of 10,000 requests to process.
    *   The data item requested by each request is an integer ID between 1 and 10,000 (inclusive).
    *   You are not allowed to modify the cache nodes directly; you can only control the routing decisions of the load balancer.
    *   Your solution must execute within a 2-second time limit.

**Input:**

*   `N`: The number of cache nodes.
*   `capacities`: An integer array representing the storage capacity of each cache node.
*   `latencies`: A 2D integer array representing the latency between cache nodes and from the load balancer to each cache node.
*   `originLatency`: An integer representing the latency of accessing the origin server.
*   `requests`: An integer array representing the sequence of data item IDs requested.

**Output:**

*   The average latency of all processed requests (as a double).

**Example:**

```
N = 3
capacities = [10, 5, 8]
latencies = [[10, 15, 20], [15, 8, 12], [20, 12, 5]] (load balancer latency)
originLatency = 50
requests = [1, 2, 1, 3, 2, 4, 1, 5, 6, 2]
```

**Scoring:**

Your solution will be evaluated based on the average latency achieved for a series of test cases. Lower average latency scores higher. Points will also be deducted for solutions that exceed the time limit.

**Challenge:**

This problem requires you to balance several factors:

*   **Latency:**  Choosing the cache node with the lowest latency is not always optimal, as it might lead to cache misses.
*   **Cache Hit Rate:**  Routing requests to nodes that are likely to have the data item can reduce latency.
*   **Cache Capacity:**  The limited capacity of each cache node affects the cache hit rate over time.
*   **LRU Eviction:**  Understanding how LRU affects cache contents is crucial for predicting hit rates.
*   **Dynamic Routing:**  You need to adapt your routing strategy based on the changing state of the cache nodes and the pattern of requests.

Good luck!
