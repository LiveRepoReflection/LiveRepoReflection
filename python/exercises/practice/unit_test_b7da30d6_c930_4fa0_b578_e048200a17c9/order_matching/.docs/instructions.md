Okay, here is a challenging Python coding problem designed to be akin to a LeetCode Hard difficulty question.

## Question: Decentralized Order Book Matching Engine

**Problem Description:**

You are tasked with building a core component of a decentralized exchange (DEX): the order book matching engine. In a DEX, orders are not centrally managed but distributed across a network. Your engine will receive a stream of orders from various sources and must efficiently match compatible buy and sell orders to execute trades.

**Specifics:**

1.  **Order Representation:** An order is represented as a tuple: `(order_id, type, price, quantity)`, where:
    *   `order_id` is a unique string identifier for the order.
    *   `type` is either `"BUY"` or `"SELL"`.
    *   `price` is a positive integer representing the price per unit.
    *   `quantity` is a positive integer representing the number of units to buy or sell.

2.  **Matching Logic:**
    *   A `"BUY"` order can be matched with a `"SELL"` order if the buy price is greater than or equal to the sell price.
    *   A `"SELL"` order can be matched with a `"BUY"` order if the sell price is less than or equal to the buy price.
    *   Orders should be matched based on **price-time priority:**  Orders with better prices (highest for buys, lowest for sells) are matched first. If prices are the same, the order that was placed earlier is matched first.
    *   Partial fills are allowed. If a buy order of quantity 10 is matched with a sell order of quantity 5, the sell order is completely filled, and the buy order is partially filled with a remaining quantity of 5.
    *   The engine should maintain separate order books for buy orders and sell orders.

3.  **Order Book Management:**
    *   Orders should be stored in appropriate data structures to ensure efficient retrieval and matching. Consider data structures that allow for ordered access (based on price and arrival time).
    *   When an order is fully filled, it should be removed from the order book.

4.  **Engine Interface:** Implement a class `MatchingEngine` with the following methods:
    *   `__init__()`: Initializes the engine with empty buy and sell order books.
    *   `add_order(order)`: Adds a new order to the appropriate order book (buy or sell). Immediately attempt to match the order against existing orders in the opposing order book.
    *   `cancel_order(order_id)`: Cancels an existing order based on its `order_id`.
    *   `get_order_book()`: Returns a tuple containing two lists. The first list represents the buy order book, and the second list represents the sell order book. Each list should contain the orders currently in the order book, sorted by price-time priority (highest buy price first, lowest sell price first). Orders with the same price should be sorted by insertion order (oldest first).
    *   `get_trades()`: Returns a list of trades that have been executed. Each trade should be a tuple: `(buy_order_id, sell_order_id, price, quantity)`. The list should be in chronological order of execution.

**Constraints:**

*   The engine must handle a large volume of orders efficiently.  Consider algorithmic complexity and data structure choices.
*   The engine must be thread-safe to handle concurrent order submissions (although you don't need to implement actual multithreading, consider how your data structures would need to be modified to ensure thread safety).
*   Order IDs are unique.
*   Prices and quantities are positive integers.
*   You need to optimize for both speed and memory usage.
*   Order cancellation can happen at any time.

**Optimization Goals:**

*   Minimize the time complexity of `add_order` and `cancel_order`. Aim for better than O(n) where n is the number of orders in the book.
*   Minimize memory usage, especially when handling a large number of orders.

**Real-World Considerations:**

This problem reflects the core functionality of a real-world exchange, where efficient order matching is crucial for fair and liquid markets.  The decentralized aspect adds the layer of complexity of managing orders across a network.

This problem requires a strong understanding of data structures (priority queues, trees), algorithmic optimization, and system design considerations. Good luck!
