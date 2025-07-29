## Project Name

`Distributed File System Consistency Checker`

## Question Description

You are tasked with designing and implementing a consistency checker for a simplified distributed file system (DFS). The DFS consists of multiple storage nodes (servers) that hold chunks of files. For simplicity, assume each file is broken into fixed-size, non-overlapping chunks, and each chunk is uniquely identified by a chunk ID. Each chunk can be replicated across multiple storage nodes for redundancy.

Your task is to implement a system that can detect inconsistencies in the DFS data across the storage nodes.

Specifically, you are given the following:

1.  A list of storage node addresses (strings representing hostnames or IP addresses).
2.  A function `get_chunk_metadata(node_address)` that simulates querying a storage node and retrieving a list of chunk metadata it holds. The chunk metadata is a dictionary containing the `chunk_id` (string), `version` (integer), and `size` (integer).  Assume that calling this function for a non-existent node or any network issue will result in an exception.

Your system should:

1.  **Collect chunk metadata:** Query each storage node to retrieve its chunk metadata. Handle potential errors during the querying process. If a node is unreachable or returns invalid data, log the error and continue with the remaining nodes. Do not let one failing node crash the entire process.
2.  **Identify inconsistencies:** Compare the metadata of chunks with the same `chunk_id` across all storage nodes.  An inconsistency exists if:
    *   The `version` is different across different replicas of the same chunk.
    *   The `size` is different across different replicas of the same chunk.

3.  **Report inconsistencies:** Generate a report of all detected inconsistencies. The report should be a list of dictionaries. Each dictionary should represent an inconsistency and contain the following keys:
    *   `chunk_id`: The ID of the inconsistent chunk.
    *   `inconsistent_nodes`: A list of tuples, where each tuple contains a node address and the corresponding chunk metadata (dictionary) for that node.
    *   `reason`: A string describing the reason for the inconsistency ("version mismatch" or "size mismatch").

**Constraints and Requirements:**

*   **Scalability:** Your solution should be designed to handle a large number of storage nodes and chunks. Consider the potential performance implications of your design choices.
*   **Error Handling:** Implement robust error handling.  Network errors or invalid data from storage nodes should not crash the system. Log errors appropriately.
*   **Efficiency:**  Minimize the number of network requests. If possible, parallelize the metadata collection process.
*   **Memory Usage:**  Be mindful of memory usage, especially when dealing with a large number of chunks. Avoid loading the entire chunk metadata into memory at once if possible.
*   **Concurrency:** Implement concurrent requests to storage nodes in order to reduce overall processing time.

**Example:**

Let's say you have two storage nodes: `node1` and `node2`.

`node1` returns:

```python
[
  {'chunk_id': 'chunk_1', 'version': 1, 'size': 1024},
  {'chunk_id': 'chunk_2', 'version': 2, 'size': 2048}
]
```

`node2` returns:

```python
[
  {'chunk_id': 'chunk_1', 'version': 2, 'size': 1024},
  {'chunk_id': 'chunk_3', 'version': 1, 'size': 4096}
]
```

The consistency checker should report the following inconsistency:

```python
[
  {
    'chunk_id': 'chunk_1',
    'inconsistent_nodes': [
      ('node1', {'chunk_id': 'chunk_1', 'version': 1, 'size': 1024}),
      ('node2', {'chunk_id': 'chunk_1', 'version': 2, 'size': 1024})
    ],
    'reason': 'version mismatch'
  }
]
```

**Bonus:**

*   Implement a mechanism to automatically retry failed requests to storage nodes.
*   Add logging to record the progress of the consistency check and any errors encountered.
*   Consider adding a configuration option to specify the maximum number of concurrent requests to storage nodes to avoid overloading the network.

This problem requires careful consideration of data structures, algorithms, error handling, concurrency, and scalability, making it a challenging and comprehensive exercise. Good luck!
