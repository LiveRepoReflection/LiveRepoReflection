## Problem: Parallel Data Processing with Fault Tolerance

### Question Description

You are tasked with designing a system for processing a massive dataset in parallel across a cluster of machines. The dataset is represented as a sequence of `N` records, where `N` can be extremely large (e.g., billions). The processing logic for each record is computationally intensive. Due to the distributed nature of the system, machine failures are a possibility, and your system needs to be fault-tolerant.

Your system should adhere to the following constraints and requirements:

1.  **Parallelism:** The processing must be distributed across multiple worker nodes to achieve significant speedup. Assume you have `K` worker nodes available.
2.  **Fault Tolerance:** If a worker node fails during processing, the system should automatically recover and ensure that all records are eventually processed correctly. Minimizing the recomputation required after a failure is crucial.
3.  **Data Partitioning:** Design an efficient strategy to partition the dataset among the worker nodes. Consider the trade-offs between even distribution, data locality (if applicable, though not strictly required in this problem), and the overhead of partitioning.
4.  **Result Aggregation:** After processing, the results from each worker node need to be aggregated into a final output. You don't need to implement the aggregation logic itself, but you need to design the system in a way that the intermediate results are easily aggregatable. Assume that each record produces a single numerical output. The final output is the sum of all these numerical outputs.
5.  **Scalability:** The system should be able to handle a large number of worker nodes and a massive dataset. The design should avoid bottlenecks that would limit scalability.
6.  **Optimization:** Your solution should minimize the overall processing time, considering both computation and communication overhead.

Specifically, you need to implement the following:

*   A `distribute_data(N, K)` function that returns a list of tuples, where each tuple `(start_index, end_index, worker_id)` represents a segment of the dataset assigned to a specific worker node. `start_index` and `end_index` are inclusive.
*   A `process_data(data_segment)` function that simulates the processing of a data segment. This function should return the sum of the simulated record processing results.  For simplicity, simulate the processing of a single record by returning the record's index.
*   A `recover_from_failure(failed_worker_id, N, K)` function that reassigns the failed worker's tasks to the remaining active workers. It should return a list of tuples similar to `distribute_data`, representing the new data distribution.
*   An `aggregate_results(worker_results)` function that takes a list of worker results (sums) and returns the final sum.

**Constraints:**

*   The worker nodes are numbered from 0 to K-1.
*   Assume a single worker can fail at most once.
*   The total number of records, N, can be very large (e.g., 10^9).
*   The number of workers, K, can be large (e.g., 100).
*   The indices should be 0-based.

**Example:**

Let's say N = 10 and K = 2.

Initially, `distribute_data(10, 2)` might return:

`[(0, 4, 0), (5, 9, 1)]`

This means worker 0 processes records 0 through 4, and worker 1 processes records 5 through 9.

If worker 0 fails, `recover_from_failure(0, 10, 2)` might return:

`[(5, 9, 1), (0, 4, 1)]`

This means worker 1 now processes records 5 through 9 and also re-processes the records that worker 0 was responsible for (0 through 4). Note the worker_id is still 1 in this case.

**Scoring:**

The solution will be judged based on:

1.  **Correctness:** The system must correctly process all records and produce the correct final sum, even in the presence of failures.
2.  **Efficiency:** The solution should minimize the total processing time. This includes minimizing the amount of recomputation required after a failure and optimizing the data partitioning strategy.
3.  **Scalability:** The solution should be able to handle a large number of records and worker nodes without significant performance degradation.
4.  **Code Clarity:** The code should be well-structured, easy to understand, and follow good coding practices.

This problem requires a deep understanding of parallel processing concepts, fault tolerance mechanisms, and optimization techniques. Good luck!
