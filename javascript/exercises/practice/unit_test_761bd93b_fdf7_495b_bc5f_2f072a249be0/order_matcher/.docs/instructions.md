## Project Name

**Optimal Order Allocation**

## Problem Description

You are tasked with building a core component for a high-frequency trading system for a cryptocurrency exchange. The system receives a continuous stream of limit sell orders (asks), which constitute the order book. Your component must process incoming market buy orders by efficiently matching them against the existing limit orders in the book. The goal is to maximize the trade execution quantity while minimizing the average execution price.

**Input:**

1.  **Order Book:** A map-like data structure (e.g., a JavaScript `Object` or `Map`) representing the sell-side (ask side) of the order book.
    *   **Keys:** Prices (integers, representing the smallest currency unit, e.g., satoshis).
    *   **Values:** An array of unique order IDs (strings) at that price, sorted by their time of insertion (First-In, First-Out - FIFO).

    ```
    // Example Structure
    {
        price1: [order_id_1, order_id_2, ...],
        price2: [order_id_3, order_id_4, ...],
        ...
    }
    ```

2.  **Order Quantities:** A map-like data structure that links each order ID (string) to its corresponding quantity (integer).

    ```
    // Example Structure
    {
        order_id_1: quantity_1,
        order_id_2: quantity_2,
        ...
    }
    ```

3.  **Market Buy Order Quantity:** An integer representing the total quantity of the asset to be purchased.

**Constraints & Allocation Rules:**

*   The input order book can be very large, potentially containing millions of orders.
*   Your system must process each market buy order with minimal latency.
*   You must allocate the market buy order against the limit sell orders according to the following rules, in order of priority:
    1.  **Minimize Average Price:** Match against orders with the lowest available price first.
    2.  **Respect FIFO:** For orders at the same price level, match against them in the order they were placed (First-In, First-Out).
    3.  **Maximize Fulfilled Quantity:** If the order book's total liquidity is less than the market order's quantity, fill as much of the order as possible.

**Output:**

Return an array of tuples (or nested arrays), where each tuple represents a match. Each tuple should contain the `order_id` (string) and the `quantity` (integer) filled from that specific limit order. The list must be sorted according to the allocation sequence (by ascending price, then by FIFO). Only include orders that were partially or fully filled to satisfy the market buy order.

**Example:**

```javascript
const orderBook = {
    100: ["order1", "order2"],
    101: ["order3"],
    102: ["order4", "order5"]
};

const orderQuantities = {
    "order1": 5,
    "order2": 10,
    "order3": 7,
    "order4": 3,
    "order5": 8
};

const marketBuyOrderQuantity = 15;

// Expected Output:
// A market buy order for 15 will be filled by:
// - Taking the full quantity of "order1" (5) at price 100.
// - Taking the full quantity of "order2" (10) at price 100.
// The total filled is 5 + 10 = 15.

// [["order1", 5], ["order2", 10]]
```

**Optimization Requirements:**

*   The solution must be highly optimized for speed. Consider the most efficient data structures and algorithms for this task.
*   The implementation should be designed to handle a high volume of transactions with consistently low latency.

**Edge Cases to Consider:**

*   An empty order book.
*   A market buy order quantity that is larger than the total available quantity in the order book.
*   A market buy order quantity that is smaller than the quantity of the first available limit order.
*   Multiple orders at the same price level (handled by FIFO).
*   The prices (keys) in the input `orderBook` are not guaranteed to be sorted.

**Evaluation Criteria:**

*   **Correctness:** The solution must accurately allocate the market order according to the specified rules.
*   **Efficiency:** The solution must be performant and scale well with a large order book.
*   **Code Clarity:** The code should be well-structured, readable, and maintainable.