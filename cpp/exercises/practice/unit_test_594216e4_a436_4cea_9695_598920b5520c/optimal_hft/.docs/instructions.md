## Problem: Optimal High-Frequency Trading Strategy

**Description:**

You are a quantitative analyst tasked with developing an optimal high-frequency trading strategy for a specific stock. You have access to a stream of real-time order book data. The order book contains a limited number of price levels for both buy (bid) and sell (ask) orders.

**Input:**

The input consists of a continuous stream of order book updates. Each update contains the following information:

*   `timestamp`: An integer representing the time of the update in milliseconds since the start of the trading day (e.g., 36000000 represents 10:00:00 AM).
*   `bid_prices`: A sorted list of floating-point numbers representing the bid prices at different levels of the order book (highest to lowest).
*   `bid_sizes`: A list of integers representing the corresponding sizes (number of shares) available at each bid price.
*   `ask_prices`: A sorted list of floating-point numbers representing the ask prices at different levels of the order book (lowest to highest).
*   `ask_sizes`: A list of integers representing the corresponding sizes (number of shares) available at each ask price.
*   `spread_cost`: A floating-point number representing the transaction cost for each trade (commission, slippage, etc.) based on the spread.

**Trading Rules and Constraints:**

1.  **Inventory Limit:** You can hold at most `K` shares of the stock at any given time. Initially, you have 0 shares.
2.  **Order Execution:** You can execute market orders to buy at the lowest ask price or sell at the highest bid price. You can only trade up to the available size at that price level. Assume immediate order execution.
3.  **Transaction Costs:** Each trade incurs a transaction cost of `spread_cost` multiplied by the number of shares traded. This cost is deducted from your profit.
4.  **Time Limit:** You can only trade between the start and end times of the trading day.
5.  **Profit Calculation:** Your profit is calculated as the sum of the selling prices of the shares you sold, minus the sum of the buying prices of the shares you bought, minus the total transaction costs incurred.
6.  **No Short Selling:** You cannot sell shares you do not own.
7.  **Maximum Levels in Order Book:** The number of price levels in `bid_prices`, `bid_sizes`, `ask_prices`, and `ask_sizes` is limited to a maximum of `L` levels.
8.  **Batch Processing:** To simulate real-time constraints, you must process the stream of order book updates in batches. You receive a batch of `N` updates at a time and must make trading decisions for all of them before receiving the next batch.

**Objective:**

Design an algorithm that maximizes your profit by making optimal trading decisions for each batch of order book updates, subject to the trading rules and constraints.

**Specific Requirements:**

*   Your solution must be efficient enough to process the stream of updates in real-time. The benchmark testing will simulate a high-frequency environment with strict time constraints.
*   Consider the trade-offs between immediate profit and potential future opportunities. A greedy approach may not be optimal.
*   Your solution should be robust and handle various market conditions, including volatile periods and periods of low liquidity.
*   You need to implement a function that takes a batch of order book updates as input and returns a list of trading decisions. Each decision should specify the timestamp, the action ("buy" or "sell"), and the number of shares to trade.
*   The return output should be in a json format.

**Constraints:**

*   `1 <= N <= 100` (Batch size)
*   `1 <= L <= 5` (Maximum number of price levels in the order book)
*   `1 <= K <= 1000` (Inventory limit)
*   The trading day starts at timestamp 0 and ends at timestamp 57600000 (16:00:00, 4 PM).
*   Price levels are always sorted as described above.
*   All prices and sizes are non-negative.

**Example:**

```
// Simplified example for illustration
Input:
[
  {
    "timestamp": 36000000,
    "bid_prices": [100.0, 99.9],
    "bid_sizes": [10, 20],
    "ask_prices": [100.1, 100.2],
    "ask_sizes": [15, 25],
    "spread_cost": 0.01
  }
]

Possible Output:
[
  {
    "timestamp": 36000000,
    "action": "buy",
    "shares": 10
  }
]
```

**Scoring:**

Your solution will be evaluated based on the total profit generated over a simulated trading day. The solution with the highest profit wins. Efficiency and robustness will also be considered in the evaluation.

**Hints:**

*   Consider using dynamic programming or reinforcement learning techniques to optimize your trading strategy.
*   Carefully manage your inventory to avoid being stuck with unprofitable positions at the end of the trading day.
*   Experiment with different trading strategies and parameter tuning to find the optimal configuration.
*   Optimize your code for performance to meet the real-time constraints.
*   Be mindful of floating-point precision issues.

This problem requires a deep understanding of algorithmic trading, data structures, and optimization techniques. It challenges candidates to design a sophisticated and efficient trading strategy that can adapt to changing market conditions. Good luck!
