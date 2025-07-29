## Question: Distributed Transaction Coordinator

You are tasked with designing and implementing a simplified distributed transaction coordinator. Imagine a system where multiple services (databases, message queues, etc.) need to participate in a single, atomic transaction. Your coordinator must ensure that either all services commit their changes, or none of them do, even in the face of failures.

**System Model:**

*   There are `N` participant services. Each service is identified by a unique integer ID from 1 to `N`.
*   The coordinator communicates with each service via a simple request/response protocol (you don't need to implement the actual network communication, just simulate it).
*   Each service can either successfully prepare (indicate willingness to commit) or abort (indicate inability to commit).
*   The coordinator initiates the transaction.

**The Task:**

Implement a function `coordinate_transaction` that takes the following inputs:

1.  `N`: The number of participant services (an integer, 1 <= N <= 1000).
2.  `prepare_results`: A vector of booleans of size `N`. `prepare_results[i]` represents the outcome of the prepare phase for service `i+1`. `true` means the service successfully prepared, `false` means it aborted.
3.  `commit_success_probabilities`: A vector of doubles of size `N`. `commit_success_probabilities[i]` represents the probability (between 0.0 and 1.0 inclusive) that service `i+1` successfully commits its changes after receiving a commit request from the coordinator.  If a service fails to commit after being instructed to do so, it is considered a permanent failure.

The function `coordinate_transaction` should simulate the two-phase commit (2PC) protocol and return a boolean indicating whether the transaction was globally committed (`true`) or globally aborted (`false`).

**2PC Protocol:**

1.  **Prepare Phase:** The coordinator sends a "prepare" request to all `N` services. You are given the results of the prepare phase in `prepare_results`. If *any* service aborts (returns `false` in `prepare_results`), the entire transaction must be aborted.
2.  **Commit Phase:** If all services successfully prepared, the coordinator sends a "commit" request to all `N` services. Each service then attempts to commit. The probability of success for each service is given in `commit_success_probabilities`. Services commit independently.
3.  **Outcome:**

    *   The transaction is considered globally committed **only if all services successfully commit**.
    *   If any service fails to commit during the commit phase, the transaction is considered globally aborted, and all services that successfully committed are now in an inconsistent state.  (You don't need to handle rolling back the committed services in the inconsistent state - simply consider the whole transaction aborted.)

**Constraints and Edge Cases:**

*   Handle edge cases: empty input vectors, invalid probabilities (outside of \[0.0, 1.0] range).
*   Optimize for efficiency: The solution should be efficient in terms of both time and space complexity. Avoid unnecessary computations.
*   Simulate commit success based on the given probability: Use a pseudo-random number generator (e.g., `std::rand()` in C++, though consider the limitations of `std::rand()` for more robust simulations) to simulate whether a service commits successfully based on its `commit_success_probabilities`.
*   Assume the random number generator is seeded appropriately before calling your function.
*   Return `false` immediately if the prepare phase fails. Avoid unnecessary computations in the commit phase if the prepare phase already aborted.
*   The `commit_success_probabilities` vector will only contain probabilities for services that successfully prepared.

**Function Signature:**

```cpp
bool coordinate_transaction(int N, const std::vector<bool>& prepare_results, const std::vector<double>& commit_success_probabilities);
```
