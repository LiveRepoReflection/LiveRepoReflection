## Project Name

`Decentralized Auction House`

## Question Description

You are tasked with designing and implementing a core component of a decentralized auction house on a permissionless blockchain. This auction house allows users to list items for sale, bid on them, and ultimately settle the auctions in a trustless manner.

**Specific Requirements:**

1.  **Auction Listing:** Implement a function that allows users to list items for auction. Each listing should include:
    *   A unique item identifier (e.g., a hash of the item's metadata, ensuring item authenticity). This ID must be a `String`.
    *   A starting price (in some abstract unit of currency, representable as a `u64`).
    *   A minimum bid increment (also `u64`). Bids must be at least this much higher than the current highest bid.
    *   An auction duration (in blocks/epochs, representable as a `u64`).  The auction ends after this many blocks/epochs have passed from the listing time.
    *   A seller's address/identifier (`String`).
2.  **Bidding:** Implement a function that allows users to bid on listed items.
    *   Bids must be higher than the current highest bid by at least the minimum bid increment.
    *   Each bid must be associated with a bidder's address/identifier (`String`) and the item identifier (`String`).
    *   The bidding function must check if the auction is still active (hasn't reached its duration).
    *   Only the highest bid for each item should be stored.  Older, lower bids are discarded.
3.  **Auction Settlement:** Implement a function to settle an auction.
    *   This function can only be called after the auction duration has elapsed.
    *   Upon settlement, the highest bidder (if any) is declared the winner.
    *   The winning bid amount is transferred to the seller (no actual transfer is required in this simulation, just recording of the event).
    *   If there are no bids, the auction is considered unsuccessful, and the item remains with the seller.
4.  **Concurrency & Data Integrity:** The auction house must be designed to handle concurrent listing and bidding operations from multiple users.  Ensure data integrity under concurrent access.
5.  **Gas Optimization:**  Minimize the computational cost (gas usage) of each operation, especially the bidding and settlement functions. Consider the data structures used and how they impact performance.
6.  **Error Handling:** Implement robust error handling to prevent unexpected behavior and provide informative error messages. Examples include:
    *   Attempting to bid on a non-existent item.
    *   Attempting to bid below the minimum increment.
    *   Attempting to settle an auction before its duration has elapsed.
    *   Attempting to list an item with an invalid starting price or duration.
7.  **Data Structures:** You have freedom to choose the data structures. However, they **must** allow for efficient lookup of auctions by item ID and retrieval of the highest bid for an item.  Consider the trade-offs between different data structures (e.g., HashMap, BTreeMap) in terms of lookup speed, memory usage, and insertion/deletion costs.

**Constraints:**

*   Assume a blockchain environment where time progresses in discrete blocks/epochs represented by a `u64` counter, you can represent it as a global variable.
*   You do not need to implement actual cryptocurrency transfers. Instead, record the winning bid amount and participants.
*   Focus on the core auction logic.  You do not need to handle complex aspects like royalties, metadata storage, or front-end interactions.
*   You **must** use Rust's standard library features for concurrency primitives, such as `Mutex` or `RwLock`, to ensure thread safety.
*   The solution should compile without warnings when using `cargo clippy`.
*   Assume all item identifiers and addresses are valid `String`.

**Bonus Challenges (optional, but highly encouraged):**

*   Implement a cancel auction function that allows the seller to cancel the auction before any bids are placed. This function should only be callable by the seller.
*   Implement a refund mechanism that allows losing bidders to reclaim their bid amounts (in a real system, this would involve transferring the currency back to them). Again, no actual transfer required in this simulation.
*   Add unit tests to demonstrate the correctness and robustness of your implementation, including tests for concurrent operations and edge cases.

This problem aims to evaluate your understanding of data structures, algorithms, concurrency, and error handling in a practical, blockchain-inspired context. The constraints and optimization requirements are designed to push your Rust skills to the limit. Good luck!
