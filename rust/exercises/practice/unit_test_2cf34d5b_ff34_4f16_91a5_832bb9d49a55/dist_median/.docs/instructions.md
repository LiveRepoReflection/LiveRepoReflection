Okay, I'm ready to create a challenging Rust coding problem. Here it is:

**Project Name:**

```
distributed-median
```

**Question Description:**

You are building a distributed system that needs to calculate the running median of a stream of integers.  The stream is distributed across multiple worker nodes, each receiving a subset of the data.  Your task is to implement a mechanism to efficiently maintain and query the global median as new data arrives at the worker nodes.

Specifically, you need to implement a `Coordinator` and `Worker` system.

*   **Worker:** Each `Worker` receives a stream of integers. Workers should maintain a local data structure to efficiently track their own local numbers.
*   **Coordinator:** The `Coordinator` receives updates from the workers and maintains the necessary global state to calculate the running median. The Coordinator needs to handle a large number of workers efficiently. The coordinator needs to be able to compute the running median whenever requested.

**Requirements:**

1.  **Real-time Median:** The `Coordinator` must be able to efficiently calculate the median at any point in time, reflecting all data received so far from all workers.
2.  **Scalability:** The system must be able to handle a large number of `Worker` nodes (e.g., 10,000+) and a high volume of data updates.  Consider memory usage and computational complexity.
3.  **Numerical Stability:** Handle potential integer overflow or precision issues when calculating the median, especially with a large dataset. You can assume the input integers are within the i32 range.
4.  **Concurrency:** The `Coordinator` should be able to handle concurrent updates from multiple `Worker` nodes.
5.  **Efficiency:** Minimize the time complexity of both updating the `Coordinator` with new data and querying the median. Aim for logarithmic or amortized logarithmic time complexity for these operations where possible.
6.  **Clear API:** Provide a clear and well-defined API for the `Coordinator` and `Worker` interaction.
7.  **Median Definition:** The median is calculated as follows:
    *   If the total number of elements is odd, the median is the middle element when the elements are sorted.
    *   If the total number of elements is even, the median is the average of the two middle elements when the elements are sorted.

**Constraints:**

*   Assume the network communication between the `Worker` and `Coordinator` is reliable (no packet loss). Focus on the algorithmic aspects of median calculation.
*   You don't need to implement the actual network communication.  Instead, simulate the communication using appropriate data structures and function calls.
*   The number of integers sent by each worker is not known in advance.
*   The `Coordinator` should not store all the integers received. (Memory constraints).
*   The total number of integers across all workers can be very large (billions).

**Bonus (Optional):**

*   Implement a persistence mechanism for the `Coordinator`'s state, allowing it to recover from failures.
*   Explore different data structures and algorithms for the `Coordinator` to optimize performance, considering factors like memory usage, update speed, and query speed.  Justify your design choices.
*   Provide a mechanism to estimate the accuracy of the median if the memory usage is limited.

This question requires a solid understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
