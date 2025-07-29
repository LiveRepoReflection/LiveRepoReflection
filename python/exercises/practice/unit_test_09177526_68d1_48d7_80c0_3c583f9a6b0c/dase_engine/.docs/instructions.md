## Problem: Decentralized Autonomous Stock Exchange (DASE)

**Description:**

You are tasked with designing and implementing core components of a Decentralized Autonomous Stock Exchange (DASE). This DASE operates on a permissionless blockchain and facilitates the trading of tokenized stocks. The core challenge lies in efficiently managing orders, matching buyers and sellers, and ensuring fair and transparent execution, all while operating within the constraints of a blockchain environment (limited computational resources, gas costs, and immutability).

**Functionality Requirements:**

1.  **Order Submission:** Users can submit limit orders to buy or sell a specific quantity of a tokenized stock at a specified price. Orders are characterized by:

    *   `order_id`: Unique identifier for the order.
    *   `user_id`: Identifier of the user submitting the order.
    *   `stock_symbol`: Symbol of the stock being traded (e.g., "AAPL", "TSLA").
    *   `order_type`: Either "BUY" or "SELL".
    *   `price`: The limit price for the order (expressed as an integer representing the price * 10000, e.g., $100.00 would be 1000000). This avoids floating point precision issues.
    *   `quantity`: Number of shares to buy or sell.
    *   `timestamp`: The time the order was submitted (Unix timestamp).

2.  **Order Book Management:** Maintain a separate order book for each `stock_symbol`. The order book should efficiently store and organize buy and sell orders, sorted by price (highest bid first for buy orders, lowest ask first for sell orders) and then by timestamp (FIFO within the same price level).

3.  **Order Matching:** When a new order is submitted, attempt to match it against existing orders in the order book. The matching algorithm should:

    *   Prioritize price:
        *   A buy order can be matched with a sell order if the buy price is greater than or equal to the sell price.
        *   A sell order can be matched with a buy order if the sell price is less than or equal to the buy price.
    *   Prioritize time (FIFO): Within a given price level, orders are matched in the order they were received.
    *   Handle partial fills: If the quantity of the incoming order is less than the quantity of a matching order, the matching order is partially filled. If the incoming order is larger, it can be matched against multiple orders until it is fully filled or there are no more matching orders.

4.  **Trade Execution:** When a match is found, execute the trade. This involves:

    *   Decrementing the quantity of the filled orders.
    *   Generating a trade record containing:
        *   `trade_id`: Unique identifier for the trade.
        *   `buy_order_id`: `order_id` of the buy order.
        *   `sell_order_id`: `order_id` of the sell order.
        *   `price`: Execution price (the price of the sell order).
        *   `quantity`: Number of shares traded.
        *   `timestamp`: The time the trade was executed (Unix timestamp).

5.  **Order Cancellation:** Users can cancel their orders if they have not been fully filled. Cancellation should remove the order from the order book.

6.  **Price Discovery:** Implement a simple mechanism to track the "last traded price" for each `stock_symbol`. This should be updated whenever a trade is executed.

**Constraints and Considerations:**

*   **Efficiency:** The order book and matching algorithm must be efficient, as operations will be performed frequently. Consider the time complexity of your data structures and algorithms. You'll be tested on large order volumes.
*   **Scalability:** While you don't need to distribute your solution, think about how the system could scale to handle a large number of stocks and users.
*   **Immutability (Simulated):** While you are not on a real blockchain, you need to simulate the immutability by carefully design your data structure to make sure you can replay every event/action on the orderbook.
*   **Integer Arithmetic:** You *must* use integer arithmetic for all price calculations to avoid floating-point precision issues.
*   **Error Handling:** Implement robust error handling to deal with invalid orders, insufficient quantities, and other potential issues.
*   **Testability:** Design your code to be easily testable.

**Input/Output:**

You will implement a class called `DASE` with the following methods:

*   `__init__()`: Initializes the DASE.
*   `submit_order(order)`: Submits a new order (dictionary). Returns a boolean indicating success or failure.
*   `cancel_order(order_id)`: Cancels an existing order. Returns a boolean indicating success or failure.
*   `get_order_book(stock_symbol)`: Returns the current order book for a given `stock_symbol` as a dictionary containing two lists: `"bids"` (buy orders) and `"asks"` (sell orders). Orders in each list should be sorted as described above. Only return orders that haven't been fully filled or cancelled. The order should be in dict format as described above.
*   `get_trades(stock_symbol)`: Returns a list of all trades executed for a given `stock_symbol`. Each trade should be a dictionary as described above.
*   `get_last_traded_price(stock_symbol)`: Returns the last traded price for a given `stock_symbol` (as an integer representing the price * 10000). Returns `None` if no trades have been executed for that stock.

**Example Order Dictionary:**

```python
order = {
    "order_id": "12345",
    "user_id": "user1",
    "stock_symbol": "AAPL",
    "order_type": "BUY",
    "price": 1500000, # $150.00
    "quantity": 10,
    "timestamp": 1678886400
}
```

**Scoring:**

Your solution will be judged on:

*   Correctness: Accurate order matching, trade execution, and order book management.
*   Efficiency: Performance of the order matching algorithm, especially with large order books.
*   Code Quality: Readability, maintainability, and adherence to best practices.
*   Error Handling: Graceful handling of invalid inputs and edge cases.

This problem requires a solid understanding of data structures, algorithms, and financial market mechanics. Good luck!
