## Question Title: Scalable Order Matching System

### Question Description

You are tasked with designing and implementing a core component of a high-frequency trading system: an order matching engine. This engine must efficiently match buy and sell orders for a single financial instrument (e.g., a specific stock).

**Order Representation:**

Each order is represented by the following information:

*   `order_id`: A unique integer identifier for the order.
*   `order_type`: Either "BUY" or "SELL".
*   `price`: The price at which the order is willing to buy (for BUY orders) or sell (for SELL orders).  The price is a positive integer.
*   `quantity`: The number of shares to buy or sell. The quantity is a positive integer.
*   `timestamp`: The time at which the order was received (represented as an integer Unix timestamp in seconds).

**Matching Logic:**

1.  A "BUY" order can be matched with a "SELL" order if and only if the BUY order's price is greater than or equal to the SELL order's price.
2.  When a match occurs, the orders are partially or fully executed, depending on the quantities.
3.  The matching engine should prioritize orders based on price and then timestamp (price-time priority).
    *   For BUY orders, the highest price has the highest priority.  If prices are equal, the earliest timestamp has the highest priority.
    *   For SELL orders, the lowest price has the highest priority.  If prices are equal, the earliest timestamp has the highest priority.
4.  If a BUY order's price is *exactly* equal to a SELL order's price, the execution is considered an "instant match" and should be processed immediately.
5.  An order can be matched with multiple counter-orders until its quantity is fully filled (i.e., becomes zero) or no matching orders are available.
6.  If a BUY order's price is strictly greater than the best available SELL order, you need to record the possible trades and execute it immediately if the new SELL order comes with an acceptable price.

**System Requirements:**

Implement the following methods in your `OrderMatchingEngine` class:

*   `__init__()`: Initializes the order matching engine.
*   `add_order(order_id, order_type, price, quantity, timestamp)`: Adds a new order to the engine. This method should attempt to match the order immediately.
*   `cancel_order(order_id)`: Cancels an existing order with the given `order_id`.  If the order is partially filled, only the remaining quantity is canceled.
*   `get_order_status(order_id)`: Returns a tuple: `(filled_quantity, is_cancelled)`. `filled_quantity` shows how much of the order has been fulfilled. `is_cancelled` indicates whether the order has been cancelled. The default value is `(0, False)` if the order never existed.
*   `get_market_depth(levels)`: Returns the top `levels` of the order book for both buy and sell orders. The return value should be a tuple: `(buy_orders, sell_orders)`.  `buy_orders` and `sell_orders` are lists of tuples, sorted by price (descending for buy, ascending for sell), where each tuple is `(price, quantity)`.  If there are fewer than `levels` distinct prices, return all available levels.
*   `process_trade(buy_order, sell_order, quantity)`: A private method to process the trade between buy and sell orders, given the quantity to trade.

**Constraints and Considerations:**

*   **Performance:** The engine must be highly performant.  Order additions and cancellations should be optimized for speed, as these operations are frequent.  Consider using appropriate data structures to achieve this.
*   **Concurrency:** While you don't need to implement actual threading, your design should be thread-safe.  Think about how you would handle concurrent access to the order book if multiple threads were adding/canceling orders simultaneously. (Describe your approach in comments).
*   **Scalability:** The engine should be able to handle a large number of orders (millions) with minimal performance degradation.
*   **Edge Cases:** Handle edge cases such as:
    *   Orders with zero quantity (should be rejected).
    *   Canceling non-existent orders (should be handled gracefully).
    *   Adding duplicate order IDs (should be rejected).
    *   Empty order book when adding orders.
*   **Correctness:** Ensure that your matching logic is correct and that orders are executed according to price-time priority.
*   **Memory Efficiency:** Consider memory usage, especially with a large number of active orders.

**Example:**

```python
engine = OrderMatchingEngine()
engine.add_order(1, "BUY", 100, 10, 1678886400)
engine.add_order(2, "SELL", 95, 5, 1678886401) # Match, order 2 is fully filled
engine.add_order(3, "SELL", 100, 3, 1678886402) # Match, order 1 is partially filled (7 remaining)
engine.add_order(4, "BUY", 102, 5, 1678886403) # No match

filled_quantity, is_cancelled = engine.get_order_status(1)  # filled_quantity = 3
filled_quantity, is_cancelled = engine.get_order_status(2)  # filled_quantity = 5
filled_quantity, is_cancelled = engine.get_order_status(4)  # filled_quantity = 0

buy_orders, sell_orders = engine.get_market_depth(2) # buy_orders = [(102, 5), (100, 7)], sell_orders = []
```

**Deliverables:**

Submit a Python class `OrderMatchingEngine` that implements the required methods.  Your code should be well-documented, and you should explain your design choices in comments, particularly regarding data structures and optimization strategies.  Focus on efficiency and scalability.
