## Project Name

`Distributed Transaction Manager`

## Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager (DTM). This DTM will coordinate transactions across multiple independent resource managers (RMs). Each RM can represent a database, a message queue, or any other system that can perform atomic operations.

**Core Concepts:**

*   **Transaction:** A sequence of operations that must either all succeed (commit) or all fail (rollback).
*   **Resource Manager (RM):** A system that manages resources and can participate in distributed transactions. Each RM has a unique ID. In this problem, you only need to simulate the existence of RMs. No actual database connections are required. You can simulate operations on the RMs by simply printing to the console.
*   **Transaction Manager (TM/DTM):** The central coordinator that manages the global transaction lifecycle, ensuring atomicity and consistency across all participating RMs.
*   **Two-Phase Commit (2PC):** The protocol used by the DTM to coordinate transactions. It consists of two phases:
    *   **Prepare Phase:** The DTM asks all RMs to prepare to commit the transaction. Each RM performs necessary checks (e.g., resource availability, data validation) and votes either "yes" (ready to commit) or "no" (abort).
    *   **Commit/Rollback Phase:** Based on the votes received in the prepare phase, the DTM decides whether to commit or rollback the transaction. It then instructs all RMs to perform the final action.

**Requirements:**

1.  **Implement the following functions:**
    *   `begin_transaction()`: Starts a new global transaction and returns a unique transaction ID (TXID).
    *   `enlist_resource(txid, rm_id)`: Registers a resource manager with a given transaction. A resource manager can only be enlisted in one transaction at a time.
    *   `execute_operation(txid, rm_id, operation)`: Simulates an operation executed within a transaction on a specific resource manager. You can simply print a message indicating that the operation is being executed (e.g., "RM1: Executing operation 'update account balance' for TXID 123").
    *   `prepare_transaction(txid)`: Initiates the prepare phase of the 2PC protocol. The DTM sends a "prepare" request to all enlisted RMs. Each RM simulates whether they are ready to commit by returning `True` or `False`.
    *   `commit_transaction(txid)`: Initiates the commit phase. If all RMs voted "yes" in the prepare phase, the DTM sends a "commit" request to all RMs.
    *   `rollback_transaction(txid)`: Initiates the rollback phase. If any RM voted "no" in the prepare phase, or if any other error occurred, the DTM sends a "rollback" request to all RMs.

2.  **Error Handling:**
    *   Raise appropriate exceptions for invalid operations, such as:
        *   `TransactionNotFound`: If a transaction ID does not exist.
        *   `ResourceManagerNotFound`: If a resource manager ID does not exist.
        *   `ResourceManagerAlreadyEnlisted`: If a resource manager is already enlisted in another transaction.
        *   `InvalidTransactionState`: If an operation is performed on a transaction in an invalid state (e.g., committing a transaction that hasn't been prepared).

3.  **Concurrency:** The DTM should be designed to handle concurrent transactions. Use appropriate locking mechanisms to ensure data consistency and prevent race conditions. Minimize lock contention to maximize throughput.

4.  **Optimization:** Optimize for the scenario where transactions are generally short-lived and involve a small number of RMs.

5.  **Constraints:**
    *   The number of RMs is limited to 100.
    *   Each RM can handle at most 10 concurrent transactions.
    *   The maximum number of concurrent transactions in the system is 1000.
    *   The `execute_operation` function should be non-blocking.
    *   Assume the system is reliable, meaning no RM crashes or network failures occur during the transaction lifecycle.
    *   You don't need to implement persistence; all data can be stored in memory.

**Example Usage:**

```python
dtm = DistributedTransactionManager()

txid1 = dtm.begin_transaction()
dtm.enlist_resource(txid1, "RM1")
dtm.execute_operation(txid1, "RM1", "update account balance")

txid2 = dtm.begin_transaction()
dtm.enlist_resource(txid2, "RM2")
dtm.execute_operation(txid2, "RM2", "send email")

if dtm.prepare_transaction(txid1):
    dtm.commit_transaction(txid1)
else:
    dtm.rollback_transaction(txid1)

# Simulate RM2 voting "no" during the prepare phase
rm2_vote = False
if dtm.prepare_transaction(txid2):
    if rm2_vote:
        dtm.commit_transaction(txid2)
    else:
        dtm.rollback_transaction(txid2)
else:
    dtm.rollback_transaction(txid2)
```

**Evaluation Criteria:**

*   Correctness: The implementation must correctly implement the 2PC protocol and handle all specified error conditions.
*   Concurrency: The implementation must be thread-safe and handle concurrent transactions efficiently.
*   Performance: The implementation should be optimized for short-lived transactions with a small number of RMs.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Resource Management: Efficiently manage resources in a concurrent environment.
