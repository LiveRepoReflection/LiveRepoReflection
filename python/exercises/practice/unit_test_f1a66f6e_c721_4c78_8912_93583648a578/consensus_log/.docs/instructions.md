## Problem: Distributed Consensus Log

**Description:**

You are designing a distributed key-value store.  A crucial component of this system is a replicated log used for consensus. Your task is to implement a simplified version of this replicated log, focusing on ensuring consistency across multiple nodes.

Each node in the system maintains its own local copy of the log. The log consists of a sequence of entries, where each entry represents an operation to be performed on the key-value store (e.g., `SET key value`, `DELETE key`).

The system operates in rounds. In each round, a leader is elected (you do not need to implement leader election). The leader proposes a new entry to be appended to the log. This proposal is then broadcast to all other nodes (followers).  Followers must validate the proposal and decide whether to accept it.

**Specific Requirements:**

1.  **Log Structure:** The log must be implemented as an append-only data structure. Each entry in the log has the following structure:
    ```python
    class LogEntry:
        def __init__(self, term: int, index: int, command: str):
            self.term = term # The term in which the entry was proposed
            self.index = index # The index of the entry in the log
            self.command = command # The operation to be performed (e.g., "SET x 5", "DELETE y")
    ```

2.  **Consensus Protocol (Simplified Raft):** Implement a simplified consensus protocol based on Raft's log replication mechanism.

    *   **Terms:** The system operates in terms. Each term is a period of time during which one leader is in charge. Terms are numbered sequentially, starting from 1.  Nodes maintain a `current_term` value.
    *   **Log Matching Property:** If two logs contain an entry with the same `term` and `index`, then the logs are identical in all entries up to that index.
    *   **Commitment:** An entry is considered "committed" when a majority of nodes have accepted the entry into their logs. Committed entries are durable and must be applied to the key-value store (you do not need to implement the key-value store itself).

3.  **Node Implementation:** Implement a `Node` class with the following methods:

    *   `__init__(self, node_id: int)`: Initializes the node with a unique ID and an empty log.  `node_id` starts from 0.
    *   `append_entry(self, entry: LogEntry) -> bool`: Appends a new `LogEntry` to the node's log.  The entry's `index` must be exactly one greater than the current last index, and its `term` must be no less than the node's `current_term`. Returns `True` if the entry is successfully appended, `False` otherwise.
    *   `accept_proposal(self, term: int, prev_log_index: int, prev_log_term: int, entry: LogEntry) -> bool`: Simulates a follower accepting or rejecting a leader's proposal.  The follower should accept the proposal if *all* of the following conditions are met:

        *   The follower's `current_term` is less than or equal to the proposal's `term`. If the proposal `term` is larger, the follower should update its `current_term`.
        *   The follower's log contains an entry at `prev_log_index` whose `term` matches `prev_log_term`, *or* `prev_log_index` is 0 (meaning the leader is proposing the first entry).
        *   The proposed `entry`'s `index` is exactly one greater than `prev_log_index`.

        If the proposal is accepted, the follower must append the `entry` to its log.  If an existing entry conflicts with a new one (same index but different term), delete the existing entry and all that follow it.
        Return `True` if the proposal is accepted, `False` otherwise.
    *   `get_log() -> list[LogEntry]`: Returns a copy of the node's log.
    *   `get_current_term() -> int`: Returns the node's current term.
    *   `set_current_term(self, term: int)`: Sets the node's current term.

4.  **Constraints:**

    *   **Efficiency:** The `accept_proposal` method should be optimized for performance. Avoid unnecessary iterations or computations.
    *   **Concurrency:** Assume your code might be run in a multi-threaded environment (though you don't need to explicitly handle threading).  Ensure your data structures are thread-safe.
    *   **Scalability:** The solution should be designed to handle a potentially large number of log entries and nodes.  Consider memory usage and algorithmic complexity.
    *   **Immutability:** Log entries themselves should be treated as immutable once created.
    *   **Error Handling:** While explicit exception handling is not strictly required, the code should be robust and avoid potential errors (e.g., index out of bounds).

5.  **Input/Output:**

    *   The solution should focus on the implementation of the `Node` class and its methods.
    *   No specific input/output format is required for testing.  You should design your own test cases to thoroughly validate the implementation.

**Challenge:**

The primary challenge lies in efficiently managing the log and ensuring consistency in the face of potential conflicts and network delays (which are simulated by the `accept_proposal` method returning `False` occasionally).  The concurrency and scalability constraints add further complexity.  The optimal solution will balance correctness, performance, and memory usage.
