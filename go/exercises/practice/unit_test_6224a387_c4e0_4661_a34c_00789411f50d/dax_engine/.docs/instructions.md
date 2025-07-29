## Problem: Decentralized Autonomous Exchange (DAX) Order Matching Engine

**Description:**

You are tasked with building the core order matching engine for a decentralized autonomous exchange (DAX) operating on a blockchain. This DAX allows users to place limit orders to buy or sell tokens. Due to the decentralized nature, orders are not processed by a central authority, but rather matched and executed by the smart contract.

**Functionality:**

Your engine should efficiently match buy and sell orders based on price and time priority.  Specifically:

1.  **Order Representation:**  Orders are represented by the following attributes:
    *   `orderID`: A unique identifier for the order (string).
    *   `tokenPair`:  The trading pair (e.g., "ETH/USDT") (string).
    *   `orderType`: Either "BUY" or "SELL" (string).
    *   `price`:  The limit price at which the order should be executed (uint64 - representing the price scaled by 10^9 for precision.  For example, a price of 1.234 would be represented as 1234000000).
    *   `quantity`:  The number of tokens to buy or sell (uint64).
    *   `timestamp`: The time the order was placed (uint64 - represents the Unix timestamp in seconds).

2.  **Order Matching:**
    *   Buy orders are matched with sell orders if the buy order's price is greater than or equal to the sell order's price.
    *   Sell orders are matched with buy orders if the sell order's price is less than or equal to the buy order's price.
    *   Orders are matched based on price priority (best price first). For buy orders, the highest price has priority. For sell orders, the lowest price has priority.
    *   Within the same price level, orders are matched based on time priority (first-in, first-out).

3.  **Partial Fills:**
    *   If an order can only be partially filled, the remaining quantity should remain in the order book as a new order with the same `orderID`.
    *   If multiple orders can fully fill an order the orders should be processed from the order book until the order is filled.
    *   When an order is partially filled, a trade record should be generated.

4.  **Order Book:**
    *   Maintain a separate order book for each `tokenPair`. The order book should efficiently store and retrieve buy and sell orders, sorted by price and time.
    *   Optimize for fast insertion, deletion, and retrieval of orders.

5.  **Trade Records:**
    *   When orders are matched, generate a `TradeRecord` containing:
        *   `buyOrderID`: The `orderID` of the buy order (string).
        *   `sellOrderID`: The `orderID` of the sell order (string).
        *   `price`: The execution price (uint64).
        *   `quantity`: The quantity of tokens traded (uint64).
        *   `timestamp`: The time of the trade (uint64).

6. **Cancellation**
    * Users should be able to cancel their orders. When an order is cancelled, the order should be removed from the order book.

**Input:**

The system receives a stream of order placements, cancellations, and queries.

*   `PlaceOrder(order)`: Adds a new order to the order book.
*   `CancelOrder(orderID, tokenPair)`: Cancels an existing order in the order book.
*   `GetOrderBook(tokenPair)`: Returns the current state of the order book for the specified `tokenPair`. This should return the Buy orders sorted in descending order of price, and the Sell orders sorted in ascending order of price. Orders at the same price should be sorted in ascending order of timestamp. The order book should only contain a limited number of orders on each side (e.g., top 10 buy and top 10 sell orders)
*   `ProcessOrder(order)`: Processes an order which will match it with existing orders.

**Output:**

*   `PlaceOrder(order)`: Returns a list of `TradeRecord` generated, or an empty list if no trades occurred.
*   `CancelOrder(orderID, tokenPair)`: Returns `true` if the order was successfully cancelled, `false` otherwise.
*   `GetOrderBook(tokenPair)`: Returns the top 10 buy and top 10 sell orders in the order book as described above.
*   `ProcessOrder(order)`: Returns a list of `TradeRecord` generated, or an empty list if no trades occurred.

**Constraints:**

*   **Scalability:** The engine must handle a large volume of orders and trades per second.
*   **Low Latency:** Matching should occur with minimal delay.
*   **Immutability:**  Once a trade is executed, the `TradeRecord` is immutable.
*   **Concurrency:** The engine must be thread-safe to handle concurrent order placements and cancellations.
*   **Memory Efficiency:** Use memory efficiently to handle a large number of open orders.
*   **Gas Optimization:** (Simulated for this coding problem) Minimize the computational complexity of order matching and trade execution.  Solutions with lower time complexity will be favored. Consider how a gas limit in a blockchain environment would affect the practicality of your solution.
*   **Precision:**  Ensure accurate price and quantity calculations to avoid rounding errors.

**Bonus Challenges:**

*   Implement market orders (execute at the best available price).
*   Implement order modifiers (e.g., "fill-or-kill", "immediate-or-cancel").
*   Implement a mechanism to handle stale orders (orders that have been open for too long).
*   Implement a mechanism to detect and prevent front-running.
*   Implement a basic "maker" fee mechanism, where the users submitting the limit orders that are resting in the book will pay a lower fee than the "taker" who is matching against the resting order.

**Judging Criteria:**

*   Correctness: The engine must correctly match orders according to the specified rules.
*   Efficiency: The engine must be efficient in terms of time and memory usage.
*   Scalability: The engine must be able to handle a large volume of orders.
*   Concurrency: The engine must be thread-safe.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Gas Optimization:  Solutions with lower time complexity and efficient data structures will be favored.
