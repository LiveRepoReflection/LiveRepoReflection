Okay, here's a challenging Java coding problem designed to test a wide range of skills:

**Problem Title:**  Real-Time Collaborative Document Editor

**Problem Description:**

You are tasked with designing and implementing the core backend logic for a real-time collaborative document editor. The system must handle concurrent edits from multiple users on a single document, ensuring data consistency and minimal latency.

The document is represented as a sequence of characters (a String). Users can perform the following operations:

1.  **Insert(position, text):** Insert a given `text` at a specified `position` within the document.
2.  **Delete(position, length):** Delete a substring of length `length` starting at a specified `position` from the document.
3.  **GetDocument():** Retrieve the current document content as a String.

**Concurrency & Consistency Requirements:**

*   The system must handle concurrent `Insert` and `Delete` operations from multiple users.
*   All operations must be atomic and serializable, ensuring that the final document state is consistent regardless of the order in which operations are executed. This means that the final document must be the result of applying all operations in *some* valid order.
*   You need to implement a mechanism for resolving conflicts arising from concurrent edits.  A naive approach of simply applying operations in arrival order will lead to incorrect document states.
*   Implement an efficient method to track operation history and resolve conflicts to maintain data integrity.
*   The system should strive for minimal latency in applying and propagating edits to all users.

**Performance & Scalability Requirements:**

*   The solution should be optimized for performance, especially in scenarios with a large number of concurrent users and frequent edits. Consider the time complexity of your algorithms.
*   The core document data structure and conflict resolution mechanism should be designed with scalability in mind.  Consider how your approach would perform with extremely large documents (e.g., 10MB+) and hundreds of concurrent users.
*   Assume the system can be deployed across multiple servers (though you don't need to implement the distributed deployment aspect). Your data structure and algorithms should be suitable for this kind of environment.

**Constraints:**

*   Positions in the document are 0-indexed.
*   `position` and `length` in `Insert` and `Delete` operations are always valid within the bounds of the document at the time the operation is received.
*   The document initially starts as an empty string.
*   The number of concurrent users can range from 1 to 1000.
*   The size of the document can grow up to 10MB.
*   The maximum length of the `text` in an `Insert` operation is 1000 characters.
*   The frequency of operations can be high (e.g., up to 100 operations per second).

**Clarifications and Edge Cases:**

*   Consider the case where two users concurrently insert text at the same position. How do you resolve the conflict and determine the final order of the inserted text?
*   Consider the case where one user inserts text and another user concurrently deletes a portion of the same text.
*   What happens when two users try to delete the same region?
*   Your solution should handle edge cases gracefully and prevent data corruption.

**Deliverables:**

Implement the core backend logic for the collaborative document editor, including the following methods:

*   `Insert(userId, position, text)`:  Handles insertion operations from a specific user.
*   `Delete(userId, position, length)`: Handles deletion operations from a specific user.
*   `GetDocument()`: Returns the current document content as a String.

Your solution should be thread-safe and optimized for performance and scalability.  You should also provide a brief explanation of your chosen data structures and conflict resolution mechanism, justifying your design choices.
