## Question Title: Decentralized Order Book Matching Engine

### Question Description

You are tasked with designing and implementing a simplified, decentralized order book matching engine. This engine facilitates the trading of a single digital asset (e.g., a specific token) on a distributed network. Because this is decentralized, there is no central authority controlling the order book. Each node in the network maintains a partial view of the order book and participates in the matching process.

**Core Requirements:**

1.  **Order Representation:** Orders are represented as tuples: `(order_id, trader_id, side, price, quantity)`.
    *   `order_id`: A unique identifier for the order (string).
    *   `trader_id`: A unique identifier for the trader submitting the order (string).
    *   `side`: Either 'buy' or 'sell'.
    *   `price`: The price at which the trader is willing to buy or sell (integer).
    *   `quantity`: The number of units of the asset the trader wants to buy or sell (integer).

2.  **Order Book Structure:** Design a data structure to efficiently store and manage buy and sell orders.  Consider the trade-offs between different data structures in terms of insertion, deletion, and matching performance. The data structure should allow for retrieval of the best bid and ask prices.

3.  **Matching Logic:** Implement a matching algorithm that attempts to match compatible buy and sell orders.
    *   A buy order is compatible with a sell order if the buy order's price is greater than or equal to the sell order's price.
    *   Orders should be matched based on *price-time priority*: Orders with the best price (highest for buy, lowest for sell) are matched first. Among orders with the same price, the order that was submitted earlier is matched first.
    *   When a match occurs, the trade quantity is the minimum of the buy order's remaining quantity and the sell order's remaining quantity.
    *   Partially filled orders remain in the order book with their remaining quantities updated.
    *   Fully filled orders are removed from the order book.

4.  **Concurrency:**  The engine must handle concurrent order submissions and matchings from multiple nodes in the network.  Implement appropriate locking mechanisms to prevent race conditions and ensure data consistency. You should assume that multiple threads/processes might be accessing and modifying the order book simultaneously.

5.  **Network Simulation:** You do not need to implement actual network communication.  Instead, simulate the decentralized nature of the system by allowing multiple threads/processes to submit orders and execute the matching logic against a shared order book.

6.  **Trade Execution & Reporting:**  When a match occurs, generate a trade record: `(buy_order_id, sell_order_id, price, quantity)`.  Collect all trade records in a thread-safe manner.

7.  **Order Cancellation:** Implement functionality to cancel an existing order by its `order_id`.  Ensure cancellation is handled safely in a concurrent environment.

**Constraints:**

*   **Scalability:** While this is a simplified model, your design should consider potential scalability issues.  Think about how your data structures and algorithms would perform with a large number of orders. Aim for O(log n) for basic operations.
*   **Efficiency:** The matching algorithm should be as efficient as possible.  Minimizing latency is critical in a trading system.
*   **Fault Tolerance:** (Conceptual) Although you don't need to implement fault tolerance, consider how your design could be adapted to handle node failures in a real decentralized network. What data replication or consensus mechanisms might be needed?
*   **No Centralized Authority:** Avoid any centralized components that would negate the decentralized nature of the system.

**Evaluation Criteria:**

*   **Correctness:** The matching algorithm must produce correct trade executions according to the price-time priority rule.
*   **Concurrency Safety:** The solution must be thread-safe and prevent race conditions.
*   **Performance:** The solution should be efficient in terms of insertion, deletion, matching, and cancellation operations.
*   **Code Clarity and Maintainability:** The code should be well-structured, documented, and easy to understand.
*   **Scalability Considerations:** The design should demonstrate awareness of potential scalability challenges.

**Bonus (Extremely Difficult):**

*   Implement a mechanism to handle "market orders" (orders that execute immediately at the best available price).
*   Incorporate a simple fee structure (e.g., a percentage of the trade value) for each trade.
*   Simulate network latency by adding a small random delay to order submission and matching operations.
