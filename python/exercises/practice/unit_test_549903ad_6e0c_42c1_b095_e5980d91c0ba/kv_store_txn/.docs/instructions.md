## Question: Distributed Transactional Key-Value Store with Consensus

### Question Description

You are tasked with designing and implementing a simplified distributed transactional key-value store. This store needs to handle a high volume of concurrent requests while ensuring data consistency and fault tolerance.

**System Requirements:**

1.  **Key-Value Operations:** The store should support basic key-value operations: `put(key, value)` and `get(key)`. Keys and values are strings.

2.  **Transactions:** The store must support ACID (Atomicity, Consistency, Isolation, Durability) transactions. A transaction can consist of multiple `put` and `get` operations. Transactions must be serializable (isolation level).

3.  **Distribution:** The store is distributed across multiple nodes. Assume a cluster of `N` nodes, where `N` can be 3, 5, or 7.

4.  **Consensus:** A consensus algorithm (e.g., Raft, Paxos) must be implemented to ensure that all nodes agree on the order of transactions and the state of the key-value store. You do *not* need to implement the consensus algorithm itself. You can use a simplified, in-memory simulation of a consensus module with the following API:

    ```python
    class ConsensusModule:
        def propose(self, transaction):
            """
            Proposes a transaction to the consensus group. Blocks until the transaction is committed.
            Returns True if the transaction was successfully committed, False otherwise (e.g., leader failure).
            """
            pass

        def get_committed_transactions(self):
            """
            Returns a list of committed transactions in the order they were committed.
            """
            pass
    ```

5.  **Fault Tolerance:** The system must be able to tolerate `f` failures, where `f = (N-1)/2`. This means that even if `f` nodes fail, the system should still be able to process transactions.

6.  **Concurrency:** The system must handle concurrent requests efficiently. Multiple clients should be able to submit transactions simultaneously.

7.  **Linearizability:** The system must exhibit linearizability. This means that the results of the operations must appear as if they were executed in a single, global order.

**Constraints:**

*   **Memory Limits:** Each node has limited memory. You should design your data structures to minimize memory usage.
*   **Latency:** The system should provide low latency for both `get` and `put` operations.
*   **Scalability:** The system should be designed to scale to a large number of keys and transactions.
*   **No External Libraries (Mostly):** You can use basic data structures and threading primitives provided by Python. However, you are **not** allowed to use external libraries for consensus or distributed transactions. You can use simple logging library if you want.

**Implementation Details:**

1.  **Transaction Management:** Implement a transaction manager that handles the start, commit, and rollback of transactions.
2.  **Data Storage:** Choose an appropriate data structure to store the key-value data on each node. Consider the trade-offs between memory usage, read performance, and write performance.
3.  **Concurrency Control:** Implement a concurrency control mechanism to ensure isolation between transactions. Consider using locking or optimistic concurrency control.
4.  **Consensus Integration:** Integrate your transaction manager with the simulated `ConsensusModule`. Ensure that all transactions are proposed to the consensus group before being committed.
5.  **Failure Handling:** Implement mechanisms to handle node failures. If a node fails, the system should be able to recover and continue processing transactions.

**Input/Output:**

*   You are expected to implement the `put(key, value)` and `get(key)` methods within a `KeyValueStore` class.
*   The `ConsensusModule` is provided as a black box.
*   You are not required to implement the node discovery or cluster management mechanisms. Assume that all nodes are known and accessible.

**Grading Criteria:**

*   **Correctness:** The system must correctly implement all the required features, including transactions, distribution, and consensus.
*   **Performance:** The system should provide low latency and high throughput.
*   **Fault Tolerance:** The system must be able to tolerate node failures.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Efficiency:** The system should use memory and CPU resources efficiently.

This problem requires a deep understanding of distributed systems concepts, including consensus, transactions, concurrency control, and fault tolerance. It also requires strong programming skills and the ability to design and implement complex systems. Good luck!
