## Project Name

`Distributed File System Consistency`

## Question Description

You are tasked with designing and implementing a simplified, in-memory distributed file system (DFS) consistency checker. The DFS consists of multiple data nodes (servers) that store chunks of files. A file can be split into multiple chunks, and each chunk can be replicated across different data nodes for redundancy. Your task is to build a tool that verifies the consistency of the file chunks across the data nodes.

**System Overview:**

*   The DFS has `N` data nodes, numbered from `0` to `N-1`.
*   Each file is identified by a unique string `file_id`.
*   A file is divided into `M` chunks, numbered from `0` to `M-1`.
*   Each chunk is represented as a byte array.
*   Each data node stores a subset of these chunks.
*   For each chunk, there is a designated primary data node. The primary data node is responsible for propagating updates to the replicas.
*   Assume all updates are made serially (no concurrent writes).
*   Assume all updates are atomic (a write either fully succeeds or fails).

**Input:**

You are given the following information:

1.  `num_data_nodes: usize`: The number of data nodes in the DFS.
2.  `file_metadata: Vec<(String, usize)>`: A vector of tuples. Each tuple represents a file and the number of chunks it is divided into. `(file_id, num_chunks)`
3.  `data_node_contents: Vec<HashMap<(String, usize), Vec<u8>>>`: A vector representing the contents of each data node. `data_node_contents[i]` is a HashMap representing the chunks stored in data node `i`. The key of the HashMap is a tuple `(file_id, chunk_index)`, and the value is the byte array representing the chunk's data.
4.  `primary_nodes: HashMap<(String, usize), usize>`: A HashMap that stores the primary data node for each chunk. The key is a tuple `(file_id, chunk_index)` and the value is the data node index `usize`.

**Task:**

Implement a function `check_consistency` that takes the above input and returns a `Vec<(String, usize, usize)>`. This vector should contain tuples of `(file_id, chunk_index, data_node_index)` for each inconsistent chunk. A chunk is considered inconsistent if its content differs from the content on its primary node.

**Constraints:**

*   `1 <= num_data_nodes <= 1000`
*   `1 <= number of files <= 100`
*   `1 <= number of chunks per file <= 100`
*   `0 <= chunk_index < num_chunks`
*   `0 <= data_node_index < num_data_nodes`
*   The size of each chunk (byte array) can vary.
*   The primary node for a chunk MUST exist.
*   A data node may not contain all chunks of a file.
*   The same chunk `(file_id, chunk_index)` can exist on multiple data nodes.
*   Consider potential edge cases, such as empty files, empty chunks, missing chunks on some data nodes, and different chunk sizes.
*   The solution should be efficient in terms of both time and space complexity. Aim for better than O(N * M * K * L), where N is the number of data nodes, M is the number of files, K is the number of chunks per file, and L is the average chunk size.

**Example:**

```rust
let num_data_nodes = 2;
let file_metadata = vec![("file1".to_string(), 2)];
let mut data_node_contents: Vec<HashMap<(String, usize), Vec<u8>>> = vec![HashMap::new(), HashMap::new()];
data_node_contents[0].insert(("file1".to_string(), 0), vec![1, 2, 3]);
data_node_contents[0].insert(("file1".to_string(), 1), vec![4, 5, 6]);
data_node_contents[1].insert(("file1".to_string(), 0), vec![1, 2, 3]);
data_node_contents[1].insert(("file1".to_string(), 1), vec![4, 5, 7]); // Inconsistent chunk
let mut primary_nodes: HashMap<(String, usize), usize> = HashMap::new();
primary_nodes.insert(("file1".to_string(), 0), 0);
primary_nodes.insert(("file1".to_string(), 1), 0);

let inconsistent_chunks = check_consistency(num_data_nodes, file_metadata, data_node_contents, primary_nodes);

// Expected output: vec![("file1".to_string(), 1, 1)]
// Because chunk 1 of file1 on data node 1 is inconsistent with its primary node (data node 0)

```

**Bonus:**

*   Implement the solution in a way that can be easily parallelized (using rayon or similar libraries) to improve performance for large DFS deployments. However, consider the overhead of parallelization. The performance gain must be significant enough to justify the added complexity.
*   Consider how you might extend your solution to handle eventual consistency scenarios, where updates are not immediately propagated to all replicas.

This problem requires a good understanding of data structures, algorithms, and distributed systems concepts. Successfully solving it demonstrates proficiency in Rust and the ability to design efficient and robust solutions for complex problems. Good luck!
