Okay, I'm ready. Here's a challenging coding problem for a high-level programming competition, designed for Go.

## Problem: Decentralized Collaborative Map

**Description:**

You are building a decentralized collaborative map service.  The map is represented as a grid of `N x N` cells. Each cell can hold a single piece of information (a string), which is contributed by different users.  Due to the decentralized nature, updates can be received out of order and might conflict. You need to design a system to manage these updates and provide a consistent view of the map.

**Data Representation:**

The map is logically a 2D array of strings: `map[row][col]string`.  However, due to the collaborative and decentralized nature, updates are received as individual "Claims".

**Claim Structure:**

A `Claim` has the following fields:

*   `Row`: Row index of the cell to be updated (0-indexed).
*   `Col`: Column index of the cell to be updated (0-indexed).
*   `Value`: The string value to be written to the cell.
*   `Timestamp`: A monotonically increasing integer representing the time the claim was created.  Higher timestamps indicate more recent claims.
*   `UserID`: A unique string identifying the user who made the claim.

**Constraints:**

1.  **Eventual Consistency:** All valid claims must eventually be reflected in the map.
2.  **Last Write Wins (with Tiebreaker):** If multiple claims apply to the same cell, the claim with the highest timestamp wins. If two claims for the same cell have the same timestamp, the claim with the *lexicographically smallest* `UserID` wins.
3.  **Concurrency:** The system must handle concurrent updates efficiently.  Multiple goroutines may be making claims simultaneously.
4.  **Memory Efficiency:** The system should avoid storing unnecessary data. Consider memory usage as the map size `N` and the number of `Claim`s grows.
5.  **Scalability:** While a single process solution is sufficient, consider how your solution could be extended to handle a sharded, distributed map.  (This will be part of the evaluation).
6.  **Bounded Staleness:**  After a certain "settling time" (e.g., 10 seconds after a claim is added), a read to a cell should *almost always* return the correct (most recent) value. Very rare exceptions are acceptable.
7.  `0 <= Row < N`
8.  `0 <= Col < N`
9.  `N <= 1000`  (The map size will not exceed 1000x1000).
10. The length of `Value` will not exceed 255.

**Task:**

Implement a `MapService` that provides the following interface:

```go
type Claim struct {
    Row       int
    Col       int
    Value     string
    Timestamp int64
    UserID    string
}

type MapService interface {
    // SubmitClaim submits a claim to update the map.  This function should
    // be thread-safe.
    SubmitClaim(claim Claim)

    // GetValue retrieves the current value of a cell.  This function should
    // be thread-safe.
    GetValue(row int, col int) string

    // Size returns the size N of the map (NxN)
    Size() int
}
```

**Evaluation:**

Your solution will be evaluated on:

*   **Correctness:**  Does it correctly implement the "last write wins" logic with tiebreaker?
*   **Concurrency Safety:**  Does it handle concurrent updates without data races?
*   **Performance:**  How quickly can it process a large number of claims and retrieve values? Consider both throughput and latency.
*   **Memory Usage:**  How much memory does it use, especially as the number of claims increases?
*   **Scalability (Design):**  How easily could your design be extended to a distributed system? Briefly describe how sharding and replication could be used to improve scalability.

**Bonus:**

*   Implement a mechanism for automatically garbage collecting old, superseded claims to further reduce memory usage.
*   Implement a read cache to improve the performance of `GetValue`.

This problem requires careful consideration of data structures, concurrency, and optimization techniques. Good luck!
