Okay, here's a challenging C++ problem designed to test a range of skills.

## Problem: Distributed Transaction Validation

**Description:**

You are designing a system for validating distributed transactions across a network of microservices. Each microservice manages its own local data and participates in transactions that may span multiple services. To ensure data consistency, a two-phase commit (2PC) protocol is used.

Each transaction is assigned a unique Transaction ID (TID). When a transaction starts, it initiates a "prepare" phase with all participating microservices. Each microservice then performs the necessary local checks (e.g., sufficient funds, inventory availability) and votes to either commit or abort the transaction.  The transaction coordinator (a separate component, not your code) collects these votes. If all votes are "commit," the coordinator sends a "commit" message to all participants. If any vote is "abort," the coordinator sends an "abort" message.

Your task is to implement a validation service that determines whether a set of transaction logs are valid, given the constraints of the 2PC protocol.

**Input:**

The input consists of a series of log entries. Each log entry is a string representing an event in the distributed transaction system. The log entries are chronologically ordered. Each microservice uses the same timestamp clock, so all logs are sorted by the timestamp in ascending order.

Log entries can be one of the following types:

*   `PREPARE TID SERVICE_ID`:  Service `SERVICE_ID` receives a prepare message for transaction `TID`.
*   `VOTE_COMMIT TID SERVICE_ID`: Service `SERVICE_ID` votes to commit transaction `TID`.
*   `VOTE_ABORT TID SERVICE_ID`: Service `SERVICE_ID` votes to abort transaction `TID`.
*   `COMMIT TID`: The transaction coordinator sends a commit message for transaction `TID`.
*   `ABORT TID`: The transaction coordinator sends an abort message for transaction `TID`.
*   `COMPLETE TID SERVICE_ID`: Service `SERVICE_ID` has successfully committed or aborted transaction `TID`.

`TID` and `SERVICE_ID` are positive integers.

**Output:**

Your program should output "VALID" if the transaction logs are consistent with the 2PC protocol. Otherwise, it should output "INVALID".

**Constraints:**

1.  **Prepare Before Vote:** A service must receive a `PREPARE` message for a transaction before it can vote (`VOTE_COMMIT` or `VOTE_ABORT`) for that transaction.
2.  **Single Vote:** A service can vote at most once for a given transaction.
3.  **Commit/Abort After Votes:** A `COMMIT` or `ABORT` message for a transaction can only be sent after all participating services have voted. You don't know how many services will participate in the transaction beforehand; you can only infer it from the logs.
4.  **Consistent Decision:** If a `COMMIT` message is sent, all services that voted must have voted to commit. If an `ABORT` message is sent, at least one service must have voted to abort.
5.  **Complete After Decision:** A service can only `COMPLETE` a transaction after a `COMMIT` or `ABORT` message has been sent for that transaction.
6.  **Single Complete:** A service can only `COMPLETE` a transaction once.
7.  **No Orphans:** A transaction will be initiated at a service, but the log does not reflect the initiator. All the services participate in a 2PC flow.

**Example Input:**

```
PREPARE 1 SERVICE_1
PREPARE 1 SERVICE_2
VOTE_COMMIT 1 SERVICE_1
VOTE_COMMIT 1 SERVICE_2
COMMIT 1
COMPLETE 1 SERVICE_1
COMPLETE 1 SERVICE_2
PREPARE 2 SERVICE_1
VOTE_ABORT 2 SERVICE_1
ABORT 2
COMPLETE 2 SERVICE_1
PREPARE 3 SERVICE_1
PREPARE 3 SERVICE_2
VOTE_COMMIT 3 SERVICE_1
VOTE_ABORT 3 SERVICE_2
ABORT 3
COMPLETE 3 SERVICE_1
COMPLETE 3 SERVICE_2
```

**Example Output:**

```
VALID
```

**Example Input (Invalid):**

```
VOTE_COMMIT 1 SERVICE_1
PREPARE 1 SERVICE_1
```

**Example Output (Invalid):**

```
INVALID
```

**Performance Requirements:**

The number of log entries can be very large (up to 1,000,000).  Your solution must be efficient in terms of both time and memory usage.  Consider using appropriate data structures to track the state of each transaction and service.

**Judging Criteria:**

Your solution will be judged based on correctness (passing all test cases) and efficiency (running within the time and memory limits).  Emphasis will be placed on handling edge cases and complex scenarios.
