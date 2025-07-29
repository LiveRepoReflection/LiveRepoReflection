## Problem: Decentralized Order Book Matching Engine

**Question Description:**

You are tasked with implementing a core component of a high-frequency, decentralized exchange (DEX): the order book matching engine. In a decentralized environment, orders are submitted by users to a network, and your engine is responsible for efficiently matching compatible buy and sell orders to facilitate trades.

**Data Model:**

*   **Order:** Represents a buy or sell order.
    *   `order_id`: Unique identifier (UUID).
    *   `timestamp`: Time the order was submitted (nanoseconds since epoch).
    *   `order_type`: `Buy` or `Sell`.
    *   `price`: Price at which the order is willing to trade.  Represented as an integer (e.g., $10.50 would be 1050).
    *   `quantity`: Number of units to trade. An unsigned 64 bit integer.
    *   `user_id`: Identifier of the user placing the order.
    *   `signature`: Digital signature of the order, ensuring authenticity and non-repudiation. (String, assumed to be validated elsewhere)
*   **Trade:** Represents a successful match between a buy and sell order.
    *   `buy_order_id`: ID of the buy order.
    *   `sell_order_id`: ID of the sell order.
    *   `price`: Price at which the trade occurred.
    *   `quantity`: Number of units traded.
    *   `timestamp`: Time the trade occurred (nanoseconds since epoch).

**Requirements:**

1.  **Order Book Management:** Implement a data structure to efficiently store and manage buy and sell orders.  The order book should be sorted by price, with the best buy orders (highest price) and best sell orders (lowest price) at the top. If multiple orders exist at the same price, orders should be processed in FIFO (first-in, first-out) order based on their timestamp.

2.  **Matching Algorithm:**  Implement a matching algorithm that continuously looks for compatible orders (buy and sell) in the order book. When a match is found:
    *   Create a `Trade` record.
    *   Reduce the quantity of the orders involved in the trade accordingly.
    *   If an order is completely filled (quantity becomes 0), remove it from the order book.
    *   The matching process should prioritize orders with better prices and earlier timestamps within the same price level.

3.  **Concurrency:**  Your matching engine must be thread-safe and capable of handling concurrent order submissions and order book modifications.  Assume a high volume of incoming orders.

4.  **Persistence:**  Periodically (e.g., every 5 seconds), the entire order book and the list of trades executed since the last persistence operation must be saved to disk. The format is up to you, but it must be efficient and allow for quick recovery. On startup, the engine should load the order book and trade history from the disk.

5.  **Order Cancellation:** Implement order cancellation based on `order_id`. A user should be able to cancel an order they have placed, removing it from the order book.

6.  **Performance:**  The matching engine must be highly performant.  Minimize latency for order matching.  Consider algorithmic complexity and data structure choices carefully.  Assume a large volume of orders and a constantly changing order book.

**Constraints:**

*   The order book can hold a maximum of 1,000,000 buy orders and 1,000,000 sell orders.
*   The system should be resilient to sudden bursts of order submissions.
*   Disk I/O for persistence should not significantly impact matching engine performance.
*   The timestamp is guaranteed to be monotonically increasing.
*   Invalid order signatures are assumed to be handled before reaching the matching engine, so you can assume all signatures are valid.
*   You do not need to implement network communication or order validation (signature, user permissions, etc.). Focus solely on the order book management and matching logic.

**Evaluation Criteria:**

*   **Correctness:**  Does the matching engine correctly match orders and generate accurate trade records?
*   **Performance:**  What is the average latency for matching orders? How does the engine scale under high load?
*   **Concurrency:**  Is the engine thread-safe and does it handle concurrent operations correctly?
*   **Persistence:**  Does the engine correctly persist and recover the order book and trade history?
*   **Code Quality:**  Is the code well-structured, readable, and maintainable?  Are appropriate data structures and algorithms used?

This problem requires a deep understanding of data structures, algorithms, concurrency, and system design, making it a challenging and sophisticated programming task. Good luck!
