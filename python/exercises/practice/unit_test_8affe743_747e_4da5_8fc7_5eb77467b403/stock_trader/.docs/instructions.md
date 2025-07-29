## The Algorithmic Stock Trader's Dilemma

**Question Description:**

You are an algorithmic stock trader tasked with maximizing profit from a volatile stock market. You have access to historical stock prices for a specific company over a period of `N` days. Your trading strategy allows for a maximum of `K` transactions (buy followed by sell). Each transaction must be completed before another can begin (no overlapping transactions). You are given the following constraints:

1.  You can only hold at most one share of the stock at any given time. You must sell the stock before buying again.
2.  You must buy before you sell, and sell after you buy.
3.  You are given an array `prices` where `prices[i]` is the price of a given stock on the `ith` day.
4.  Each transaction (buy and sell) incurs a fixed transaction fee `fee`. This fee is deducted at the *sell* action.
5.  You are given an initial capital `C`. You cannot buy shares if you don't have enough money to pay for them.

Given the integer `K`, the array of prices `prices`, the transaction fee `fee`, and the initial capital `C`, write a function to calculate the maximum profit you can make.

**Constraints:**

*   1 <= `N` <= 10<sup>5</sup> (Number of days)
*   0 <= `K` <= 50 (Maximum number of transactions)
*   0 <= `prices[i]` <= 10<sup>4</sup> (Stock price on day i)
*   0 <= `fee` <= 10<sup>4</sup> (Transaction fee)
*   0 <= `C` <= 10<sup>9</sup> (Initial Capital)
*   The returned profit must be an integer.

**Optimization Requirements:**

*   The solution must be efficient enough to handle large input sizes (N = 10<sup>5</sup>). A naive O(N<sup>2</sup>K) or O(N<sup>3</sup>) solution will likely time out. Aim for a solution with time complexity close to O(NK).
*   The solution should be space-optimized. Solutions with large memory footprints might lead to memory limit exceeded errors.

**Edge Cases:**

*   Consider cases where `K` is significantly larger than the number of profitable opportunities.
*   Handle cases where the transaction fee is high enough to make all transactions unprofitable.
*   Handle cases where the initial capital is not enough to buy any stock.
*   Handle cases where the stock prices are constantly decreasing.
*   Consider the edge case of an empty `prices` array.

**Real-world Considerations:**

*   Transaction fees are a real-world constraint in stock trading.
*   Limiting the number of transactions is a common risk management strategy.
*   Initial capital limits the potential profit.

**Multiple Valid Approaches:**

*   Dynamic programming is a viable approach, but careful optimization is needed to meet the time and space constraints.
*   State machine-based approaches might offer an alternative perspective and potential for optimization.

Good luck!
