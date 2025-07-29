## The Algorithmic Stock Exchange

### Question Description

You are tasked with building a core component of a new high-frequency algorithmic stock exchange.  This exchange needs to handle a massive volume of orders with extremely low latency. A key requirement is efficient order matching and execution.

**The Problem:**

Simulate a simplified stock exchange order book and matching engine. Your system must efficiently handle the following operations:

1.  **`add_order(order_id, timestamp, stock_symbol, order_type, price, quantity)`:**  Adds a new order to the order book.
    *   `order_id`: A unique integer identifier for the order.
    *   `timestamp`:  An integer representing the time the order was placed (in nanoseconds since the epoch).  Timestamps are strictly increasing.
    *   `stock_symbol`: A string representing the stock being traded (e.g., "AAPL", "GOOG").
    *   `order_type`:  An enum or string representing the order type: either "BUY" or "SELL".
    *   `price`: An integer representing the price per share at which the order is willing to trade.
    *   `quantity`: An integer representing the number of shares to trade.

2.  **`cancel_order(order_id, timestamp)`:** Cancels an existing order from the order book.
    *   `order_id`: The ID of the order to cancel.
    *   `timestamp`: The time the cancellation request was received.  Must be *strictly greater* than the order's original timestamp.

3.  **`get_top_of_book(stock_symbol)`:**  Returns the best (highest bid and lowest ask) prices for a given stock.
    *   `stock_symbol`: The stock symbol to query.
    *   Returns a tuple `(best_bid_price, best_ask_price)`. If there are no bids, `best_bid_price` should be `None`. If there are no asks, `best_ask_price` should be `None`. If neither bid nor ask exists, return `(None, None)`.

**Matching Engine Logic:**

When a new order is added, the system must immediately attempt to match it against existing orders in the order book.

*   **BUY orders match against SELL orders.** A BUY order can execute if its price is *greater than or equal to* the price of a SELL order.
*   **SELL orders match against BUY orders.** A SELL order can execute if its price is *less than or equal to* the price of a BUY order.
*   **Price Priority:** Orders are matched based on price priority.  The best-priced orders are matched first (highest bid, lowest ask).
*   **Time Priority (FIFO):** If multiple orders exist at the same price, orders are matched in the order they were placed (earliest timestamp first).
*   **Partial Fills:** Orders can be partially filled.  If a matching order has a quantity less than the incoming order, the incoming order's quantity is reduced by the matched quantity, and the process continues until the incoming order is completely filled or no more matching orders exist.
*   **Order Execution:** When an order is matched, the corresponding trade is executed.  For this problem, you only need to update the quantities of the involved orders.  You do *not* need to track trade history.  When an order's quantity reaches 0, it should be automatically removed from the order book.

**Constraints:**

*   **Performance is critical.**  Your solution should be optimized for speed.  Assume a very high volume of `add_order` operations compared to `cancel_order` and `get_top_of_book` operations.
*   **Memory Usage:**  Minimize memory footprint.
*   **Concurrency (Optional):**  While not strictly required, consider how your data structures and algorithms could be adapted for concurrent access in a multi-threaded environment. (This will *not* be tested directly, but demonstrates deeper understanding).
*   **Data Integrity:**  Ensure that the order book remains consistent and accurate at all times. No race conditions or incorrect state.
*   **Order IDs are unique and never reused.**
*   **Timestamps are strictly increasing.**  Cancellation timestamps will always be later than the original order's timestamp.
*   **Valid Input:** Assume the input data is valid (e.g., quantities and prices are non-negative integers, order types are always "BUY" or "SELL"). You do not need to add input validation logic.

**Example:**

```python
exchange = AlgorithmicStockExchange()
exchange.add_order(1, 1000, "AAPL", "BUY", 150, 100)
exchange.add_order(2, 1001, "AAPL", "SELL", 152, 50)
exchange.add_order(3, 1002, "AAPL", "BUY", 151, 75)
exchange.add_order(4, 1003, "AAPL", "SELL", 150, 125)

# after adding the orders, order 1 (BUY at 150, quantity 100) is immediately
# matched to order 4 (SELL at 150, quantity 125).
# The trade quantity is 100 (order 1's full quantity). order 1 is fulfilled
# and removed from the book. order 4 remains with quantity 25 (125 - 100).

top_of_book = exchange.get_top_of_book("AAPL") # Returns (151, 152)

exchange.cancel_order(2, 1004) # Cancels SELL order 2.

top_of_book = exchange.get_top_of_book("AAPL") # Returns (151, 150). Order 4 is now the best ask.
```

**Focus:**

The core challenge is to design data structures and algorithms that allow for efficient order matching, insertion, cancellation, and top-of-book retrieval under high load.  Consider the trade-offs between different data structures (e.g., heaps, sorted lists, hash maps) and their impact on performance.  The optimal solution will balance speed, memory usage, and code complexity.
