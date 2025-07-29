Okay, here is a challenging coding problem designed with the specified criteria in mind.

## Question: Distributed Transactional Key-Value Store

### Question Description

You are tasked with designing a simplified, in-memory, distributed transactional key-value store. The system consists of multiple nodes that can participate in transactions. Each node stores a subset of the total data, and transactions can involve multiple nodes. You need to implement a system that guarantees ACID (Atomicity, Consistency, Isolation, Durability - although durability is simplified to in-memory persistence for this problem).

**Core Functionality:**

1.  **`get(key: str) -> str | None`:** Retrieves the value associated with a key. Returns `None` if the key does not exist.

2.  **`put(key: str, value: str) -> None`:**  Stores a key-value pair. Overwrites existing values.

3.  **`begin_transaction() -> int`:**  Starts a new transaction and returns a unique transaction ID (an integer).

4.  **`transactional_get(transaction_id: int, key: str) -> str | None`:** Retrieves the value associated with a key *within* a given transaction.  If the key does not exist or was not modified within the transaction, it should return the most recent committed value (or `None` if it never existed).

5.  **`transactional_put(transaction_id: int, key: str, value: str) -> None`:**  Stores a key-value pair *within* a given transaction.  The change is not visible outside the transaction until committed.

6.  **`commit_transaction(transaction_id: int) -> bool`:**  Attempts to commit the transaction with the given ID. If all nodes involved in the transaction agree to commit (simulated using a simplified two-phase commit protocol - see below), the changes are made permanent and visible to subsequent reads. Returns `True` on successful commit, `False` on abort.

7.  **`abort_transaction(transaction_id: int) -> None`:**  Aborts the transaction with the given ID. Discards all changes made within the transaction.

**Simplified Two-Phase Commit Protocol:**

For this problem, the "nodes" are represented by your code's data structures. To simulate a distributed environment, the commit process involves a simplified check:

*   During `commit_transaction`, before applying the changes, the function must check if a global flag `global_abort` is set to `True`.  If it is, the transaction must be aborted (return `False`).
*   The `global_abort` flag is external to your Key-Value Store and represents a simulated external failure or conflict.

**Requirements and Constraints:**

*   **Concurrency:** The system must be thread-safe. Multiple transactions can run concurrently.
*   **Isolation:**  Transactions must be isolated. Changes made in one transaction should not be visible to other concurrent transactions until the first transaction commits.
*   **Atomicity:** Transactions must be atomic. Either all changes within a transaction are committed, or none are.
*   **Memory Persistence:**  Data is stored in memory. Durability is not a primary concern (no disk persistence).
*   **Optimization:**  Optimize for read performance (both `get` and `transactional_get`).  Minimize the impact of ongoing transactions on read operations.
*   **Scalability (Conceptual):** While you don't need to actually distribute the system, consider how your design would scale to a large number of nodes and transactions.  Mention any potential bottlenecks or limitations in your approach.
*   **Error Handling:**  Handle invalid transaction IDs gracefully.  For example, attempting to commit or abort a non-existent transaction should raise an appropriate exception.
*   **Global Abort:** In a real-world scenario, a transaction can be aborted if any of the nodes involved cannot commit. For the sake of the test, a global variable will be introduced during test execution. In the commit execution, you need to check if the global variable is set to 'True', and if it is, you should abort the transaction.

**Example Usage (Illustrative):**

```python
store = DistributedKeyValueStore()

# Initial state
store.put("x", "10")

# Transaction 1
tx1_id = store.begin_transaction()
store.transactional_put(tx1_id, "x", "15")
print(store.transactional_get(tx1_id, "x"))  # Output: 15
print(store.get("x")) # Output: 10  (uncommitted value)

# Transaction 2
tx2_id = store.begin_transaction()
store.transactional_put(tx2_id, "y", "20")
print(store.transactional_get(tx2_id, "y"))  # Output: 20
print(store.get("y")) # Output: None (does not exist)


# Commit Transaction 1
success = store.commit_transaction(tx1_id)  # Assume global_abort is False here
print(success) # Output: True
print(store.get("x")) # Output: 15 (committed value)

# Abort Transaction 2
store.abort_transaction(tx2_id)
print(store.get("y")) # Output: None (aborted value)
```

**Deliverables:**

Implement the `DistributedKeyValueStore` class with the methods described above.  Focus on correctness, thread safety, and read performance.  Include comments explaining your design choices and any trade-offs you made. Also, comment on the design choices and scalability concerns of your approach.
