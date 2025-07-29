## Question: Decentralized Collaborative Document Editing

**Description:**

You are tasked with designing and implementing a simplified version of a decentralized, collaborative document editing system. Imagine a scenario where multiple users can simultaneously edit a single document stored across a peer-to-peer network. The core challenge is to ensure consistency and prevent conflicts when multiple users make changes concurrently.

**System Requirements:**

1.  **Document Representation:** The document is represented as a sequence of characters (a string).

2.  **Operations:** Users can perform only two types of operations:

    *   **Insert(position, character):** Inserts a single character at the specified position in the document. Position is 0-indexed.
    *   **Delete(position):** Deletes the character at the specified position in the document. Position is 0-indexed.

3.  **Decentralization:** There is no central server. Each user (peer) maintains a local copy of the document and a log of operations.

4.  **Collaboration:** Users broadcast their operations to all other users in the network.

5.  **Conflict Resolution:** When multiple users perform conflicting operations (e.g., inserting at the same position, deleting the same character after another user already deleted it), your system must resolve these conflicts and ensure that all users eventually converge to the same document state. This is the most critical part of the problem.

6.  **Causality Preservation:** If operation A happened before operation B on one peer, it must remain that way on all peers.

7.  **Efficiency:**  The conflict resolution mechanism should be reasonably efficient, even with a large number of concurrent operations.

8.  **Eventual Consistency:**  All peers in the network will eventually converge to the same, consistent document state, assuming a reliable broadcast mechanism.

**Implementation Details:**

*   You will implement a `Peer` class that represents a single user in the network.
*   The `Peer` class should have the following methods:

    *   `__init__(self, peer_id, initial_document="")`: Initializes the peer with a unique ID and an optional initial document state.
    *   `local_insert(self, position, char)`: Performs a local insertion operation on the peer's document and broadcasts the operation to other peers.
    *   `local_delete(self, position)`: Performs a local deletion operation on the peer's document and broadcasts the operation to other peers.
    *   `receive_operation(self, operation, sender_id)`: Receives an operation from another peer and applies it to the local document.
    *   `get_document(self)`: Returns the current document state as a string.

*   The `operation` argument in `receive_operation` should be a dictionary with the following structure:

    ```python
    {
        "type": "insert" or "delete",
        "position": integer,
        "char": character (only for insert)
    }
    ```

**Constraints and Edge Cases:**

*   Handle concurrent operations from multiple peers.
*   Handle cases where operations are received out of order.
*   Ensure that insertion and deletion operations do not cause index-out-of-bounds errors.  If an insert position is beyond the end of the current string, the character should be appended.  If a delete position is beyond the end of the current string, the operation should be ignored.
*   The number of peers in the network can be large (up to 100).
*   The document size can be large (up to 100,000 characters).
*   The frequency of operations can be high.

**Evaluation Criteria:**

*   **Correctness:** The system must correctly resolve conflicts and ensure eventual consistency.
*   **Efficiency:** The conflict resolution mechanism should be efficient.
*   **Robustness:** The system should handle various edge cases and error conditions gracefully.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.

**Bonus:**

*   Implement a mechanism for handling peer joins and leaves in the network.
*   Optimize the operation broadcasting mechanism to reduce network traffic.
*   Implement a more sophisticated conflict resolution algorithm, such as Operational Transformation (OT) or Conflict-free Replicated Data Types (CRDTs). Note that implementing OT or CRDTs fully is beyond the scope of a typical coding competition question, but demonstrating an understanding of these concepts and implementing a simplified version will be favorably considered.

This problem requires you to think critically about distributed systems, data structures, and algorithms. It's a challenging problem that will test your ability to design and implement a robust and efficient solution. Good luck!
