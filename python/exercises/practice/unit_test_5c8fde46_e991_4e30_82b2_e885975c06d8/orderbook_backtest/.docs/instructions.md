Okay, I'm ready to create a challenging Python coding problem suitable for a high-level programming competition. Here it is:

**Problem Title:** Optimal High-Frequency Trading Strategy Backtester

**Problem Description:**

You are a quantitative analyst at a high-frequency trading firm. Your task is to develop a backtesting engine to evaluate the performance of different trading strategies on historical limit order book data.

The input data consists of a sequence of timestamped limit order book snapshots. Each snapshot represents the state of the order book at a particular point in time, containing the `price` and `quantity` available for both `bid` and `ask` orders at multiple levels.

Your backtesting engine needs to simulate the execution of trading orders based on a given strategy, considering several real-world constraints:

*   **Market Impact:** Executing large orders impacts the market price. Assume a linear market impact model: each unit traded moves the price by a fixed amount *i* (impact factor). Separate impact factor for bid and ask.
*   **Latency:** There is a fixed latency *l* (in milliseconds) between placing an order and it being filled. The order book may change during this latency period. If the order is not fully filled within the book after the latency, the remaining portion of the order is cancelled.
*   **Transaction Costs:** Each trade incurs a transaction cost *t* (as a percentage of the trade value).
*   **Inventory Limits:** The trader has a maximum inventory limit *I*. They cannot buy more than *I* units or sell more than *I* units short at any time.
*   **Order Lifetime:** An order has a maximum lifetime of *O* (in milliseconds). If an order is not filled within *O* milliseconds, it should be cancelled.

**Objective:**

Implement a function that takes:

1.  A sequence of limit order book snapshots. Each snapshot is a dictionary containing the bid and ask levels.
2.  A trading strategy function. This function receives the current order book snapshot, current timestamp, current inventory, and returns a list of orders to execute. Each order should specify the side (buy/sell), price, and quantity.
3.  The market impact factor for bid and ask, latency, transaction cost, inventory limit and order lifetime.

The function should simulate the execution of the trading strategy against the historical data and return:

*   The total profit/loss (in currency units).
*   The final inventory.
*   A list of all trades executed, including their timestamp, side, price, and quantity.
*   Maximum inventory reached during the period.

**Constraints:**

*   The solution must be computationally efficient. The backtesting engine will be used to evaluate strategies on large datasets (millions of order book snapshots).
*   The strategy function should not have access to future data (no peeking!).
*   The solution should handle various edge cases, such as:
    *   Order book gaps (missing price levels).
    *   Orders that cannot be fully filled.
    *   Orders that expire before being filled.
    *   Zero quantities or invalid prices in orders.
*   Inventory limit must be respected at all times.

**Grading Criteria:**

*   Correctness: The backtesting engine must accurately simulate order execution and calculate profit/loss.
*   Efficiency: The solution should be optimized for speed and memory usage.
*   Robustness: The solution should handle edge cases and invalid inputs gracefully.
*   Code Quality: The code should be well-structured, documented, and easy to understand.
*   Scalability: The time complexity of the algorithm should be considered.

This problem requires a deep understanding of limit order book dynamics, trading strategy implementation, and efficient algorithm design. It encourages the use of appropriate data structures and optimization techniques. Good luck!
