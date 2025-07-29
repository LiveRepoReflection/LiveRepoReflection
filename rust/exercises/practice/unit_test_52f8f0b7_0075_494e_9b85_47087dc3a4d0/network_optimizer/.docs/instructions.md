Okay, I'm ready. Here's a challenging Rust coding problem, designed to be difficult and nuanced:

### Project Name

`NetworkOptimizer`

### Question Description

You are tasked with designing a network optimization algorithm for a distributed system. The system consists of `n` nodes, each identified by a unique integer ID from `0` to `n-1`. Nodes communicate with each other by sending messages.  The network topology is represented by a weighted, directed graph where the nodes are vertices and the ability to send messages between two nodes is an edge.  The weight of an edge `(u, v)` represents the latency (in milliseconds) of sending a message from node `u` to node `v`. If there is no direct route from `u` to `v`, no edge exists, the latency is infinite.

The goal is to minimize the average latency for a specific communication pattern. The communication pattern is defined as a set of `m` requests. Each request `(src, dest, size)` indicates that a message of `size` bytes needs to be sent from node `src` to node `dest`.

You are given the following inputs:

*   `n`: The number of nodes in the network.
*   `edge_list`: A vector of tuples, where each tuple `(u, v, latency)` represents a directed edge from node `u` to node `v` with the given `latency`.
*   `requests`: A vector of tuples, where each tuple `(src, dest, size)` represents a communication request from node `src` to node `dest` of a message of size `size`.
*   `bandwidth`: The bandwidth of the network in bytes per millisecond. It constrains the amount of data that can be actively transmitted in a specific time.

Your task is to implement a function `optimize_network` that returns the minimum average latency (in milliseconds) across all `m` requests, subject to the following constraints:

1.  **Path Finding:**  For each request `(src, dest)`, you must find the shortest (lowest latency) path from `src` to `dest` in the network graph. If no path exists, that request is considered failed and contributes a latency of `Infinity` to the average.

2.  **Bandwidth Constraint:** At any given time, the sum of the data being sent across all links cannot exceed the network's total `bandwidth`. The latency of the path is added to a given communication only if the node bandwidth is available at that moment. If it isn't, the communication will have to wait until the node bandwidth is available.

3.  **Parallel Transmission:**  Multiple requests can be processed concurrently, as long as the bandwidth constraint is not violated. You must schedule the transmission of these requests to minimize the overall average latency.

4.  **Optimization:** The goal is to minimize the *average* latency across all `m` requests.

5.  **Large Datasets**: The size of the network and the number of requests can be very large. The algorithm should be efficient.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= u, v < n`
*   `1 <= latency <= 1000`
*   `1 <= m <= 1000`
*   `0 <= src, dest < n`
*   `1 <= size <= 10000`
*   `1 <= bandwidth <= 10000`

**Output:**

The function should return a `f64` representing the minimum average latency in milliseconds. Return `f64::INFINITY` if all requests fail.

**Example:**

Let's say you have a `bandwidth` of 10 bytes/ms, and you have two parallel requests from node 0 to node 1, each having a latency of 5ms and a size of 10 bytes. Both requests can happen in parallel because the total bandwidth usage is 20 bytes, which will take 2ms (20/10) of total bandwidth usage. Then both requests will complete in 5ms + 2ms = 7ms. The average latency is 7ms.

Good luck! I'm eager to see how you approach this problem.
