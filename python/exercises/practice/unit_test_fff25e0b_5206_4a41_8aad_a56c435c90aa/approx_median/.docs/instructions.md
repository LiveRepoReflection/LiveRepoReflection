## Project Name

```
Distributed-Median-Computation
```

### Question Description

You are tasked with designing a system to efficiently compute the approximate median of a large dataset distributed across multiple worker nodes.  This is a common problem in large-scale data analysis and monitoring.

**System Overview:**

1.  **Data Distribution:** The input data consists of N unsorted integers. These integers are distributed across K worker nodes. Each worker node holds roughly N/K integers. The distribution is not guaranteed to be perfectly uniform.

2.  **Communication:**  Worker nodes can communicate with a central aggregator node.  Communication between worker nodes is *not* allowed. Communication is expensive and should be minimized.

3.  **Central Aggregator:** The central aggregator node has limited memory. It cannot store all N integers from the worker nodes.

4.  **Approximate Median:** The goal is to compute an *approximate* median, not necessarily the exact median. The approximation should be within a specified tolerance `epsilon`. That is, the computed value should be within the range of the true median +/- `epsilon * N`.

**Your Task:**

Implement a function `approximate_median(worker_data, epsilon)` that takes the following inputs:

*   `worker_data`: A list of lists. Each inner list represents the integers held by a single worker node.  For example, `worker_data = [[1, 5, 2, 8], [9, 3, 7, 4], [6, 10]]` represents 3 worker nodes holding different sets of integers.
*   `epsilon`: A floating-point number representing the desired tolerance for the approximate median.  For example, `epsilon = 0.01` means the approximate median should be within 1% of the total number of data points from the true median.

Your function should return a single integer representing the approximate median.

**Constraints and Requirements:**

*   **Large Dataset:** The input dataset N can be very large (up to 10^9 integers).
*   **Limited Aggregator Memory:** The central aggregator node has limited memory.  It can only store a relatively small number of integers (on the order of K * log(N), where K is the number of worker nodes). This constraint necessitates techniques for summarizing or sketching the data from worker nodes.
*   **Minimize Communication:** The amount of data transmitted from worker nodes to the central aggregator node should be minimized. Aim for a solution with communication complexity of O(K * log(N)).
*   **Efficiency:**  The algorithm should be efficient in terms of both time and space complexity.
*   **Correctness:** The computed approximate median should satisfy the given tolerance `epsilon`.
*   **Edge Cases:** Handle edge cases such as empty input datasets, `epsilon = 0`, and worker nodes with no data.
*   **No external libraries:** You cannot use external libraries like `numpy` or `scipy`. Implement the solution using Python's built-in data structures and functions.

**Evaluation:**

Your solution will be evaluated based on:

*   **Accuracy:**  How close the computed approximate median is to the true median.
*   **Communication Cost:** The total number of integers transmitted from worker nodes to the central aggregator.
*   **Time Complexity:** The runtime of the algorithm.
*   **Space Complexity:** The memory usage of the central aggregator node.
*   **Code Clarity:** The readability and maintainability of the code.
