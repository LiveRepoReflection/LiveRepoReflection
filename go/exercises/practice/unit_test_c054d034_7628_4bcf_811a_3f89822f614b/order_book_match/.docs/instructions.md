## Question: Decentralized Order Book Matching

**Difficulty:** Hard

**Problem Description:**

You are tasked with designing a decentralized order book matching system. This system will simulate a simplified version of a cryptocurrency exchange where users can submit buy and sell orders.  Due to the decentralized nature, orders are not processed by a central entity, but instead, matching is achieved through a peer-to-peer network.

**Data Structures:**

*   **Order:** Represents a buy or sell order. Each order has the following attributes:
    *   `OrderID`: A unique string identifier for the order.
    *   `OrderType`: An enumeration (`Buy` or `Sell`).
    *   `Price`: The price at which the order is willing to buy or sell. Represented as an integer.
    *   `Quantity`: The amount of the asset the order wants to buy or sell. Represented as an integer.
    *   `Timestamp`: The time the order was submitted. You can use Unix timestamp in nanoseconds.
    *   `SubmitterID`: A unique string that represents order submitter.

*   **Order Book:**  A collection of `Buy` orders and `Sell` orders. Your system needs to maintain separate sorted lists for `Buy` and `Sell` orders. `Buy` orders should be sorted in descending order of price (highest price first). `Sell` orders should be sorted in ascending order of price (lowest price first). Orders with the same price should be sorted by timestamp (oldest first).

**System Requirements:**

1.  **Order Submission:**  Implement a function `SubmitOrder(order Order)` that adds a new order to the appropriate side of the order book (`Buy` or `Sell`).

2.  **Order Matching:** Implement a function `MatchOrders()` that attempts to match buy and sell orders in the order book. The matching algorithm should prioritize orders based on price and timestamp, as explained above.

    *   When a match is found (a `Buy` order's price is greater than or equal to a `Sell` order's price), execute the trade. The trade quantity should be the smaller of the `Buy` order's quantity and the `Sell` order's quantity.
    *   Partially filled orders should remain in the order book with their remaining quantity.
    *   Fully filled orders should be removed from the order book.
    *   The `MatchOrders()` function should continue matching orders until no more matches can be found.
    *   Return a list of `Trade` structs representing the executed trades. Each `Trade` struct has the following attributes:
        *   `BuyOrderID`: The `OrderID` of the buy order involved in the trade.
        *   `SellOrderID`: The `OrderID` of the sell order involved in the trade.
        *   `Price`: The price at which the trade was executed.
        *   `Quantity`: The quantity of the asset traded.
        *   `Timestamp`: The timestamp of the trade.

3.  **Order Cancellation:** Implement a function `CancelOrder(orderID string)` that removes an order from the order book.

4.  **Order Book Query:** Implement functions `GetBuyOrders()` and `GetSellOrders()` that return sorted lists of the current `Buy` and `Sell` orders in the order book, respectively.

**Constraints:**

*   **Efficiency:** The `MatchOrders()` function must be efficient.  Consider the time complexity of your matching algorithm, especially as the order book grows. Aim for an efficient solution (e.g., avoid brute-force comparisons).

*   **Concurrency:**  The system should be designed to handle concurrent order submissions, cancellations, and matching operations. Use appropriate synchronization mechanisms (e.g., mutexes, channels) to prevent race conditions and ensure data consistency.

*   **Scalability:** Although you don't need to implement actual network communication, your design should consider how the system could be scaled to handle a large number of orders and users in a real-world decentralized exchange. This is more of a system design consideration to reflect in your implementation.

*   **Edge Cases:**  Handle various edge cases, such as:
    *   Empty order book.
    *   Orders with zero or negative quantity.
    *   Attempting to cancel a non-existent order.
    *   Orders with the same price and timestamp.

*   **Precision:** Ensure price and quantity calculations are accurate to avoid rounding errors that could lead to incorrect trade executions. Consider using integer representation for price and quantity to avoid floating-point inaccuracies.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:**  Does the system correctly match orders, execute trades, and maintain the order book according to the specified rules and constraints?

*   **Efficiency:** Is the matching algorithm efficient, especially for large order books?

*   **Concurrency Safety:**  Does the system handle concurrent operations correctly without race conditions or data corruption?

*   **Code Quality:** Is the code well-structured, readable, and maintainable?

*   **Error Handling:** Does the system handle edge cases and invalid inputs gracefully?

*   **Scalability Considerations:** Does the design reflect an understanding of the challenges of scaling a decentralized system?

This is a challenging problem that requires a strong understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
