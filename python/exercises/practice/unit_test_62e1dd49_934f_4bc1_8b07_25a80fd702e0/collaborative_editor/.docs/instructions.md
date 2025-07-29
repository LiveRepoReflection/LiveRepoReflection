## Real-Time Collaborative Document Editing with Operational Transformation

### Question Description

You are tasked with designing a system for real-time collaborative document editing. Multiple users can simultaneously edit the same document, and their changes should be reflected in everyone's view as quickly as possible. To handle concurrent edits and maintain consistency, you will implement a simplified version of Operational Transformation (OT).

**Core Requirements:**

1.  **Document Representation:** The document is represented as a simple string.
2.  **Operations:** Only two types of operations are supported:
    *   `Insert(position, text)`: Inserts `text` at the given `position` in the document.
    *   `Delete(position, length)`: Deletes `length` characters starting from the given `position` in the document.
3.  **Operational Transformation (OT):** When a user's operation arrives at the server, it needs to be transformed against all concurrent operations that have been applied to the server's document but haven't yet been acknowledged by that user. This transformation ensures that operations are applied in a consistent order, even when users are working offline or experience network delays.
4.  **Concurrency Handling:** Design your OT algorithm to handle the following challenging concurrency scenarios:
    *   **Insert-Insert Conflict:** Two users insert text at the same position.
    *   **Insert-Delete Conflict:** One user inserts text at a position where another user deletes text.
    *   **Delete-Insert Conflict:** One user deletes text at a position where another user inserts text.
    *   **Delete-Delete Conflict:** Two users delete text overlapping regions of the document.
5.  **Client-Server Communication:** Implement a basic client-server model (can be simulated in a single process). The client sends operations to the server, and the server broadcasts the transformed operations to all connected clients (excluding the origin client). The origin client keeps track of which operations it sent, waiting for server acknowledgement.
6.  **Acknowledgement:** The server acknowledges the operations it has applied from each client. Clients must wait for acknowledgement before considering any operations as definitively applied.
7.  **Correctness:** The system must maintain document consistency across all clients, even with concurrent edits and network delays.

**Constraints and Considerations:**

*   **String Manipulation Efficiency:** Optimize string manipulation operations (insertion and deletion) for large documents. Consider using more efficient data structures if necessary.
*   **Network Latency:** The system should be resilient to network latency and temporary disconnections.
*   **Scalability:** While full scalability is not required, consider how the design could be extended to handle a large number of concurrent users.
*   **Operation Ordering:** The operations must be applied in the correct order to ensure consistency across all clients.
*   **Edge Cases:** Handle various edge cases, such as inserting/deleting at the beginning or end of the document, or deleting a range that extends beyond the document length.
*   **Atomicity**: Although it's not strictly enforced on the user side, the server implementation should ideally ensure that operations are applied atomically to avoid partial updates and inconsistencies.
*   **Operation ID**: Each operation has a unique ID, allowing clients and the server to reliably identify and track operations, particularly for acknowledgement purposes.

**Input/Output:**

The problem does not have explicit input/output. Instead, your solution will be judged on its correctness, efficiency, and design. You should demonstrate your solution with a series of simulated client-server interactions, including various concurrent editing scenarios.

**Evaluation Criteria:**

*   **Correctness:** Does the system maintain document consistency across all clients under various concurrent editing scenarios?
*   **Efficiency:** Are string manipulation operations optimized for large documents?
*   **Design:** Is the code well-structured, readable, and maintainable?
*   **Concurrency Handling:** Does the OT algorithm correctly handle all defined conflict scenarios?
*   **Resilience:** Is the system resilient to network latency and temporary disconnections?

This problem requires a deep understanding of Operational Transformation, concurrency control, and distributed systems concepts. A well-designed and implemented solution will demonstrate strong problem-solving and programming skills. Good luck!
