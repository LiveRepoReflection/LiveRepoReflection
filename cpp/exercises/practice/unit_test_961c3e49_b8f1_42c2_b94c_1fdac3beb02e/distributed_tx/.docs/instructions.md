Okay, here's a challenging C++ programming problem, designed to be comparable to LeetCode Hard difficulty, focusing on data structures, optimization, and real-world applicability.

## Problem: Distributed Transaction Coordinator

### Problem Description

You are tasked with implementing a simplified distributed transaction coordinator.  Imagine a system where multiple independent services (databases, message queues, etc.) need to participate in a single, atomic transaction.  If all services successfully commit their part of the transaction, the overall transaction is considered successful. If any service fails to commit, the entire transaction must be rolled back.

Your coordinator will manage these distributed transactions using a two-phase commit (2PC) protocol.  Due to network unreliability and service failures, the coordinator needs to be robust and efficient in its handling of transactions.

**Core Functionality:**

1.  **Transaction Initiation:** The coordinator receives a request to start a new transaction.  The request includes a unique transaction ID (TID) and a list of participating service IDs (SIDs).

2.  **Prepare Phase:**  For each service in the transaction, the coordinator sends a "prepare" message. The service attempts to prepare its local changes for commitment.  The service responds with either "prepared" or "abort".

3.  **Commit/Rollback Phase:**
    *   If *all* services respond with "prepared", the coordinator sends a "commit" message to all services.
    *   If *any* service responds with "abort", or if the coordinator doesn't receive a response from a service within a specified timeout, the coordinator sends a "rollback" message to all services.

4.  **Logging and Recovery:** The coordinator must maintain a durable log of its actions (transaction state, prepare responses, commit/rollback decisions). In case of a crash, the coordinator should be able to recover its state from the log and resume pending transactions.

5.  **Handling Failures:** The coordinator must handle various failure scenarios:
    *   Service unavailable during the prepare phase.
    *   Service failing to respond during the commit/rollback phase.
    *   Coordinator crashing and restarting.

**Input:**

The coordinator will receive commands from standard input.  The commands are text-based and follow a specific format:

*   `BEGIN <TID> <SID1> <SID2> ... <SIDN>`:  Starts a new transaction with ID `<TID>` involving services `<SID1>` to `<SIDN>`.  TIDs and SIDs are positive integers.
*   `PREPARED <TID> <SID>`:  Service `<SID>` has successfully prepared transaction `<TID>`.
*   `ABORT <TID> <SID>`: Service `<SID>` has aborted transaction `<TID>`.
*   `TIMEOUT <TID> <SID>`:  The coordinator timed out waiting for a response from service `<SID>` for transaction `<TID>`.
*   `RECOVER`:  Simulates coordinator recovery from a crash.  The coordinator should read its log and resume any incomplete transactions.  This command can be called at any time.
*   `PRINT_LOG`: Prints the current state of the log, each entry on a new line. The format of the log entries is up to you, but it should be clear and interpretable.
*   `EXIT`: Terminates the coordinator.

**Output:**

The coordinator should print messages to standard output based on its actions.

*   `PREPARE <TID> <SID>`: Sent to service `<SID>` to prepare transaction `<TID>`.
*   `COMMIT <TID> <SID>`: Sent to service `<SID>` to commit transaction `<TID>`.
*   `ROLLBACK <TID> <SID>`: Sent to service `<SID>` to rollback transaction `<TID>`.
*   `TRANSACTION_COMMITTED <TID>`: Printed when transaction `<TID>` has been successfully committed.
*   `TRANSACTION_ABORTED <TID>`: Printed when transaction `<TID>` has been aborted.
*   `UNKNOWN_COMMAND`:  Printed if an invalid command is received.
*   Error messages for any internal errors (e.g., invalid TID, SID).  These should start with "ERROR: ".

**Constraints:**

*   **Scalability:** The coordinator should be able to handle a large number of concurrent transactions and services.
*   **Durability:** The log must be durable. Assume a simple file-based log is sufficient for this problem.  You don't need to implement complex crash recovery mechanisms; simply replaying the log upon `RECOVER` is enough.
*   **Concurrency:**  Multiple commands can arrive simultaneously, and the coordinator must handle them concurrently.  Consider using threads or asynchronous programming.
*   **Efficiency:** The coordinator should minimize the number of messages exchanged and the amount of data written to the log.
*   **Timeout:** Implement a timeout mechanism for the prepare phase.  A reasonable default timeout value (e.g., 100 milliseconds) can be used if no explicit timeout value is provided. The `TIMEOUT` input command is only for simulating a timeout, not for setting the timeout duration.
*   **Idempotency:**  Services might receive the same commit or rollback message multiple times.  They should handle these messages idempotently (i.e., processing the message multiple times has the same effect as processing it once).  *Your coordinator doesn't need to explicitly handle idempotency of the participants. The participants are assumed to be idempotent.*

**Example:**

```
Input:
BEGIN 123 1 2 3
PREPARED 123 1
PREPARED 123 2
ABORT 123 3

Output:
PREPARE 123 1
PREPARE 123 2
PREPARE 123 3
ROLLBACK 123 1
ROLLBACK 123 2
ROLLBACK 123 3
TRANSACTION_ABORTED 123
```

**Judging Criteria:**

*   Correctness: The coordinator must correctly implement the 2PC protocol and handle all failure scenarios.
*   Performance: The coordinator must be efficient in terms of message exchange, logging, and concurrency.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Error Handling: The coordinator must handle errors gracefully and provide informative error messages.

This problem requires a strong understanding of distributed systems concepts, concurrency, and data structures. It challenges you to design and implement a robust and efficient transaction coordinator that can handle various failure scenarios. Good luck!
