## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified, distributed transaction coordinator.  Imagine a system where multiple services (databases, message queues, etc.) need to participate in a single atomic transaction.  If any service fails to commit its changes, the entire transaction must be rolled back across all participants.

Your coordinator is responsible for managing these distributed transactions using a two-phase commit (2PC) protocol.  The coordinator communicates with several "participants" (simulated as other modules within your application). Each participant can either agree to commit the transaction (vote "yes") or refuse to commit (vote "no").  If all participants vote "yes", the coordinator instructs them to commit. If even one participant votes "no", the coordinator instructs all participants to rollback.

**Input:**

The input consists of a series of transaction requests.  Each transaction request specifies a set of participant IDs and, for each participant, a probability that the participant will vote "yes" (commit).

The input will be provided via standard input in the following format:

```
<number_of_transactions>
<transaction_id_1> <number_of_participants_1> <participant_id_1_1> <commit_probability_1_1> <participant_id_1_2> <commit_probability_1_2> ... <participant_id_1_n> <commit_probability_1_n>
<transaction_id_2> <number_of_participants_2> <participant_id_2_1> <commit_probability_2_1> <participant_id_2_2> <commit_probability_2_2> ... <participant_id_2_n> <commit_probability_2_n>
...
<transaction_id_k> <number_of_participants_k> <participant_id_k_1> <commit_probability_k_1> <participant_id_k_2> <commit_probability_k_2> ... <participant_id_k_n> <commit_probability_k_n>

```

*   `<number_of_transactions>` is a positive integer representing the number of transaction requests.
*   `<transaction_id_i>` is a unique positive integer identifying the transaction.
*   `<number_of_participants_i>` is a positive integer representing the number of participants in transaction `i`.
*   `<participant_id_i_j>` is a unique positive integer identifying a participant in transaction `i`.
*   `<commit_probability_i_j>` is a floating-point number between 0.0 and 1.0 (inclusive) representing the probability that participant `j` will vote "yes" for transaction `i`.

**Output:**

For each transaction, output a single line indicating whether the transaction committed or rolled back.

```
Transaction <transaction_id>: Committed
```

or

```
Transaction <transaction_id>: Rolled Back
```

Output to standard output.

**Constraints:**

*   1 <= `<number_of_transactions>` <= 1000
*   1 <= `<transaction_id_i>` <= 100000
*   1 <= `<number_of_participants_i>` <= 100
*   1 <= `<participant_id_i_j>` <= 1000
*   0.0 <= `<commit_probability_i_j>` <= 1.0
*   Participant IDs are unique across *all* transactions.
*   Transaction IDs are unique.

**Requirements:**

1.  **Concurrency:**  The coordinator must be able to handle multiple concurrent transactions. You should use threads to simulate the parallel nature of distributed systems.
2.  **Fault Tolerance (Simplified):**  Simulate participant failures. If a participant fails (votes "no"), the coordinator must ensure that all other participants are rolled back.
3.  **Idempotency:** The coordinator should be able to handle duplicate commit/rollback requests. This could simulate network issues that cause messages to be delivered multiple times.
4.  **Scalability:** While this is a simulation, consider the scalability implications of your design.  How would your solution handle a much larger number of participants and transactions? (This won't be directly tested, but your design should reflect an understanding of scalability principles).
5.  **Efficiency:**  Minimize the time it takes to process transactions. The number of transactions is large, so inefficient algorithms may result in timeouts.

**Advanced Considerations (Optional, but highly encouraged):**

*   **Deadlock Detection:**  If your solution involves locking resources, consider how to detect and resolve deadlocks. In this simplified simulation, you don't need to implement full deadlock resolution, but you should describe how you would approach it in a real-world system.
*   **Logging/Recovery:**  Describe how you would implement logging to ensure that the coordinator can recover from failures. What information would you log, and how would you use it to restore the system to a consistent state? (Again, no need to implement, just describe).

**Judging Criteria:**

*   **Correctness:**  The solution must correctly implement the 2PC protocol and produce the correct output.
*   **Concurrency Safety:** The solution must be thread-safe and avoid race conditions.
*   **Efficiency:** The solution must process transactions within a reasonable time frame.
*   **Design Quality:** The solution should be well-structured, maintainable, and scalable. The code should be clear and easy to understand.
*   **Handling Edge Cases:** The solution should correctly handle edge cases such as duplicate requests, participant failures, and empty transaction sets.
*   **Explanation of Design Choices:**  A brief comment block at the top explaining the data structures and algorithms used, and their trade-offs, will be favorably considered.
