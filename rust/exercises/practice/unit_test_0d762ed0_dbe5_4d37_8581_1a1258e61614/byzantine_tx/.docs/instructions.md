## Problem: Distributed Transaction Coordinator with Byzantine Fault Tolerance

**Description:**

You are tasked with building a simplified, but robust, distributed transaction coordinator in Rust. The system manages transactions across multiple independent storage nodes (simulated as in-memory data structures within the program).  The key challenge is to ensure atomicity and consistency even when some storage nodes might exhibit *Byzantine faults* – i.e., they can behave arbitrarily, including sending incorrect data, lying about their state, or even colluding.

**System Model:**

*   **Storage Nodes:** There are `N` storage nodes. Each node stores a key-value store (HashMap<String, String>). Each node is independent, has no shared memory, and communicates only via messages.
*   **Coordinator:** A single coordinator orchestrates the transactions.
*   **Clients:** Clients send transaction requests to the coordinator.
*   **Transactions:**  A transaction consists of a set of read and write operations on the key-value stores across the storage nodes.  Each operation is specified as a tuple: `(node_id: usize, operation_type: OperationType, key: String, value: Option<String>)`.  `OperationType` is either `Read` or `Write`.  For `Write`, the `value` is `Some(String)`. For `Read`, the `value` is `None`.

**Requirements:**

1.  **Atomicity:** Either all operations in a transaction are applied, or none are.
2.  **Consistency:** After a transaction completes, the system must be in a consistent state.  Even with Byzantine faults, the "honest" nodes (those behaving correctly) should agree on the committed state.
3.  **Byzantine Fault Tolerance:** The system must tolerate up to `f` Byzantine faulty storage nodes, where `N = 3f + 1` (i.e., at least 2/3+1 nodes must be correct).
4.  **Serialization:** Transactions must be executed serially.  No concurrent transactions are allowed.
5.  **Performance:** The coordinator should minimize the number of messages exchanged and the amount of time spent in decision-making.  While perfect performance is impossible with Byzantine fault tolerance, aim for efficiency.  Excessive message complexity will be penalized.

**Specific Implementation Details:**

*   Implement a `Coordinator` struct with methods for:
    *   `new(num_nodes: usize)`: Initializes the coordinator with the specified number of storage nodes.  The number of nodes *must* satisfy `N = 3f + 1` for some `f >= 0`. The coordinator should initialize its internal state, including connections to the storage nodes (simulated within the program; no actual networking needed).
    *   `execute_transaction(transaction: Vec<(usize, OperationType, String, Option<String>)>) -> Result<(), String>`: Executes the given transaction.  Returns `Ok(())` on success, or `Err(String)` on failure.

*   Implement an `OperationType` enum with variants `Read` and `Write`.

*   Implement a simple fault injection mechanism.  The coordinator should be able to designate a subset of the storage nodes as Byzantine faulty before a transaction is executed.  Faulty nodes should exhibit arbitrary behavior (e.g., return incorrect values for reads, refuse to acknowledge messages, or disagree with each other about the transaction outcome).  The fault injection should be controllable via a method on the Coordinator, e.g., `set_faulty_nodes(node_ids: Vec<usize>)`.

*   **Consensus:** Use a Byzantine Fault Tolerant consensus algorithm (e.g., Practical Byzantine Fault Tolerance (PBFT) or a simplified variant) to ensure that the storage nodes agree on the outcome of the transaction.  You may adapt a pre-existing, *correct* implementation of PBFT or similar, but must provide clear attribution.  Explain your choice of algorithm and its suitability for this specific problem.  Your own implementation of the consensus mechanism will be reviewed carefully.

**Constraints:**

*   The number of storage nodes `N` will be relatively small (e.g., 4 to 10).
*   The size of the key-value store in each node is also limited.
*   Transaction size will be small (e.g., fewer than 10 operations).
*   The primary focus is on correctness and Byzantine fault tolerance, not raw throughput.
*   Your solution *must* be memory-safe and avoid data races.  Rust's ownership and borrowing system should be leveraged to ensure this.

**Judging Criteria:**

*   **Correctness:**  The solution must correctly implement atomicity and consistency even in the presence of Byzantine faults.  Test cases will include scenarios with various numbers of faulty nodes exhibiting different types of malicious behavior.
*   **Byzantine Fault Tolerance:** The solution must tolerate up to `f` Byzantine faulty nodes, where `N = 3f + 1`.
*   **Code Clarity and Readability:** The code should be well-structured, commented, and easy to understand.
*   **Efficiency:** While not the primary focus, the solution should be reasonably efficient in terms of message complexity and execution time.  Avoid unnecessary computations or message exchanges.
*   **Rust Best Practices:**  The solution should adhere to Rust's best practices for memory safety, error handling, and code organization.
*   **Explanation:**  A clear explanation of the chosen consensus algorithm, its implementation details, and the rationale behind design decisions is required.  This should be included as comments in the code.

This problem requires a deep understanding of distributed systems, consensus algorithms, and Byzantine fault tolerance. It also demands strong Rust programming skills to ensure correctness, memory safety, and reasonable performance. Good luck!
