Okay, here's a challenging problem designed to test various aspects of algorithm design, data structures, and optimization, tailored for a high-level programming competition:

### Problem Title: Distributed Transaction Commit Protocol Analyzer

### Problem Description:

You are designing a system to analyze the commit logs of a distributed transaction protocol. In a distributed system, transactions often involve multiple nodes. To ensure data consistency, these transactions must either fully commit on all participating nodes or fully rollback. This is often achieved using a two-phase commit (2PC) protocol or similar consensus-based protocols.

Your task is to write a program that analyzes a set of transaction logs from multiple nodes and determines whether the transactions were successfully committed, rolled back, or are in an indeterminate state due to missing or incomplete logs.

**Input:**

The input consists of multiple transaction logs. Each transaction log entry has the following format:

`node_id, transaction_id, log_type, timestamp, data`

Where:

*   `node_id`: An integer representing the ID of the node where the log entry was recorded. (1 <= node\_id <= N)
*   `transaction_id`: A unique string identifying the transaction.
*   `log_type`: A string representing the type of log entry. Possible values: "PREPARE", "COMMIT", "ROLLBACK", "VOTE_COMMIT", "VOTE_ROLLBACK".
*   `timestamp`: An integer representing the timestamp of the log entry (Unix epoch time).
*   `data`: A string containing additional data associated with the log entry. This field can be empty or contain relevant information specific to the `log_type`.

The input will be provided as a list of strings, where each string represents a single log entry.

**Assumptions and Constraints:**

*   There are `N` nodes in the distributed system (1 <= N <= 100).
*   The number of log entries can be very large (up to 1,000,000).
*   Timestamps are not necessarily ordered within each node's log.
*   A transaction can have log entries across multiple nodes.
*   A node might crash or experience network issues, leading to missing or incomplete log entries.
*   A transaction can only be in one of three states: COMMITTED, ROLLED_BACK, or INDETERMINATE.
*   Each transaction should have a "PREPARE" log on at least one node before any commit-related or rollback-related log is written.
*   Assume a simplified 2PC protocol where a node votes to commit or rollback after a PREPARE message is received. The coordinator decides based on the votes. If all nodes vote to commit, the transaction is committed. Otherwise, it is rolled back. The coordinator then sends COMMIT or ROLLBACK message to all the nodes.
*   For simplicity, assume there is a single coordinator node for each transaction, but you don't know which node is the coordinator.
*   Assume that there are no duplicated log entries in any single node, but the entries might be duplicated between nodes.

**Output:**

Your program should output a dictionary (or equivalent data structure in your language of choice) where the keys are the `transaction_id` strings and the values are the final states of the transactions. The possible states are:

*   "COMMITTED": All nodes that participated in the transaction have a "COMMIT" log entry.
*   "ROLLED_BACK": At least one node has a "ROLLBACK" log entry, and no nodes have a "COMMIT" log entry.
*   "INDETERMINATE": The transaction's state cannot be determined definitively due to missing or incomplete log entries. This includes cases where a "PREPARE" log exists, but neither "COMMIT" nor "ROLLBACK" logs are consistently present across participating nodes.

**Example:**

```
Input:
[
"1,tx1,PREPARE,1678886400,",
"1,tx1,VOTE_COMMIT,1678886401,",
"2,tx1,PREPARE,1678886402,",
"2,tx1,VOTE_COMMIT,1678886403,",
"1,tx1,COMMIT,1678886404,",
"2,tx1,COMMIT,1678886405,",
"1,tx2,PREPARE,1678886406,",
"2,tx2,PREPARE,1678886407,",
"1,tx2,VOTE_ROLLBACK,1678886408,",
"2,tx2,VOTE_ROLLBACK,1678886409,",
"1,tx2,ROLLBACK,1678886410,",
"2,tx2,ROLLBACK,1678886411,",
"1,tx3,PREPARE,1678886412,",
"2,tx3,PREPARE,1678886413,",
"1,tx3,VOTE_COMMIT,1678886414,"
]

Output:
{
"tx1": "COMMITTED",
"tx2": "ROLLED_BACK",
"tx3": "INDETERMINATE"
}
```

**Grading Criteria:**

*   **Correctness:**  The program must correctly determine the final state of each transaction based on the provided logs.
*   **Efficiency:**  The program must be able to handle large input sizes (up to 1,000,000 log entries) within a reasonable time limit.  Consider optimizing data structures and algorithms.
*   **Robustness:**  The program must handle edge cases and invalid input gracefully.
*   **Code Clarity:**  The code should be well-structured, readable, and maintainable.

**Hints:**

*   Consider using appropriate data structures (e.g., dictionaries, sets) to efficiently store and retrieve log entries.
*   Think about how to handle missing log entries and how to determine which nodes participated in a given transaction.
*   Pay attention to the order of operations and how to handle concurrent transactions.
*   Consider using multithreading or other parallel processing techniques to improve performance.

This problem is designed to be challenging and requires a good understanding of distributed systems concepts, efficient data structures, and algorithm design. Good luck!
