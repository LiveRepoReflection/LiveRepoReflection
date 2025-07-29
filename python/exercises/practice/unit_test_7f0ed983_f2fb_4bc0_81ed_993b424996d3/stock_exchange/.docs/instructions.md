## The Algorithmic Stock Exchange

**Problem Description:**

You are tasked with building the core matching engine for a highly volatile, decentralized stock exchange. This exchange operates on a continuous auction basis, meaning orders are matched and executed as soon as possible. You are given a stream of buy and sell orders arriving in real-time. Each order specifies the stock symbol, quantity, price, and a unique order ID.

**Requirements:**

1.  **Order Structure:** Each order is represented by the following information:
    *   `order_id`: A unique integer identifier for the order.
    *   `timestamp`: The time the order was received (represented as an integer).
    *   `stock_symbol`: A string representing the stock being traded (e.g., "AAPL", "GOOG").
    *   `order_type`: An enum or string representing the type of order: "BUY" or "SELL".
    *   `quantity`: An integer representing the number of shares to buy or sell.
    *   `price`: A floating-point number representing the price at which the order is to be executed.

2.  **Matching Logic:**
    *   The exchange should prioritize price and then time.  For buy orders, higher prices are prioritized. For sell orders, lower prices are prioritized.
    *   When a buy order matches a sell order (i.e., the buy price is greater than or equal to the sell price), the orders are executed. The trade occurs at the **sell order's price**.
    *   If the quantities don't match exactly, the order with the smaller quantity is completely filled, and the other order is partially filled.
    *   Partial fills should be recorded.
    *   Orders should be processed in the order they are received (FIFO within price levels).

3.  **Data Structures:**
    *   You must use appropriate data structures to efficiently manage the buy and sell order books for each stock symbol. Consider using priority queues, heaps, or ordered sets.
    *   The data structure must efficiently support adding new orders, finding matching orders, and removing filled or partially filled orders.
    *   Minimize memory usage as the system needs to handle a very large number of pending orders.

4.  **Output:**

    For each trade that occurs, your system should output a list of tuples representing the executed trades. Each tuple should contain:

    *   `(buy_order_id, sell_order_id, quantity, price)`

    If no trade occurs when an order is processed, the output should be an empty list `[]`.

5.  **Concurrency:** The input stream of orders is high volume. Design your matching engine to be thread-safe and potentially handle concurrent order processing.  While you don't need to implement actual threading/multiprocessing for the submission, your data structures and matching logic must be designed with concurrency in mind to avoid race conditions if it were to be deployed in a multi-threaded environment.  Explain your concurrency strategy in comments.

6.  **Efficiency:** Your solution must be highly efficient in terms of both time and space complexity. The exchange processes a massive number of orders per second, so performance is critical. Focus on optimizing your matching algorithm and data structure implementations.

7.  **Edge Cases:**

    *   Handle cases where the order book is empty for a given stock symbol.
    *   Handle cases where an order is fully filled upon arrival.
    *   Handle cases where multiple orders can be matched against a single incoming order.
    *   Gracefully handle invalid order data (e.g., negative quantities, invalid stock symbols - you can choose to ignore or raise an exception, clearly document your approach).

8.  **Constraints:**

    *   The number of distinct stock symbols can be large (e.g., 10,000).
    *   The number of orders per stock symbol can be very high (e.g., millions).
    *   The range of prices can be wide.
    *   Minimize latency: the time to process each order and generate the trade output needs to be as low as possible.
    *   Assume that the input orders are pre-validated to be of correct format. No need to validate them.

**Example:**

**Input Order Stream:**

```
[
    (1, 1678886400, "AAPL", "BUY", 100, 170.00),
    (2, 1678886401, "AAPL", "SELL", 50, 165.00),
    (3, 1678886402, "AAPL", "SELL", 60, 165.00),
    (4, 1678886403, "GOOG", "BUY", 20, 2500.00),
    (5, 1678886404, "GOOG", "SELL", 20, 2490.00),
    (6, 1678886405, "AAPL", "BUY", 60, 165.00) # This trade will occur at 165.00
]
```

**Output:**

```
[
    [(1, 2, 50, 165.00)],  # Buy order 1 matches sell order 2 for 50 shares at 165.00
    [(1, 3, 50, 165.00)],  # Buy order 1 matches sell order 3 for 50 shares at 165.00
    [(4, 5, 20, 2490.00)], # Buy order 4 matches sell order 5 for 20 shares at 2490.00
    [(6, 3, 10, 165.00)] # Buy order 6 matches sell order 3 for 10 shares at 165.00

]
```

**Grading Criteria:**

*   Correctness of the matching logic
*   Efficiency of the data structures and algorithms
*   Concurrency safety and design considerations
*   Handling of edge cases
*   Code clarity and readability
*   Optimization of time and space complexity
