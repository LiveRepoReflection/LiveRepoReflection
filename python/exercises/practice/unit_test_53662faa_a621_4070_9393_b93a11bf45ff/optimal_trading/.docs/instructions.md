## Problem: Optimal High-Frequency Trading Strategy

### Question Description

You are a quantitative analyst at a high-frequency trading firm. You have access to a stream of order book data for a specific stock. Your task is to design and implement an algorithm to maximize profit by placing buy and sell orders based on the order book information.

The order book is represented as a sequence of snapshots. Each snapshot contains the top `N` levels of bids and asks, along with their corresponding sizes (volume).

**Input:**

Your program will receive a stream of order book snapshots. Each snapshot is a dictionary with the following structure:

```python
{
    'timestamp': int,  # Unix timestamp of the snapshot
    'bids': list[tuple[float, int]],  # List of (price, size) tuples for bids, sorted in descending order of price
    'asks': list[tuple[float, int]],  # List of (price, size) tuples for asks, sorted in ascending order of price
    'mid_price': float # the mid_price of current timestamp, defined as (best_bid + best_ask) / 2
}
```

The `bids` and `asks` lists contain at most `N` levels.  `N` will be a parameter of your algorithm. The prices are floating-point numbers, and the sizes are integers.

**Constraints:**

1.  **Transaction Costs:** There is a transaction cost of `T` per share traded (both buy and sell).
2.  **Inventory Limit:** You can hold a maximum of `I` shares of the stock at any given time (long or short).  Exceeding this limit will result in immediate liquidation of the excess shares at the *current* best bid/ask price, incurring transaction costs.
3.  **Order Size Limit:** You can place a maximum order size of `O` shares at a time.  If you want to trade more than `O` shares, you need to split it into multiple orders.
4.  **Latency:**  Assume a fixed latency `L` (in milliseconds) between placing an order and the order being filled. This means that you cannot react to the immediate next snapshot if you have just placed an order. After `L` ms, an order is immediately and completely filled at the price prevailing at the time the order was *placed*.
5.  **Market Impact:** Placing large orders can move the price. Assume that buying `x` shares increases the best ask price by `M * x`, and selling `x` shares decreases the best bid price by `M * x`. The price impact is temporary and only affects the execution price of the current order.
6.  **Time Limit:** Your algorithm must process each snapshot within a given time limit (e.g., 10 milliseconds). If it exceeds this limit, the snapshot will be skipped, and your algorithm will proceed to the next snapshot.
7.  **No Partial Fills:** Orders are filled completely or not at all. If the order cannot be filled at the simulated price (after market impact), it's considered not filled.
8. **Maximum lookahead:** Your algorithm cannot "look ahead" into the future snapshots. It must make decisions based only on the current and past snapshots.

**Objective:**

Implement a function `trading_algorithm(order_book_snapshot, current_inventory, last_trade_timestamp)` that takes an order book snapshot, the current inventory (number of shares held), and the timestamp of the last trade (or 0 if no trades have been made yet) as input, and returns a trading decision.

The trading decision should be a tuple `(action, quantity)`.

*   `action` can be one of the following strings: `"BUY"`, `"SELL"`, or `None` (for doing nothing).
*   `quantity` is an integer representing the number of shares to buy or sell.

**Example:**

```python
def trading_algorithm(order_book_snapshot, current_inventory, last_trade_timestamp):
  # Implement your trading strategy here
  if order_book_snapshot['mid_price'] > 100 and current_inventory < I:
    return ("BUY", min(O, I - current_inventory))
  elif order_book_snapshot['mid_price'] < 90 and current_inventory > -I:
    return ("SELL", min(O, I + current_inventory))
  else:
    return (None, 0)
```

**Evaluation:**

Your algorithm will be evaluated based on its total profit (or loss) over a simulated trading period. The simulation will use a series of order book snapshots. The profit will be calculated as the sum of all realized gains from selling shares minus the sum of all costs from buying shares, taking into account transaction costs, market impact, and inventory liquidations.

**Hints:**

*   Consider using techniques like moving averages, order book imbalance analysis, or simple machine learning models to predict short-term price movements.
*   Pay close attention to the transaction costs, inventory limits, and latency constraints.
*   Optimize your code for speed to meet the time limit per snapshot.
*   Think about how to manage your inventory to minimize liquidation risks.
*   Experiment with different values for `N`, `T`, `I`, `O`, `L`, and `M` to find the optimal trading strategy.

This problem requires a strong understanding of financial markets, algorithmic trading strategies, and efficient coding practices. Good luck!
