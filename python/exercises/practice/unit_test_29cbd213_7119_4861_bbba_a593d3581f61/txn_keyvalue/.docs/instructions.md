## Question: Distributed Transactional Key-Value Store with Snapshot Isolation

### Question Description

You are tasked with designing and implementing a simplified, in-memory, distributed transactional key-value store. This store guarantees snapshot isolation across multiple nodes.

**System Overview:**

The system comprises multiple nodes, each holding a portion of the data. Data is not replicated; each key exists on only one node (determined by a simple hashing function, `node_id = hash(key) % num_nodes`). Clients can connect to any node to initiate transactions.

**Transaction Model:**

*   Transactions are atomic, consistent, isolated, and durable (ACID). However, due to the in-memory nature, durability is relaxed to mean "durable within the lifespan of the node."
*   **Snapshot Isolation:** Each transaction operates on a consistent snapshot of the data as it existed at the transaction's start time. Reads within a transaction always see the same version of the data, regardless of concurrent writes by other transactions.
*   Transactions can perform `read(key)` and `write(key, value)` operations.
*   Transactions must explicitly `commit()` or `abort()`.
*   There is no support for distributed transactions across multiple nodes, meaning one transaction operates on only one node.

**Core Requirements:**

1.  **Node Implementation:** Implement a `Node` class/structure that manages its local key-value store and handles transaction requests.
2.  **Transaction Management:** Implement a `Transaction` class/structure that tracks read and write operations, ensuring snapshot isolation.
3.  **Concurrency Control:** Implement a mechanism to handle concurrent transactions, ensuring data consistency and isolation.  Consider using techniques like Multi-Version Concurrency Control (MVCC) or similar.
4.  **Hashing Function:** Implement a simple hashing function that determines which node a key belongs to.
5.  **Client Interface:** Provide a simple client interface for initiating transactions, reading, writing, committing, and aborting.

**Constraints and Considerations:**

*   **In-Memory:** The entire key-value store resides in memory.
*   **No Replication:** Data is not replicated across nodes.
*   **Single-Node Transactions:** Each transaction is confined to a single node.
*   **No Distributed Transactions:** You do not need to implement transactions that span multiple nodes.
*   **Memory Efficiency:** Strive for memory efficiency, especially when dealing with multiple versions of data for MVCC.
*   **Scalability:** Consider how your design might scale to a larger number of nodes, even though you are only implementing a single node.
*   **Performance:** Optimize for read and write performance, considering the overhead of snapshot isolation.
*   **Deadlock Avoidance:**  Your design should inherently avoid deadlocks.
*   **Error Handling:** Implement proper error handling for cases like key not found, transaction conflicts, etc.
*   **Concurrency:** Your solution must be thread-safe and handle concurrent transactions gracefully.

**Input/Output:**

The interface to your implementation is a function to start a transaction, read a key's value within a transaction, write a key's value within a transaction, commit a transaction, and abort a transaction. All transaction operations happen on the node it is assigned to.

**Example Usage:**

```python
# Assuming you have Node, Transaction, and hashing function implemented
node = Node(node_id=0)

# Client connects to node 0 and starts a transaction
transaction_id = node.start_transaction()

# Transaction reads value of key "x" (initially None)
value = node.read(transaction_id, "x")
print(f"Value of x in transaction {transaction_id}: {value}") # Output: None

# Transaction writes value 10 to key "x"
node.write(transaction_id, "x", 10)

# Transaction reads value of key "x" again (should be 10)
value = node.read(transaction_id, "x")
print(f"Value of x in transaction {transaction_id}: {value}") # Output: 10

# Client commits the transaction
node.commit(transaction_id)

# Another transaction reads the committed value
transaction_id2 = node.start_transaction()
value = node.read(transaction_id2, "x")
print(f"Value of x in transaction {transaction_id2}: {value}") # Output: 10

node.commit(transaction_id2)

# Start another transaction and write "y"
transaction_id3 = node.start_transaction()
node.write(transaction_id3, "y", 20)

# Abort the transaction
node.abort(transaction_id3)

# Start another transaction to verify aborted value isn't there
transaction_id4 = node.start_transaction()
value = node.read(transaction_id4, "y")
print(f"Value of y in transaction {transaction_id4}: {value}") # Output: None
node.commit(transaction_id4)

```

**Judging Criteria:**

*   **Correctness:** The implementation must correctly implement snapshot isolation and handle concurrent transactions without data corruption.
*   **Efficiency:** The implementation should be memory-efficient and provide reasonable read/write performance.
*   **Scalability:**  The design should be scalable in terms of the number of keys and concurrent transactions.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Error Handling:** The implementation should handle errors gracefully and provide informative error messages.
*   **Concurrency Handling:** The implementation should correctly handle concurrent transactions.

This problem requires a deep understanding of concurrency control mechanisms and data structures. Good luck!
