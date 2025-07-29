Okay, here's a challenging Rust programming competition problem designed to be difficult and require careful consideration of efficiency and edge cases.

## Problem: Decentralized Order Book Simulation

**Description:**

You are tasked with simulating a simplified decentralized order book for a cryptocurrency exchange. In a decentralized exchange (DEX), the order book isn't maintained by a central authority but is distributed across multiple nodes in a peer-to-peer network. This problem focuses on the core logic of maintaining and querying this distributed order book.

Each node in the network maintains a partial view of the order book, containing a subset of all active buy (bid) and sell (ask) orders.  Orders have the following properties:

*   **Order ID:** A unique string identifier for each order.
*   **Price:**  A positive integer representing the price at which the order is placed.
*   **Quantity:** A positive integer representing the number of units being bought or sold.
*   **Order Type:**  Either "buy" (bid) or "sell" (ask).
*   **Timestamp:** A non-decreasing integer representing the time when the order was created.  Later timestamps represent more recent orders.

Your task is to implement a system that can:

1.  **Ingest Orders:**  Efficiently process a stream of orders from various nodes.  New orders should be added to the order book.
2.  **Cancel Orders:**  Remove orders from the order book based on their Order ID.
3.  **Query the Order Book:**  Given a price level, retrieve the total quantity of buy and sell orders at that price.  Also, retrieve the *n* most recent buy and sell orders, separately.
4.  **Calculate Weighted Average Price:** Given a price range (minimum and maximum price), calculate the volume-weighted average price for buy and sell orders within that range.

**Constraints:**

*   **Performance:** The system must be able to handle a high volume of orders (millions).  Ingestion and query operations should be optimized for speed.
*   **Memory:** Memory usage should be carefully managed.  Avoid storing unnecessary data.
*   **Concurrency:**  While a single-threaded solution is acceptable, consider how the design could be extended to support concurrent order ingestion and querying (you don't need to implement concurrency, but the design should not preclude it).
*   **Data Structures:** Choose appropriate data structures to optimize for both insertion, deletion, and querying.  Consider trade-offs between memory usage and performance.
*   **Order Book Consistency:** If an order is cancelled, it must be removed from *all* relevant data structures to ensure query results are accurate.
*   **Timestamp Ordering:**  The 'n' most recent orders must be returned in reverse chronological order of their timestamp (newest first).
*   **Price Range:** The price range should be inclusive of both the minimum and maximum price.

**Input:**

The input will consist of a series of operations:

*   **`add_order(order_id: String, price: u32, quantity: u32, order_type: String, timestamp: u64)`:** Adds a new order to the order book.
*   **`cancel_order(order_id: String)`:** Cancels an existing order.
*   **`get_quantity_at_price(price: u32)`:** Returns a tuple `(buy_quantity: u32, sell_quantity: u32)` representing the total quantity of buy and sell orders at the given price.
*   **`get_recent_orders(n: usize)`:** Returns a tuple `(buy_orders: Vec<Order>, sell_orders: Vec<Order>)` representing the *n* most recent buy and sell orders, separately, sorted by timestamp in descending order.  If there are fewer than *n* buy/sell orders, return all available orders of that type. *Order* is a struct containing all order information.
*   **`get_weighted_average_price(min_price: u32, max_price: u32)`:** Returns a tuple `(buy_weighted_avg: f64, sell_weighted_avg: f64)` representing the volume-weighted average price for buy and sell orders within the specified price range. If there are no orders in the specified range, return `(0.0, 0.0)`.

**Output:**

The output should be the results of the query operations.

**Grading Criteria:**

*   **Correctness:**  The solution must produce accurate results for all test cases, including edge cases.
*   **Performance:**  The solution must meet the performance requirements for large datasets.  Solutions that are excessively slow may time out.
*   **Code Quality:**  The code should be well-structured, readable, and maintainable.
*   **Memory Usage:**  The solution should use memory efficiently.
*   **Rust Idiomaticity:**  The code should follow Rust best practices and idioms.

This problem requires a solid understanding of data structures, algorithms, and Rust programming. Good luck!
