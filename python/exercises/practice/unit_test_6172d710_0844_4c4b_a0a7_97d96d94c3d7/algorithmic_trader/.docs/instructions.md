## The Algorithmic Stock Trader's Dilemma

**Question Description**

You are a quantitative analyst working for a high-frequency trading firm. Your team has developed a sophisticated model that can predict, with a certain probability, the price movement of a specific stock within a small time window. However, the model's predictions are not perfect, and trading incurs transaction costs. Your task is to design an algorithm to maximize profit by strategically buying and selling stocks based on the model's predictions, while carefully managing risk and transaction costs.

Specifically, you are given the following:

*   **`predictions`**: A list of tuples. Each tuple represents a prediction for a single time window and contains:
    *   `timestamp`: An integer representing the start time of the window (in milliseconds since epoch).
    *   `probability`: A float between 0 and 1, representing the probability that the stock price will increase during this time window.
    *   `expected_return`: A float representing the expected percentage increase in the stock price if it does increase (e.g., 0.01 for a 1% increase).

*   **`initial_capital`**: A positive float representing the initial amount of capital you have to trade with (in USD).

*   **`transaction_cost`**: A non-negative float representing the transaction cost (as a percentage of the trade value) incurred each time you buy or sell stock.

*   **`risk_aversion`**: A non-negative float representing your risk aversion. Higher values mean you are more risk-averse. This parameter will influence how aggressively you trade.

*   **`max_holdings`**: A positive integer representing the maximum number of shares of the stock you are allowed to hold at any given time.

*   **`min_trade_size`**: A positive integer representing the minimum amount of shares of the stock you are allowed to trade at any given time.

*   **`stock_price_history`**: A list of tuples. Each tuple contains:
    *   `timestamp`: An integer representing the time (in milliseconds since epoch).
    *   `price`: A float representing the stock price at that time.

The trading environment has the following characteristics:

*   You can only buy or sell stock at the *beginning* of each time window represented in `predictions`, using the most recent stock price available in `stock_price_history` *before* that timestamp.
*   Fractional shares are *not* allowed. All trades must be in whole shares.
*   You must decide, at the beginning of each time window, how many shares to buy or sell. You can choose to do nothing.
*   You cannot "short" the stock (i.e., you cannot hold a negative number of shares).
*   Your goal is to maximize your total profit at the end of the last time window in `predictions`. This profit is calculated as the value of your remaining capital *plus* the value of your stock holdings (number of shares * current stock price).  Use the latest stock price in `stock_price_history` to calculate the value of stock holdings.

**Constraints:**

*   The list `predictions` is sorted in ascending order by timestamp.
*   The list `stock_price_history` is sorted in ascending order by timestamp.
*   Timestamps in `predictions` and `stock_price_history` may not be perfectly aligned (you might not have a stock price exactly at the beginning of each time window).
*   The stock price history must contain at least one price *before* the timestamp of the first prediction.
*   Your algorithm must be computationally efficient. Test cases will include a large number of predictions and stock price history entries. Solutions that run in exponential time will not pass.  Consider dynamic programming or other optimization techniques.
*   The stock price is guaranteed to be non-zero at all times.

**Your function should return a list of integers, `trades`. The i-th element in `trades` represents the number of shares you buy (positive integer) or sell (negative integer) at the beginning of the i-th time window in `predictions`. A value of 0 means you do nothing in that time window.**

**Scoring:**

Your solution will be evaluated based on the total profit achieved across a set of hidden test cases. The test cases will vary in length, prediction accuracy, transaction costs, risk aversion, and other parameters. A higher profit will result in a higher score.
