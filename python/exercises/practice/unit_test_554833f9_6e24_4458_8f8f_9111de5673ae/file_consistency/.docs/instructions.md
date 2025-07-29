Okay, here's a problem designed to be challenging and suitable for a high-level programming competition, focusing on efficiency, design, and handling complex constraints.

## Project Name

```
Distributed-File-System-Consistency
```

## Question Description

You are tasked with designing a simplified model of a distributed file system and implementing a consistency check mechanism. The file system consists of `N` nodes, each storing chunks of data that make up a set of files. Each file is divided into multiple chunks, and these chunks are replicated across different nodes for redundancy and availability.

The challenge is to determine if the replicas of all the chunks across the distributed file system are consistent. Due to network issues, node failures, and concurrent writes, inconsistencies can arise.

**Specifically, you are given the following:**

*   **`N`:** The number of nodes in the distributed file system, numbered from `0` to `N-1`.
*   **`files`:** A list of files in the system. Each file is represented as a string identifier. Assume file names are unique.
*   **`chunk_map`:** A dictionary (or similar data structure) where:
    *   Keys are file names (strings).
    *   Values are lists of chunk identifiers (strings). Each chunk identifier is unique within a file.
*   **`node_data`:** A list (of length `N`) of dictionaries representing the data stored on each node.  For each node `i`, `node_data[i]` is a dictionary where:
    *   Keys are chunk identifiers (strings). These are *all* chunk identifiers present in the entire file system.
    *   Values are byte strings representing the data stored in that chunk on that node.  If a node does *not* have a particular chunk, the corresponding entry in the dictionary is `None`.

**Your task is to write a function `are_chunks_consistent(N, files, chunk_map, node_data)` that returns `True` if all replicas of all chunks are consistent across all nodes, and `False` otherwise.**

**Consistency is defined as follows:**

Two replicas of the *same* chunk (same file, same chunk identifier) are considered consistent if they contain identical byte strings. If a node contains `None` for a chunk, it's considered as *not* holding a replica of that chunk and thus doesn't participate in the consistency check for that chunk. Only nodes that *do* have data for a specific chunk need to have the same data to be considered consistent.

**Constraints and Edge Cases:**

*   `1 <= N <= 100`
*   The number of files can be up to 100.
*   The number of chunks per file can be up to 100.
*   The size of each chunk can be up to 1MB.
*   A node may not contain any chunks.
*   A node may contain all chunks.
*   The `node_data` may contain chunks that are not part of any of the files listed in `files` and `chunk_map`. These chunks should be ignored.
*   The byte strings in `node_data` can be empty (`b''`). An empty byte string should be considered consistent with another empty byte string.
*   If no node has a chunk (i.e., all entries for a given chunk across all nodes are `None`), the chunk is considered consistent.

**Efficiency Requirements:**

Your solution should be efficient in terms of both time and space complexity.  A naive solution that compares all pairs of replicas for each chunk will likely be too slow for larger datasets.  Consider using appropriate data structures and algorithms to optimize your solution.

**Example:**

```python
N = 3
files = ["file1", "file2"]
chunk_map = {
    "file1": ["chunk1", "chunk2"],
    "file2": ["chunk3"]
}
node_data = [
    {
        "chunk1": b"hello",
        "chunk2": b"world",
        "chunk3": b"python"
    },
    {
        "chunk1": b"hello",
        "chunk2": b"world",
        "chunk3": b"java"
    },
    {
        "chunk1": None,
        "chunk2": b"world",
        "chunk3": None
    }
]

are_chunks_consistent(N, files, chunk_map, node_data) # Should return False, because chunk3 is inconsistent (python vs java)
```

**Rationale for Difficulty:**

*   **Data Structure Management:** Requires careful handling of dictionaries and lists to represent the distributed file system state.
*   **Edge Case Handling:** Numerous edge cases related to missing chunks, empty chunks, and inconsistencies need to be considered.
*   **Efficiency:**  The size constraints force the solver to think about efficient algorithms to avoid quadratic time complexity.  A good solution will likely involve hashing or other methods to quickly compare chunk data.
*   **Real-World Relevance:**  Models a simplified but important aspect of distributed systems consistency, which is a core concept in cloud computing and large-scale data processing.
*   **System Design Consideration:**  While not a full system design problem, the problem forces the solver to think about how data is organized and accessed in a distributed environment.
