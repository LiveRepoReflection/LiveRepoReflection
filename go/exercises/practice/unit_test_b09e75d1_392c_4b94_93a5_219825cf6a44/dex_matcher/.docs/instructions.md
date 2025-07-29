## Question Title: Decentralized Order Matching Engine

**Problem Description:**

You are tasked with building a core component of a decentralized exchange (DEX): an efficient order matching engine. In this DEX, users submit orders to buy or sell a specific cryptocurrency. Due to the decentralized nature, orders are not processed by a central authority but instead need to be matched and settled using a distributed ledger.

Your engine receives a continuous stream of buy and sell orders. Each order specifies the following:

*   **Order ID:** A unique string identifier for the order.
*   **Order Type:** Either "BUY" or "SELL".
*   **Price:** The price at which the user is willing to buy or sell.
*   **Quantity:** The amount of cryptocurrency the user wants to buy or sell.
*   **Timestamp:** The time the order was submitted (Unix timestamp in nanoseconds).

Your goal is to match buy and sell orders based on price and time priority and simulate order execution.

**Matching Rules:**

1.  **Price Priority:** Sell orders with the lowest price should be matched first, and buy orders with the highest price should be matched first.
2.  **Time Priority:** Within the same price level, orders are matched based on their submission time. The earlier the order, the higher its priority.
3.  **Order Execution:** If a buy order's price is greater than or equal to a sell order's price, a match can occur. Similarly, if a sell order's price is less than or equal to a buy order's price, a match can occur.
4.  **Partial Fills:** Orders can be partially filled. If a buy order for 10 units matches with a sell order for 7 units, the buy order is partially filled for 7 units, and the sell order is completely filled. The remaining buy order will remain active in the order book.
5.  **Matching Algorithm:**  The engine should prioritize finding the best possible match for each incoming order. When a new order arrives, it should be matched immediately against the existing order book.

**Requirements:**

1.  **Order Book Representation:** Implement a suitable data structure to maintain the buy and sell orders. The order book must be highly performant for both insertion and retrieval of orders. Consider using a combination of data structures to optimize for both price and time priority.
2.  **Matching Function:** Implement a function `matchOrders(order Order)` that takes a new order as input and attempts to match it with existing orders in the order book.
3.  **Order Execution Simulation:** The `matchOrders` function should return a list of `Trade` structs representing the order executions that occurred. Each `Trade` struct should contain:
    *   `BuyerOrderID`: The Order ID of the buying order involved in the trade.
    *   `SellerOrderID`: The Order ID of the selling order involved in the trade.
    *   `Price`: The execution price of the trade.
    *   `Quantity`: The quantity of cryptocurrency traded.
    *   `Timestamp`: The current timestamp when trade happened.
4.  **Concurrency:** The matching engine must be thread-safe and capable of handling concurrent order submissions. Implement appropriate locking mechanisms to ensure data consistency.
5.  **High Performance:** The matching engine should be highly optimized for speed, as it needs to handle a large volume of orders with minimal latency.
6.  **Edge Cases:** Handle the following edge cases:
    *   Empty order book.
    *   No matching orders.
    *   Orders with zero quantity.
    *   Orders with invalid prices.

**Constraints:**

*   The maximum number of active orders at any given time can be up to 100,000.
*   The price and quantity can be represented as `float64`.
*   Assume the system clock is synchronized across all nodes.
*   The engine must be able to process at least 1,000 orders per second on a standard machine.
*   Minimize memory usage.

**Bonus Challenges:**

*   Implement a cancellation mechanism to allow users to cancel their orders.
*   Add support for different order types (e.g., market orders, limit orders).
*   Implement a mechanism to prevent front-running.
*   Integrate the matching engine with a simulated distributed ledger to record order executions.
*   Implement the ability to handle multiple crypto pairs in the same engine.

**Deliverables:**

*   A well-documented Go program that implements the decentralized order matching engine.
*   A `README` file explaining the design choices, data structures used, and optimization techniques employed.
*   Benchmark tests demonstrating the performance of the matching engine.
*   Unit tests covering all edge cases.

This problem requires a deep understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
