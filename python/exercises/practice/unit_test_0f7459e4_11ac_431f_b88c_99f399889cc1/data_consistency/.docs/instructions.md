## Project Name

```
Distributed File System Consistency Checker
```

## Question Description

You are tasked with building a consistency checker for a simplified distributed file system. The file system consists of multiple nodes, each storing potentially overlapping chunks of data. Due to network issues and asynchronous writes, data inconsistencies can arise between nodes. Your goal is to design an efficient algorithm to identify and report these inconsistencies.

**System Model:**

*   The file system consists of `N` nodes, numbered from `0` to `N-1`.
*   A file is divided into `M` chunks, numbered from `0` to `M-1`.
*   Each node stores a subset of these chunks.
*   Each chunk is identified by its index (an integer from 0 to M-1).
*   Each chunk has a version number (a non-negative integer).
*   A node's data is represented as a dictionary/map where the key is the chunk index and the value is the chunk's version number.
*   The input is a list of `N` dictionaries, representing the data stored on each node.  `data[i]` is the dictionary for node `i`.

**Task:**

Write a function that takes the list of node data dictionaries as input and identifies inconsistent chunks. A chunk is considered inconsistent if its version number differs across the nodes that store it.

Your function should return a list of tuples. Each tuple represents an inconsistency and contains the following elements:

*   `chunk_index`: The index of the inconsistent chunk.
*   `node_ids`: A list of node IDs that store this chunk.
*   `version_numbers`: A list of version numbers for this chunk across the listed nodes, corresponding to the `node_ids`.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes)
*   `1 <= M <= 1000` (Number of chunks)
*   Chunk version numbers are non-negative integers and fit within a standard integer data type.
*   The size of the data stored on each node can vary.
*   Optimize for efficiency.  A naive solution with O(N^2 * M) complexity might not pass all test cases.  Consider solutions with better time complexity.

**Example:**

```python
data = [
    {0: 1, 1: 2, 2: 3},  # Node 0
    {0: 1, 1: 3},       # Node 1
    {1: 2, 2: 4}        # Node 2
]

# Expected output:
# [(1, [0, 1, 2], [2, 3, 2]), (2, [0, 2], [3, 4])]
```

**Clarifications:**

1.  If a node does not store a particular chunk, it should not be considered when checking for inconsistencies for that chunk.
2.  The order of tuples in the output list and the order of node IDs within a tuple does not matter.
3.  The version numbers in the tuple MUST correspond to the order of node_ids.
4.  The same chunk should only appear once in the output list, even if there are multiple inconsistencies involving different sets of nodes.
5.  The function should be implemented in Python.

**Bonus (Optional, but recommended for a truly excellent solution):**

*   Consider how the solution would scale if the number of nodes and chunks increased significantly (e.g., `N = 100,000`, `M = 1,000,000`).  What data structures or optimizations could be employed to handle such large datasets efficiently? This doesn't necessarily need to be implemented, but demonstrate that your solution could be adapted to handle the scale.
*   Handle the case where the input data contains errors (e.g., invalid chunk indices, malformed data). Your solution should gracefully handle these errors and avoid crashing.
