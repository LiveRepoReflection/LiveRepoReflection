## Project Name

**Optimal Order Allocation**

## Question Description

You are building a high-frequency trading system for a cryptocurrency exchange. The exchange provides a continuous stream of limit orders, each with a price, quantity, and a unique order ID. Your system receives incoming market buy orders and must efficiently allocate them against the existing limit orders in the order book to maximize the trade execution quantity and minimize the average execution price.

**Input:**

1.  **Order Book:** Represented as a dictionary/hashmap. Keys are prices (integers representing the smallest unit of the cryptocurrency, e.g., satoshis), and values are lists of order IDs (strings) at that price, sorted by insertion time (first in, first out - FIFO). Higher prices represent sell orders (asks), while lower prices represent buy orders (bids).

    ```python
    {
        price1: [order_id_1, order_id_2, ...],
        price2: [order_id_3, order_id_4, ...],
        ...
    }
    ```

2.  **Order Quantities:** Represented as a dictionary/hashmap mapping order IDs (strings) to their corresponding quantities (integers).

    ```python
    {
        order_id_1: quantity_1,
        order_id_2: quantity_2,
        ...
    }
    ```

3.  **Market Buy Order:** An integer representing the quantity of cryptocurrency to buy.

**Constraints:**

*   The input order book can be very large (millions of orders).
*   New limit orders are constantly being added and existing orders can be cancelled.  Cancellation is handled by a separate module outside the scope of this problem. You can assume the order book and quantities dictionaries are always internally consistent.
*   Your system must process each market buy order as quickly as possible to minimize latency.
*   You must allocate the market buy order against the limit orders in the order book to:

    1.  Maximize the quantity of the market buy order that is fulfilled. If the order book does not contain sufficient liquidity to fulfill the entire market buy order, fulfill as much as possible.
    2.  Minimize the average execution price. This means prioritizing limit orders with the lowest prices (asks) first.
    3.  Respect FIFO order at each price level.

**Output:**

A list of tuples. Each tuple represents a filled order and contains the order ID (string) and the quantity (integer) filled from that order. The list should be ordered according to the allocation strategy (lowest price, FIFO). Only include filled orders that contribute to fulfilling the market buy order.

**Example:**

```python
order_book = {
    100: ["order1", "order2"],
    101: ["order3"],
    102: ["order4", "order5"]
}

order_quantities = {
    "order1": 5,
    "order2": 10,
    "order3": 7,
    "order4": 3,
    "order5": 8
}

market_buy_order = 15

# Expected Output (one possible correct output):
# [("order1", 5), ("order2", 10)]
```

**Optimization Requirements:**

*   The solution should be highly optimized for speed. Consider using appropriate data structures and algorithms to achieve the best possible performance.
*   Aim for a solution that can handle a large volume of market buy orders with minimal latency.

**Edge Cases to Consider:**

*   Empty order book.
*   Market buy order larger than the total quantity available in the order book.
*   Market buy order smaller than the smallest order quantity in the book.
*   Multiple orders at the same price level.
*   Prices not sorted in the input `order_book`.

**Evaluation Criteria:**

*   Correctness: The solution must correctly allocate market buy orders according to the specified criteria.
*   Efficiency: The solution must be optimized for speed and handle large order books efficiently.
*   Code Clarity: The code should be well-structured, readable, and maintainable.

Good luck! This is a challenging problem that requires a solid understanding of data structures, algorithms, and optimization techniques.
