Okay, here's a problem designed to be challenging and sophisticated, aiming for a difficulty similar to LeetCode Hard.

### Project Name

```
distributed-event-sourcing
```

### Question Description

You are tasked with designing and implementing a simplified, distributed event sourcing system. This system will be responsible for recording events related to financial transactions across multiple geographically distributed banking institutions.  Each institution operates independently but must maintain a consistent, auditable history of all transactions.

**Core Requirements:**

1.  **Event Storage:** Implement a persistent event store. Events are immutable records of state changes.  Each event should contain:
    *   `timestamp`: (Unix timestamp in milliseconds) The time the event occurred.
    *   `institution_id`: (String) A unique identifier for the banking institution.
    *   `account_id`: (String)  A unique identifier for the account affected by the transaction.
    *   `event_type`: (Enum: `DEPOSIT`, `WITHDRAWAL`, `TRANSFER_IN`, `TRANSFER_OUT`) The type of transaction.
    *   `amount`: (Integer) The amount of the transaction (in cents, to avoid floating point precision issues).
    *   `transfer_id`: (Optional String) If the event is TRANSFER_IN or TRANSFER_OUT, then it should contain the transfer_id

2.  **Event Ingestion:** Implement an API endpoint (or a function, depending on the language's capabilities) that allows each institution to append new events to the event store.  The API should handle concurrent requests.

3.  **Eventual Consistency:** Guarantee eventual consistency across all institutions.  Assume a simplified scenario where network partitions are infrequent but possible.  Focus on ensuring that after a period of stability, all institutions will have an identical view of the global transaction history.

4.  **Querying:** Implement an API endpoint (or function) to query the event store. The query should support the following filters:
    *   `institution_id`: (Optional String) Filter by institution. If omitted, return events from all institutions.
    *   `account_id`: (Optional String) Filter by account. If omitted, return events for all accounts.
    *   `start_time`: (Optional Unix timestamp in milliseconds) Filter events occurring after this time. If omitted, return all events from the beginning.
    *   `end_time`: (Optional Unix timestamp in milliseconds) Filter events occurring before this time. If omitted, return all events up to the present.
    *   Implement pagination (return events in batches of a specified size).

5.  **Fault Tolerance:**  The system should be reasonably fault-tolerant.  Specifically, implement a mechanism to handle the case where one or more institutions might temporarily go offline. Events generated during that offline period must eventually be ingested into the global event store once the institution comes back online.

**Constraints & Considerations:**

*   **Scalability:** While not requiring a full-blown distributed database, design the event store in a way that *could* be scaled to handle a large number of events and institutions.  Consider data partitioning and sharding strategies. The system should not run out of memory when ingesting a large number of events.

*   **Concurrency:**  Multiple institutions will be adding events concurrently.  Implement appropriate locking or concurrency control mechanisms to ensure data integrity.

*   **Event Ordering:** It's *not* strictly necessary to guarantee perfectly global ordering of events.  However, events *within* a single `account_id` and `institution_id` *must* be ordered by `timestamp`. This ordering is critical for auditing.

*   **Optimization:** Optimize for read performance.  Queries should be as efficient as possible, even with a large number of events.  Consider indexing strategies.

*   **Data Integrity:** Implement checksums or other mechanisms to verify the integrity of the stored events.  Detect and handle corrupted data.

*   **Storage Medium:** You are free to choose the underlying storage mechanism (e.g., in-memory data structures, files, embedded database like SQLite, etc.).  However, justify your choice based on scalability, performance, and fault tolerance considerations. In-memory storage will not be accepted.

*   **Testing:** Provide unit tests to demonstrate the correctness of your implementation. Focus on testing concurrency, fault tolerance, and query functionality.

**Bonus Challenges (Optional):**

*   **Snapshotting:** Implement a snapshotting mechanism to reduce the time required to reconstruct the state of an account.
*   **Conflict Resolution:**  Handle conflicting events (e.g., two institutions attempt to withdraw from the same account simultaneously). Design a conflict resolution strategy (e.g., last-write-wins, optimistic locking) and implement it.
*   **Replication:** Implement replication of the event store across multiple nodes to improve availability and fault tolerance.

This problem requires a solid understanding of data structures, algorithms, concurrency, and system design principles. It encourages the solver to think about trade-offs between performance, scalability, fault tolerance, and consistency. Good luck!
