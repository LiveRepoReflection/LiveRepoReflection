## Problem: Decentralized Order Book Matching Engine

**Description:**

You are tasked with building the core matching engine for a new decentralized exchange (DEX). This DEX aims to provide high throughput and low latency order matching while operating on a blockchain where each transaction (order placement, cancellation, trade execution) incurs a significant gas cost. Your engine must efficiently handle a high volume of limit orders and market orders for a single trading pair (e.g., BTC/USDT).

The exchange operates with the following constraints:

*   **Decentralized Order Book:** The order book is not centralized. Orders are submitted as transactions to a smart contract. Your engine simulates the processing of these transactions.
*   **Gas Optimization:**  Minimize the number of operations (comparisons, iterations, data structure modifications) required to process each incoming order, as this directly translates to gas costs on a real blockchain.  Favor data structures and algorithms that provide efficient lookups and modifications.
*   **Price-Time Priority:**  Matching should strictly adhere to price-time priority. Orders at the best price are filled first, and within each price level, earlier orders are filled before later orders.
*   **Limit Orders:**  Limit orders are placed with a specific price and quantity. They are added to the order book and wait to be matched.
*   **Market Orders:** Market orders are executed immediately at the best available price(s) in the order book. Market orders specify a quantity to buy or sell.
*   **Order Cancellation:** Orders can be cancelled at any time.
*   **Partial Fills:** Orders can be partially filled. The remaining quantity of a partially filled limit order remains in the order book.
*   **Integer Arithmetic:** To avoid floating-point issues and align with typical blockchain implementations, all prices and quantities are represented as non-negative integers.
*   **Order IDs:** Each order is assigned a unique integer ID. This ID is used for identifying and cancelling orders.
*   **Order Book Representation:** You need to design an appropriate data structure to represent the order book.  Consider the trade-offs between different data structures in terms of insertion, deletion, and retrieval efficiency, especially under high load.
*   **Concurrency (Simulated):** The matching engine should be designed with concurrency in mind. Although you are not required to implement actual multi-threading, your design should be easily adaptable to concurrent order processing.  Think about how you would handle race conditions and ensure data consistency in a multi-threaded environment.
*   **Large Scale:** The system should be able to handle a large number of orders (up to 10^6) with a large number of price points.

**Input:**

A sequence of operations (represented as strings), one operation per line. Each operation can be one of the following types:

*   `LIMIT BUY <order_id> <price> <quantity>`:  Place a limit buy order with the given ID, price, and quantity.
*   `LIMIT SELL <order_id> <price> <quantity>`: Place a limit sell order with the given ID, price, and quantity.
*   `MARKET BUY <quantity>`: Place a market buy order with the given quantity.
*   `MARKET SELL <quantity>`: Place a market sell order with the given quantity.
*   `CANCEL <order_id>`: Cancel the order with the given ID.

**Output:**

For each `MARKET BUY` or `MARKET SELL` operation, output a list of trades executed. Each trade should be represented as a tuple `(order_id, price, quantity)`, where:

*   `order_id` is the ID of the limit order that was matched.
*   `price` is the price at which the trade occurred.
*   `quantity` is the quantity of the trade.

For `LIMIT` and `CANCEL` operations, no output is required.

**Constraints:**

*   `1 <= order_id <= 10^6`
*   `1 <= price <= 10^9`
*   `1 <= quantity <= 10^6`
*   The input sequence contains at most 10^6 operations.
*   All order IDs are unique.
*   Prices and quantities are non-negative integers.
*   If a `CANCEL` operation refers to a non-existent order ID, ignore the operation.

**Example:**

**Input:**

```
LIMIT BUY 1 100 10
LIMIT SELL 2 101 5
MARKET BUY 5
LIMIT SELL 3 99 7
MARKET SELL 3
CANCEL 2
MARKET BUY 5
```

**Output:**

```
[(2, 101, 5)]
[(3, 99, 3)]
[(1, 100, 5)]
```

**Judging Criteria:**

*   **Correctness:** The engine must correctly match orders according to price-time priority.
*   **Efficiency:** The engine must process operations efficiently. Solutions will be tested with large input sequences and a tight time limit.
*   **Clarity and Readability:** The code should be well-structured, documented, and easy to understand.  Even though performance is paramount, maintainability is also important.
*   **Data Structure Choice:** The selection of appropriate data structures is critical. Solutions that use inefficient data structures will likely time out.
*   **Scalability Considerations:** The code should be designed in a way that is easily scalable to handle higher order volumes and more complex matching rules in the future.

This problem requires careful consideration of data structures, algorithms, and optimization techniques to achieve the required performance within the given constraints.  Good luck!
