Okay, I'm ready. Here's a challenging problem description, aiming for LeetCode Hard level difficulty.

**Problem Title:** Decentralized Order Matching Engine

**Problem Description:**

You are tasked with building a core component of a decentralized exchange (DEX): an efficient and robust order matching engine. This engine operates on a blockchain-like environment, where data is immutable and consistency is paramount.

The exchange supports a single trading pair: Asset A and Asset B. Users submit limit orders to either buy Asset A with Asset B (a "bid") or sell Asset A for Asset B (an "ask"). Each order specifies a price (the exchange rate between A and B) and a quantity (the amount of Asset A being bought or sold).

Your engine must maintain two separate, prioritized order books: one for bids (buy orders) and one for asks (sell orders).  Orders in each book should be sorted based on price and timestamp. For bids, higher prices have priority. For asks, lower prices have priority. If two orders have the same price, the earlier order (lower timestamp) has priority.

When a new order arrives, the engine must attempt to match it against existing orders in the opposite order book. A match occurs when a bid price is greater than or equal to an ask price. When matches occur, orders are partially or fully filled until either the new order or the matching order(s) are completely filled.

**Input:**

A stream of order events. Each event is a tuple containing:

1.  `timestamp`: An integer representing the time the order was received. Timestamps are strictly increasing.
2.  `order_id`: A unique string identifying the order.
3.  `order_type`: An enum or string indicating whether the order is a "BID" (buy) or an "ASK" (sell).
4.  `price`: A floating-point number representing the price of the order (Asset B per Asset A).
5.  `quantity`: An integer representing the quantity of Asset A to be bought or sold.
6.  `is_cancellation`: A boolean that specifies whether an order is a new order or a cancellation of the order that has the `order_id` specified.

**Output:**

For each order event, your engine must return a list of trade executions. Each trade execution is a tuple containing:

1.  `taker_order_id`: The `order_id` of the incoming order (the "taker").
2.  `maker_order_id`: The `order_id` of the existing order that matched against (the "maker").
3.  `price`: The price at which the trade occurred.
4.  `quantity`: The quantity of Asset A traded.

**Constraints and Requirements:**

*   **Immutability:** Once an order is placed, its price and initial quantity cannot be changed. However, the remaining quantity can be reduced as trades occur.
*   **Order Priority:** Orders must be matched based on price and then timestamp (FIFO within each price level).
*   **Partial Fills:** Orders can be partially filled.
*   **Cancellation:** Orders can be cancelled by providing the `order_id` and setting `is_cancellation` to `True`. Cancelling an order removes it from the order book.
*   **Efficiency:** The engine must handle a large volume of orders efficiently.  Consider the time complexity of your matching and cancellation algorithms. Aim for logarithmic or better performance where possible.
*   **Floating-Point Precision:** Be mindful of potential floating-point precision issues when comparing prices. Use a reasonable tolerance for equality checks.
*   **Concurrency (Conceptual):** While you don't need to implement actual concurrency, your design should consider how the engine could be made thread-safe and handle concurrent order submissions in a real-world DEX.
*   **Persistence (Conceptual):** Consider how the order books and trade history could be persisted in a blockchain-like environment (e.g., using a Merkle tree). You don't need to implement persistence, but your design should be mindful of it.

**Example:**

(Illustrative - actual input/output format may vary slightly)

Input:

```
[
    (1, "order1", "BID", 10.0, 5, False),
    (2, "order2", "ASK", 9.5, 3, False),
    (3, "order3", "ASK", 10.0, 2, False),
    (4, "order4", "BID", 9.7, 4, False),
    (5, "order2", "", 0, 0, True)
]
```

Possible Output:

```
[
    [("order1", "order2", 9.5, 3)], # order1 (bid) matches order2 (ask)
    [("order4", "order3", 10.0, 2), ("order4", "order1", 10.0, 2)] # order4 matches order3 and order1
]

```

**Judging Criteria:**

*   Correctness: The engine must correctly match orders according to price, timestamp, and quantity.
*   Efficiency: The engine must handle a large volume of orders within reasonable time constraints.
*   Code Clarity: The code should be well-structured, readable, and maintainable.
*   Design Considerations: The design should demonstrate awareness of the constraints and requirements of a decentralized environment.

This problem requires a solid understanding of data structures, algorithms, and trading mechanics. Good luck!
