Okay, I'm ready to craft a truly challenging coding problem. Here it is:

## Project Name

`distributed-file-system`

## Question Description

You are tasked with designing and implementing a simplified, distributed file system. This file system consists of multiple storage nodes and a metadata server.

**Core Functionality:**

1.  **Data Storage (Storage Nodes):** The file system should be able to store large files. Files are split into chunks of fixed size (e.g., 64MB). Each chunk is uniquely identified by a chunk ID. Storage nodes are responsible for storing these chunks. You can assume storage nodes have infinite storage capacity.

2.  **Metadata Management (Metadata Server):** A single metadata server maintains information about:
    *   Which file is broken into which chunks.
    *   The order of chunks for each file.
    *   The location (storage node IDs) of each chunk. For fault tolerance, each chunk should be replicated on at least `R` different storage nodes (replication factor). The metadata server should implement a simple round-robin chunk distribution strategy.

3.  **File Read:** Given a file path, the system should be able to retrieve the file content. This involves:
    *   Querying the metadata server to get the chunk IDs and their locations.
    *   Reading the chunks from the storage nodes.
    *   Assembling the chunks in the correct order to reconstruct the file. If a chunk is available on multiple storage nodes, the system should attempt to read from them in a round-robin fashion, prioritizing responsiveness. In case all nodes storing a chunk are unresponsive, the system should return an error.

4.  **File Write:** Given a file path and content, the system should be able to store the file. This involves:
    *   Splitting the file into chunks.
    *   Assigning chunk IDs to the chunks.
    *   Choosing `R` storage nodes for each chunk.
    *   Storing the chunks on the chosen storage nodes.
    *   Updating the metadata server with the file metadata.

5.  **Fault Tolerance:** The system should be able to tolerate the failure of storage nodes.  If a storage node becomes unavailable, the system should still be able to read files, assuming the replication factor `R` is sufficient. The metadata server does *not* need to detect node failures. The read operation simply needs to handle unresponsive nodes gracefully.

**Constraints and Requirements:**

*   **Chunk Size:** Define a constant for the chunk size (e.g., 64MB).
*   **Replication Factor (R):** The replication factor `R` will be given as input. `1 <= R <= N` where `N` is the number of storage nodes.
*   **Number of Storage Nodes (N):** The number of storage nodes `N` will be given as input. `1 <= N <= 100`. Storage nodes are identified by integer IDs from `0` to `N-1`.
*   **File Size:** The file size can be very large (up to several GB). You should avoid loading the entire file into memory at once during read or write operations.
*   **Performance:** The read and write operations should be reasonably efficient. Consider using appropriate data structures and algorithms to minimize latency. You will be tested on the speed of reading and writing large files.
*   **Concurrency:** Assume concurrent read and write requests can arrive. The metadata server must handle concurrent requests safely and efficiently. Use appropriate locking mechanisms to prevent race conditions.
*   **Metadata Server Storage:** The metadata server should store its metadata in memory. You do not need to persist the metadata to disk.
*   **Error Handling:** Implement proper error handling. For example, return appropriate error codes if a file does not exist, a storage node is unavailable, or a write operation fails.
*   **Chunk Distribution:** Implement a round-robin distribution of chunks across storage nodes.
*   **Unresponsive Nodes:** A storage node is considered unresponsive if a read request to it times out after a specified timeout. The read operation should try other replicas if available. Define a constant for the read timeout.
*   **No Deletion:** File deletion is not required.

**Input:**

*   `N`: The number of storage nodes.
*   `R`: The replication factor.
*   A series of read and write requests, as specified by the problem instance.

**Output:**

*   For each read request, output the file content.
*   For each write request, output "OK" if the write was successful, or an error message if it failed.

**Example Interaction:**

(This is just illustrative - your code should handle a series of reads and writes as defined by the hidden test cases)

1.  System initializes with `N = 3`, `R = 2`.
2.  Write request: `write("file1.txt", "This is the content of file1.")`
    *   System splits "file1.txt" into chunks (if necessary).
    *   System stores chunks on storage nodes (e.g., chunk1 on nodes 0 and 1).
    *   System updates metadata server.
    *   Output: "OK"
3.  Read request: `read("file1.txt")`
    *   System retrieves metadata for "file1.txt".
    *   System reads chunk1 from either node 0 or 1.
    *   System assembles the file content.
    *   Output: "This is the content of file1."

**Judging Criteria:**

*   **Correctness:** Your code must correctly implement the required functionality.
*   **Efficiency:** Your code must be reasonably efficient in terms of time and memory usage.
*   **Fault Tolerance:** Your code must be able to tolerate the failure of storage nodes.
*   **Concurrency:** Your code must handle concurrent requests safely and efficiently.
*   **Code Quality:** Your code must be well-structured, readable, and maintainable.

This problem requires a good understanding of distributed systems concepts, data structures, algorithms, and concurrency. Good luck!
