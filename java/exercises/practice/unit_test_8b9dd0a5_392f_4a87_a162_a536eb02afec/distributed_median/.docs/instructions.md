## Project Name

```
distributed-median
```

## Question Description

You are tasked with designing a system to efficiently calculate the running median of a stream of numbers arriving from multiple distributed sources.

**Scenario:**

Imagine a large-scale sensor network where numerous sensors continuously generate numerical readings. These readings are streamed to a central processing unit (CPU) from various locations. Due to network limitations and processing constraints at the sensor level, the data arrives at the CPU in a non-deterministic and potentially out-of-order manner. Your goal is to design an algorithm and data structure that can efficiently compute the median of all received numbers at any given point in time.  The median should be calculated *without* storing all the numbers, as the stream can be extremely large.

**Specific Requirements:**

1.  **Real-time Updates:** The system must be able to efficiently update the median whenever a new number arrives from any sensor.
2.  **Distributed Sources:** The input data arrives from multiple independent sources (think of them as separate threads or network connections). The system should handle concurrent updates from these sources correctly.
3.  **Memory Constraint:** You are severely limited in the amount of memory you can use. Storing all incoming numbers is not an option. The memory usage must be significantly less than the total number of elements seen so far.  Consider the space complexity of your data structures.
4.  **Efficiency:** The time complexity for updating the median after receiving a new number should be as low as possible. Aim for logarithmic time complexity or better.
5.  **Correctness:** The calculated median must be accurate at any point in time. For an even number of elements, the median should be the average of the two middle elements.
6.  **Scalability:** While you are solving this problem for a single CPU, consider how your design could be adapted to a distributed computing environment (though you don't need to implement the distributed version).  What are the challenges of extending your solution to multiple machines?

**Input:**

The input is a stream of integers arriving from multiple (at least 2) sources/threads. Your solution should simulate this stream.

**Output:**

Your code needs to provide a function or method called `getMedian()` that returns the current median of all numbers received so far. This function should be callable at any time after a number has been added to the stream.

**Constraints:**

*   The range of input integers is -10<sup>9</sup> to 10<sup>9</sup>.
*   The number of concurrent sources/threads is between 2 and 100.
*   You cannot store all the input numbers.
*   The `getMedian()` method must have a time complexity of O(1) or O(log n) in the average case, where n is the number of elements received so far.
*   The memory usage must be significantly less than the number of elements received so far. A memory usage of O(sqrt(n)) or O(log n) would be acceptable.
*   The code must be thread-safe to handle concurrent updates from multiple sources.

**Bonus:**

*   Implement a mechanism to handle delayed or out-of-order arrival of data from different sources.
*   Provide a justification for your data structure choices, including the trade-offs between time complexity, space complexity, and implementation complexity. Discuss how your solution scales to a distributed environment. What are the bottlenecks and how can they be addressed?
