## Problem: Parallel Data Processing and Aggregation with Limited Memory

**Description:**

You are tasked with designing and implementing a system to process a massive dataset of key-value pairs. The dataset is too large to fit into memory on a single machine. You have access to a cluster of machines, each with limited memory. The goal is to efficiently process the data in parallel and aggregate the values for each unique key.

**Input:**

*   A distributed dataset of key-value pairs represented as a collection of files. Each file contains lines of text, where each line is a key-value pair separated by a comma: `key,value`.
    *   The `key` is a string.
    *   The `value` is a double.
*   The number of available machines in the cluster, `N`.
*   A memory limit, `M`, for each machine in the cluster (in MB). This is a *hard* constraint. Exceeding this limit will cause the program to crash.

**Output:**

*   A single file containing the aggregated key-value pairs, where the value for each key is the *sum* of all values associated with that key in the input dataset. The output file should be sorted alphabetically by key. The format should be identical to the input: `key,aggregated_value`.

**Constraints:**

*   The dataset size can be significantly larger than the combined memory of all machines in the cluster (e.g., terabytes of data processed by a cluster of machines with a few GB of RAM each).
*   Each machine can only load a small fraction of the entire dataset into memory at any given time (limited by `M`).
*   The number of unique keys can also be very large.
*   The input data is distributed across multiple files. You are free to decide how to access these files.
*   The solution must be parallelized to leverage the available machines in the cluster.
*   The solution must be memory-efficient to avoid exceeding the memory limit `M` on each machine.
*   The solution must be computationally efficient.  Minimize the overall processing time.
*   Ensure numerical stability when summing the double values to avoid potential precision issues with very large datasets.
*   Handle potential errors gracefully, such as malformed input data.  Invalid key-value pairs should be logged but should *not* halt processing.  Do *not* include them in the final output.

**Considerations:**

*   Different parallel processing strategies (e.g., map-reduce, data partitioning) can be used, each with its own trade-offs.
*   Intermediate data storage and communication between machines are crucial aspects of the design.
*   The choice of data structures can significantly impact performance and memory usage. Consider using space-efficient data structures.
*   External sorting algorithms might be necessary to produce the final sorted output.
*   Think about the optimal number of partitions and how data is distributed across the machines to minimize communication overhead and maximize parallelism.

**Bonus:**

*   Implement a mechanism to handle machine failures during processing.
*   Provide metrics on resource usage (CPU, memory, disk I/O) during execution.
*   Allow the number of machines, `N`, to be configurable at runtime.

This question requires a strong understanding of data structures, algorithms, parallel processing, and system design principles.  The limited memory constraint forces candidates to think creatively about how to process massive datasets efficiently. The multiple considerations and the bonus tasks further increase the complexity of the question. Good luck!
