## Question Title: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system manages accounts distributed across multiple independent database shards.  Each shard is responsible for storing and managing a subset of the total accounts.

Your transaction coordinator must ensure ACID (Atomicity, Consistency, Isolation, Durability) properties across these distributed shards when transferring funds between accounts.

**System Requirements:**

1.  **Account Identification:** Each account is uniquely identified by a string `accountId`.

2.  **Shard Mapping:** You are given a function `getShard(accountId)` that, given an `accountId`, returns the shard ID (an integer) where the account's data resides. This function is considered a black box and you cannot modify it.

3.  **Transaction Requests:** The system receives transaction requests in the form of `transfer(fromAccountId, toAccountId, amount)`.

4.  **Two-Phase Commit (2PC):** You must implement a 2PC protocol to guarantee atomicity. This involves a "prepare" phase and a "commit/rollback" phase.

5.  **Shard Communication:** Assume you have a reliable, asynchronous message passing mechanism represented by the following simplified functions:

    *   `sendPrepare(shardId, transactionId, operations)`: Sends a "prepare" message to the specified shard, containing the `transactionId` and a list of `operations` that the shard needs to perform (e.g., debit `fromAccountId` and credit `toAccountId`).  `operations` is a list of objects with `{accountId: string, amount: number, type: 'DEBIT' | 'CREDIT'}`. Returns a `Promise` that resolves to `true` if the shard is prepared to commit, or `false` if the shard rejects the prepare request.
    *   `sendCommit(shardId, transactionId)`: Sends a "commit" message to the specified shard for the given `transactionId`.  Returns a `Promise` that resolves when the shard has successfully committed the transaction.
    *   `sendRollback(shardId, transactionId)`: Sends a "rollback" message to the specified shard for the given `transactionId`. Returns a `Promise` that resolves when the shard has successfully rolled back the transaction.

6.  **Transaction ID Generation:**  You need to generate unique transaction IDs for each `transfer` request.

7.  **Error Handling:** You must handle scenarios where shards fail to prepare or commit.  Rollback transactions in case of failures.

8.  **Concurrency:** The system must handle concurrent transaction requests.

9. **Idempotency:** The system should be able to handle duplicate transaction requests. If a transaction with the same `transactionId` is received again, the system should return the previous result without re-executing the transaction.

**Constraints:**

*   The number of shards can be large.
*   Network communication between shards can be unreliable and slow.
*   Minimize the time a shard is blocked during the transaction process.
*   Optimize for throughput (number of transactions processed per unit time).
*   The `getShard` function is deterministic and will always return the same shard ID for a given `accountId`.

**Your Task:**

Implement the `transfer(fromAccountId, toAccountId, amount)` function.  You are free to design and implement any necessary helper functions or data structures to support the 2PC protocol and meet the given requirements.  Consider carefully how to structure your code to handle concurrency, failures, and idempotency.
