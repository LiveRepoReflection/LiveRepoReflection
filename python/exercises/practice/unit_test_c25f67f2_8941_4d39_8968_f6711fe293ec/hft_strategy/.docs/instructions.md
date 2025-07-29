## Problem Title: Optimal High-Frequency Trading Strategy on a Limit Order Book

### Problem Description:

You are tasked with developing an optimal high-frequency trading strategy for a single stock using a Limit Order Book (LOB). A Limit Order Book is a record of all outstanding buy (bid) and sell (ask) orders for a particular asset, organized by price level. Your goal is to maximize profit by strategically placing and canceling limit orders within the LOB, taking advantage of short-term price fluctuations.

**Limit Order Book Representation:**

The LOB will be provided as a stream of updates. Each update consists of the following information:

*   `timestamp`: Integer representing the time of the update (in milliseconds since the start of the trading day).
*   `side`: String representing the side of the order ('bid' or 'ask').
*   `price`: Float representing the price of the order.
*   `size`: Integer representing the size (number of shares) of the order.
*   `action`: String representing the action taken on the order ('new', 'cancel', 'execute').

    *   `new`: A new limit order is placed on the LOB.
    *   `cancel`: An existing limit order is cancelled from the LOB. The `size` represents the remaining size of the order being cancelled.
    *   `execute`: A limit order is executed (filled) at the specified price and size.

**Trading Constraints:**

*   You start with an initial capital of \$1,000,000 and 0 shares of the stock.
*   You can only place limit orders (no market orders allowed).
*   You cannot hold more than 1000 shares of the stock at any given time (inventory constraint).
*   You cannot place more than 100 orders (active + historical) in total.
*   You can only place one order at a time; your decision must be made before the next LOB update is processed.
*   Transaction fees: Each order (new or cancel) incurs a fee of \$0.10 per share.
*   Minimum order size: You must order in increments of 10 shares.
*   Order prices must be multiples of \$0.01.
*   Orders cannot be placed "inside the spread". That is, a bid must have a price strictly less than the lowest ask, and an ask must have a price strictly greater than the highest bid. If the spread is zero (best bid >= best ask), orders are not allowed.

**Objective:**

Write a function `trade(timestamp, side, price, size, action, current_capital, current_inventory, order_history)` that takes the LOB update, current state of your portfolio, and your order history as input. The function should return a dictionary representing your trading decision for that update:

```python
{
    'order_type': 'new' or 'cancel' or 'hold',
    'side': 'bid' or 'ask' or None (only if order_type is 'new'),
    'price': float or None (only if order_type is 'new' or 'cancel'),
    'size': int or None (only if order_type is 'new' or 'cancel'),
    'order_id': int or None (only if order_type is 'cancel') # ID of order to cancel
}
```

*   `order_type`:
    *   `'new'`: Place a new limit order.
    *   `'cancel'`: Cancel an existing limit order.
    *   `'hold'`: Do nothing for this update.
*   `side`:  The side of the new order ('bid' or 'ask'). Required only if `order_type` is `'new'`.
*   `price`: The price of the new or cancelled order. Required only if `order_type` is `'new'` or `'cancel'`.
*   `size`: The size (number of shares) of the new or cancelled order. Required only if `order_type` is `'new'` or `'cancel'`. Must be a multiple of 10.
*   `order_id`: ID of order to cancel.

**Input Format:**

The `trade` function will receive the following inputs:

*   `timestamp` (int): The timestamp of the LOB update.
*   `side` (str): The side of the LOB update ('bid' or 'ask').
*   `price` (float): The price of the LOB update.
*   `size` (int): The size of the LOB update.
*   `action` (str): The action of the LOB update ('new', 'cancel', 'execute').
*   `current_capital` (float): Your current capital.
*   `current_inventory` (int): Your current inventory (number of shares).
*   `order_history` (dict): A dictionary containing information about all your placed orders, both active and historical. The keys are order IDs (integers, starting from 1). The values are dictionaries containing the following keys:

```python
{
    'order_id': int,
    'timestamp': int, # Timestamp when order was placed.
    'side': str, # 'bid' or 'ask'
    'price': float,
    'size': int,
    'status': str # 'active', 'filled', 'cancelled'
}
```

**Output Format:**

The `trade` function should return a dictionary in the format described above, representing your trading decision.

**Evaluation:**

Your solution will be evaluated based on the total profit generated after processing a stream of LOB updates. The profit is calculated as:

```
Final Capital + (Final Inventory * Last Traded Price) - Initial Capital
```

**Constraints:**

*   All input values will be valid.
*   You must adhere to all trading constraints outlined above.
*   The provided LOB data is realistic and may contain noise, gaps, and sudden price jumps.
*   Your algorithm must be efficient and execute within a reasonable time frame for each LOB update (e.g., less than 100ms).
*   The trading day lasts for 8 hours (8 * 60 * 60 * 1000 milliseconds).
*   At the end of the trading day, all open orders are automatically cancelled.
*   If your solution violates any of the trading constraints, it will be penalized (e.g., by deducting profit).

**Hints:**

*   Consider using data structures like sorted lists or heaps to efficiently maintain the LOB.
*   Implement a risk management strategy to avoid large losses due to unexpected price movements.
*   Experiment with different order placement strategies, such as placing orders close to the best bid/ask or using more aggressive pricing to increase the chance of execution.
*   Consider using machine learning techniques to predict short-term price movements and adjust your trading strategy accordingly.

This problem requires a strong understanding of financial markets, data structures, algorithms, and risk management. Good luck!
