Okay, here's a challenging problem for a Rust programming competition, designed to be difficult and incorporate the elements you requested.

**Problem Title: Decentralized Order Book Reconciliation**

**Problem Description:**

You are building a component for a high-frequency, decentralized exchange (DEX).  A key challenge in DEXs is maintaining a consistent order book across a peer-to-peer network where message delivery isn't guaranteed and nodes can arbitrarily fail.

Each node in the network maintains its own local order book, represented as a priority queue (min-heap for bids, max-heap for asks). Orders are identified by a unique 128-bit UUID. Orders have a price (unsigned 64-bit integer) and a quantity (unsigned 64-bit integer).

Due to network latency and node failures, order books can become inconsistent. Your task is to reconcile two potentially inconsistent order books, a *primary* order book and a *secondary* order book, given a stream of "gossip" messages indicating order modifications and executions. The goal is to determine the final *reconciled* order book, representing a best-effort approximation of the "true" state.

**Input:**

1.  **Primary Order Book Snapshot:** A list of tuples, where each tuple represents an order in the primary order book.  Each tuple contains: `(order_id: UUID, is_bid: bool, price: u64, quantity: u64)`.
2.  **Secondary Order Book Snapshot:** A list of tuples, with the same format as the primary order book.
3.  **Gossip Message Stream:** A potentially very long stream of messages. Each message is an enum with the following variants:

    *   `AddOrder { order_id: UUID, is_bid: bool, price: u64, quantity: u64 }`
    *   `CancelOrder { order_id: UUID }`
    *   `ExecuteOrder { order_id: UUID, executed_quantity: u64 }`

    The messages are provided in chronological order as a `Vec<Message>`.
4.  **Time Window:** A `u64` representing a time window (in nanoseconds). Only messages timestamped within the last time window (relative to the *latest* message timestamp) should be considered for reconciliation. The messages are timestamped using `std::time::Instant` which stores a duration since an arbitrary but fixed point in time.

**Output:**

A tuple containing two lists of tuples:

1.  **Bids:** A list of tuples, representing the final reconciled bid order book. Each tuple contains: `(order_id: UUID, price: u64, quantity: u64)`. The bids should be sorted in descending order of price.
2.  **Asks:** A list of tuples, representing the final reconciled ask order book. Each tuple contains: `(order_id: UUID, price: u64, quantity: u64)`. The asks should be sorted in ascending order of price.

**Constraints:**

*   **Order IDs are unique.**  No two orders will ever have the same UUID.
*   **Message timestamps are monotonically increasing.**  The gossip message stream is ordered chronologically.
*   **Partial Order Execution:**  An `ExecuteOrder` message might indicate a partial execution (i.e., `executed_quantity` is less than the order's initial quantity).
*   **Stale Messages:** Messages can be "stale" if they refer to orders that no longer exist in either order book (due to a prior cancellation or full execution).  Your code should handle these gracefully.
*   **Conflicting Information:**  It's possible for the primary and secondary order books to contain conflicting information about the same order (e.g., different quantities).  Prioritize the primary order book, but *only* if the message stream supports that prioritization (see Reconciliation Strategy below).
*   **Quantity Overflow:** Be mindful of potential integer overflows when handling quantities, especially during execution updates.
*   **Performance:** The gossip message stream can be extremely long (millions of messages).  Your solution must be efficient in both time and memory.  Consider using appropriate data structures and algorithms to minimize processing time.
*   **Time Complexity:** Aim for a solution with logarithmic time complexity for order book operations (adding, cancelling, executing).  Linear time complexity for processing the message stream is acceptable, but strive for better if possible.

**Reconciliation Strategy:**

1.  **Initial State:** Start with the primary order book snapshot as the initial state of the reconciled order book.
2.  **Apply Time Window:** Filter the gossip message stream to include only messages within the specified `time_window` of the *latest* message timestamp.
3.  **Message Application:** Iterate through the filtered gossip messages in chronological order.  Apply each message to the reconciled order book as follows:
    *   `AddOrder`: If the order doesn't already exist, add it to the reconciled order book.  If it *does* already exist, do *not* change the reconciliated order book.
    *   `CancelOrder`: Remove the order from the reconciled order book if it exists.
    *   `ExecuteOrder`: If the order exists, decrement its quantity by `executed_quantity`.  If the resulting quantity is zero or negative, remove the order.

**Optimization Considerations:**

*   **Data Structures:**  Carefully consider the data structures used to represent the order books.  `BinaryHeap` is a good starting point, but explore alternatives if necessary.
*   **Hashing:** Use hashing techniques (e.g., `HashMap`) to efficiently look up orders by ID.
*   **Avoid Unnecessary Cloning:**  Minimize cloning of data, especially large data structures.
*   **Benchmarking:**  Benchmark your code with realistic input data to identify performance bottlenecks.

This problem combines algorithmic challenges with real-world considerations, demanding a solid understanding of data structures, algorithms, and system design principles. Good luck!
