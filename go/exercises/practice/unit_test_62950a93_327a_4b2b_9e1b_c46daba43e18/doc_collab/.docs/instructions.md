## Problem: Decentralized Collaborative Document Editing with Conflict Resolution

**Description:**

Design a distributed system for real-time collaborative document editing.  Multiple users can simultaneously edit the same document.  The challenge lies in managing concurrent edits and resolving conflicts in a decentralized manner, without relying on a central server for conflict resolution.

Specifically, you are given a series of operations on a shared document.  Each operation is represented as a tuple: `(user_id, operation_type, position, text)`.

*   `user_id`: A unique integer identifying the user performing the operation.
*   `operation_type`: An enum representing the type of operation: `INSERT` or `DELETE`.
*   `position`: An integer representing the index in the document where the operation should be applied (0-indexed).
*   `text`: A string representing the text to insert or delete. For `DELETE` operations, this represents the text that *was* at `position` *before* the delete.

Your task is to implement a function that takes a list of these operations, potentially out of order and containing conflicts, and produces the final, consistent document state.

**Constraints and Requirements:**

1.  **Decentralized Conflict Resolution:**  You cannot assume a central authority to resolve conflicts.  The algorithm must work based on the information available within the operations themselves.
2.  **Causality Preservation:**  If operation A happened before operation B (i.e., user X performed A, then performed B), then the effect of A should be applied before the effect of B, even if the operations arrive out of order.
3.  **Data Structures:** You are free to choose appropriate data structures to represent the document and operations. Consider structures optimized for insertions, deletions, and conflict detection.
4.  **Edge Cases:**
    *   Handle concurrent inserts at the same position.
    *   Handle deletes that overlap with inserts or other deletes.
    *   Handle operations with invalid positions (e.g., position outside the current document length).
    *   Handle operations with empty text fields.
5.  **Performance:**  The solution should be reasonably efficient, especially for scenarios with a large number of operations and frequent concurrent edits. Aim for a time complexity that scales gracefully with the number of operations.  Excessive brute-force or naive approaches will likely timeout in larger test cases.
6.  **Consistency:**  The final document state must be consistent, meaning the order of operations from the same user must be preserved, and conflicting operations must be resolved in a deterministic manner (e.g., using user IDs as tiebreakers).
7.  **Error Handling:** Define and return an error type for cases where an operation is fundamentally invalid (e.g., negative position).  Otherwise, all valid operations should be applied, even if there are conflicts.  Conflicts should be resolved to produce a consistent, though potentially imperfect, final state.
8.  **Concurrency:** While you do not need to explicitly implement concurrent processing in your solution, the design should be amenable to concurrent application of operations in a real-world distributed system. Consider how your data structures and algorithms would behave under concurrent access.

**Input:**

A `[]Operation`, where `Operation` is a struct defined as:

```go
type Operation struct {
    UserID       int
    OperationType OperationType
    Position     int
    Text         string
}

type OperationType int

const (
    INSERT OperationType = iota
    DELETE
)
```

**Output:**

A `string` representing the final document content, or an `error` if an invalid operation is encountered.

**Example:**

```go
operations := []Operation{
    {1, INSERT, 0, "hello"},
    {2, INSERT, 0, "world "},
    {1, INSERT, 5, ", "},
    {2, DELETE, 0, "world "},
    {1, INSERT, 6, "!"},
}

finalDocument, err := processOperations(operations)

// Expected Output: "hello, world!"
```

This problem requires a deep understanding of distributed systems concepts, data structure design, algorithm optimization, and careful handling of edge cases. A robust and efficient solution will be a testament to a strong understanding of Go and software engineering principles.
