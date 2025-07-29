Okay, here's a high-difficulty programming competition problem:

**Problem Title: Decentralized Autonomous Exchange (DAX) Simulation**

**Problem Description:**

You are tasked with simulating the core matching engine of a Decentralized Autonomous Exchange (DAX). A DAX is a cryptocurrency exchange that operates on a blockchain and is governed by smart contracts. This removes central intermediaries and allows users to trade directly with each other.

Your simulation must handle a stream of limit orders and market orders for a single trading pair (e.g., BTC/USD). The exchange uses an order book to match buy and sell orders.

**Order Types:**

1.  **Limit Order:**  An order to buy or sell a specific quantity of an asset at a specified price or better.  If the order cannot be immediately filled, it is placed in the order book.
2.  **Market Order:** An order to buy or sell a specific quantity of an asset at the best available price in the order book. Market orders are executed immediately against existing limit orders.

**Input Format:**

Your program will receive a stream of orders, one per line, in the following JSON format:

```json
{
  "order_id": "unique_order_id",
  "timestamp": 1678886400,
  "type": "LIMIT" | "MARKET",
  "side": "BUY" | "SELL",
  "quantity": 1.0,
  "price": 40000.00 // Present only for LIMIT orders
}
```

Where:

*   `order_id` is a unique string identifier for the order.
*   `timestamp` is a Unix timestamp (seconds since epoch).
*   `type` indicates the order type (LIMIT or MARKET).
*   `side` indicates whether the order is a buy ("BUY") or sell ("SELL") order.
*   `quantity` is the amount of the asset to buy or sell. Quantities are floating-point numbers.
*   `price` is the limit price for LIMIT orders. Prices are floating-point numbers with up to two decimal places.

**Order Book Behavior:**

*   **Limit Orders:**
    *   If a limit order can be immediately filled (i.e., there are matching orders on the opposite side of the order book at a price equal to or better than the limit price), it should be filled according to price-time priority.  That is, orders at the best price are filled first, and among orders at the same price, earlier orders are filled first.
    *   If a limit order cannot be immediately filled, it should be added to the order book. Buy orders are sorted in descending order of price (highest price first), and sell orders are sorted in ascending order of price (lowest price first).  Within each price level, orders are sorted by timestamp (earliest first).
*   **Market Orders:**
    *   Market orders are filled immediately against the best available limit orders in the order book on the opposite side.
    *   If a market order cannot be completely filled because there is insufficient liquidity in the order book, it should be partially filled to the extent possible, and the remaining quantity should be considered unfulfilled. The unfulfilled amount does not enter the orderbook.
*   **Matching Logic:**
    *   When a buy order matches a sell order, a trade occurs. The traded quantity is the minimum of the remaining quantities of the buy and sell orders.
    *   Both buy and sell orders can be partially filled over time through multiple trades.
*   **Order Cancellation:** Orders can be cancelled. An order cancellation is not provided as an input. You must implement a system that supports order cancellation.

**Output Format:**

For each order received, your program should output a JSON array of trades that occurred as a result of processing that order. Each trade should be in the following format:

```json
[
    {
      "buy_order_id": "order_id_of_buy_order",
      "sell_order_id": "order_id_of_sell_order",
      "quantity": 0.5,
      "price": 40000.00,
      "timestamp": 1678886400
    }
  ]
```

*   `buy_order_id` is the `order_id` of the buy order involved in the trade.
*   `sell_order_id` is the `order_id` of the sell order involved in the trade.
*   `quantity` is the amount of the asset traded.
*   `price` is the price at which the trade occurred.
*   `timestamp` is the timestamp of the trade (taken from the order which causes the trade).

If no trades occur as a result of processing an order, output an empty JSON array: `[]`

**Constraints:**

*   The number of orders in the input stream will be up to 10<sup>6</sup>.
*   Order IDs are unique strings of up to 36 characters.
*   Quantities are positive floating-point numbers with up to 8 decimal places.
*   Prices are positive floating-point numbers with up to 2 decimal places.
*   Timestamps are integers representing seconds since the epoch.
*   The order book must be implemented efficiently to handle a large number of orders with minimal latency.
*   The simulation must be deterministic (i.e., given the same input, it must produce the same output).
*   Implement an order cancellation functionality. You should implement a function `cancel_order(order_id)` that removes the order with the given `order_id` from the orderbook. No trade will be generated by a cancellation, but any future trades will be impacted because the canceled order is no longer in the orderbook.

**Optimization Requirements:**

*   Minimize the latency of order processing. The goal is to process each order as quickly as possible.
*   Minimize memory usage. The order book can potentially grow very large, so efficient memory management is crucial.

**Edge Cases:**

*   Handle invalid input gracefully (e.g., invalid JSON format, invalid order types, non-positive quantities).  Invalid input should not crash the program but may result in the order being ignored (no output).
*   Handle cases where a limit order's price is zero or negative.
*   Handle cases where a market order arrives when the order book is empty.
*   Handle cases where a large market order depletes the order book entirely.

**Judging Criteria:**

*   **Correctness:** The program must accurately simulate the DAX order book and produce the correct trades.
*   **Efficiency:** The program must process orders with minimal latency and memory usage.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Handling of Edge Cases:** The program must handle invalid input and edge cases gracefully.
*   **Order Cancellation Implementation:** The `cancel_order` function must correctly remove orders from the orderbook, and the orderbook must remain valid.

This problem requires a good understanding of data structures (especially ordered dictionaries or trees for the order book), algorithms (for matching orders efficiently), and software engineering principles (for writing robust and maintainable code).  Good luck!
