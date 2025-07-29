Okay, I understand. Here's a challenging Python coding problem designed to be similar to a LeetCode Hard difficulty:

## Project Name

`Distributed-Median-Tracker`

## Question Description

You are tasked with designing a system for tracking the approximate median of a large stream of numerical data distributed across multiple nodes in a network.  Each node receives a continuous stream of integers and needs to efficiently contribute to a global estimate of the median. Due to network bandwidth limitations, you cannot simply transmit all data to a central server.

Your task is to implement a `MedianTracker` class that operates in a distributed environment. The class should support the following operations:

1.  **`add_value(node_id: str, value: int)`:**  This method is called on a node (identified by `node_id`) to add a new integer `value` to its local data stream. You need to design an efficient way to summarize the data received by each node.

2.  **`estimate_median() -> float`:** This method returns an *approximate* global median of all the data seen across all nodes.  The estimate does not need to be perfectly accurate, but should be reasonably close to the true median.  A trade-off between accuracy and efficiency is expected.

**Constraints and Requirements:**

*   **Scale:** The system must be able to handle a very large number of nodes (potentially thousands) and a massive stream of data per node.
*   **Limited Communication:** Minimize the amount of data transmitted between nodes. You cannot send the entire data stream from each node to a central location.
*   **Approximate Solution:** A perfectly accurate median is not required.  Focus on providing a good approximation with reasonable computational and communication costs. Aim for an error tolerance of within 5% of the true median, although this is not a hard requirement, the lower the better.
*   **Memory Efficiency:** Each node has limited memory and cannot store the entire data stream. Summarization techniques are crucial.
*   **Real-time Considerations:**  While not strictly real-time, the `estimate_median()` operation should complete in a reasonable amount of time, even with a large number of nodes.
*   **Data Distribution:** The data distribution across nodes may be non-uniform. Some nodes might receive significantly more data or data with different statistical properties than others.
*   **Multiple Valid Approaches:** There are several possible approaches to solve this problem, each with its own trade-offs in terms of accuracy, communication overhead, and memory usage. You are encouraged to explore different techniques and justify your design choices.

**Considerations:**

*   **Data Summarization Techniques:** Explore techniques like histograms, quantiles, or other sketching algorithms to summarize the data on each node.
*   **Communication Strategy:**  Consider how nodes communicate their data summaries to a central server (or other nodes) for median estimation.  Periodic updates, gossip protocols, or other distributed communication strategies could be used.
*   **Median Estimation Algorithm:** Choose an appropriate algorithm for estimating the median from the summarized data.  Consider the accuracy and computational complexity of your chosen algorithm.
*   **Handling Skewed Data:** Your solution should be robust to skewed data distributions, where a small number of nodes contribute a large fraction of the data.

This problem requires you to combine knowledge of data structures, algorithms, distributed systems, and optimization techniques. It encourages you to think about the trade-offs between accuracy, efficiency, and communication costs in a distributed environment.  Good luck!
