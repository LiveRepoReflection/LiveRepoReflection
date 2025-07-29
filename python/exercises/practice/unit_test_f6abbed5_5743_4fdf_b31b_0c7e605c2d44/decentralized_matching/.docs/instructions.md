## Problem: Decentralized Order Matching Engine

**Description:**

You are tasked with designing and implementing a simplified decentralized order matching engine for a cryptocurrency exchange. The exchange operates on a blockchain, and each participant (user) has their own node. Orders are submitted to the network and need to be matched efficiently across all nodes. Due to the decentralized nature, there's no central authority to manage order matching.

**Functionality:**

1.  **Order Submission:** Each user can submit buy or sell orders for a specific cryptocurrency pair (e.g., BTC/USD). An order consists of:
    *   `order_id`: A unique identifier for the order (string).
    *   `user_id`: The identifier of the user submitting the order (string).
    *   `order_type`: Either "BUY" or "SELL" (string).
    *   `price`: The price at which the user wants to buy or sell (float).
    *   `quantity`: The amount of cryptocurrency to buy or sell (float).
    *   `timestamp`: The time the order was submitted (integer - Unix timestamp).

2.  **Order Broadcast:** When an order is submitted, it's broadcast to all other nodes in the network.  Assume a reliable broadcast mechanism exists (implementation detail not required).

3.  **Local Order Book:** Each node maintains a local order book. The order book consists of two lists: one for buy orders and one for sell orders.  Orders in each list should be sorted:
    *   Buy orders are sorted in descending order of price (highest price first). If prices are equal, sort by timestamp (earliest first).
    *   Sell orders are sorted in ascending order of price (lowest price first). If prices are equal, sort by timestamp (earliest first).

4.  **Order Matching:**  Each node continuously attempts to match buy and sell orders in its local order book. An order can be partially or fully filled. Matching occurs when the best buy order (highest price) has a price greater than or equal to the best sell order (lowest price).

    *   When a match is found, determine the trade price (see below).
    *   Determine the trade quantity, which is the minimum of the buy order quantity and the sell order quantity.
    *   Create a trade record containing:
        *   `trade_id`: A unique identifier for the trade (string).
        *   `buy_order_id`: The `order_id` of the buy order.
        *   `sell_order_id`: The `order_id` of the sell order.
        *   `price`: The trade price (float).
        *   `quantity`: The quantity traded (float).
        *   `timestamp`: The time the trade occurred (integer - Unix timestamp).
    *   Update the quantities of the buy and sell orders involved in the trade.  If an order is fully filled, remove it from the order book.
    *   The trade price is determined as follows: If the buy order's price is higher than the sell order's price, the trade price is the sell order's price. Otherwise, the trade price is the buy order's price.

5.  **Trade Execution and Synchronization:**  After a match is found, the trade needs to be executed. Assume a mechanism exists to execute the trade on the blockchain (implementation detail not required). All nodes should eventually have the same set of trade records in the same order (this implies some form of consensus mechanism is in place, but you don't need to implement that).

**Requirements:**

*   **Efficiency:** Your order matching algorithm should be as efficient as possible, especially when dealing with a large number of orders. Consider the time complexity of your matching process.
*   **Concurrency:** The system should be able to handle concurrent order submissions and matching.
*   **Immutability:** Once a trade is executed, the trade record should be immutable (cannot be changed).
*   **Global State Consistency:** Assume trades propagate through the network consistently, although processing order arrival is not necessarily in perfect global order due to network latency (eventual consistency is acceptable, but more immediate is better).
*   **Scalability:** Consider how the system might scale as the number of users and orders increases.
*   **Realistic Order Book Management:** Your implementation should accurately reflect how an order book works in a real exchange, considering order types, price levels, and time priority.

**Input:**

A series of order submissions, each represented as a dictionary with the fields described above. You will receive a stream of these orders.

**Output:**

A list of trade records, each represented as a dictionary with the fields described above, in the order they were executed.  Each node should produce the same list of trades eventually, even if the order of order arrival differs slightly.

**Constraints:**

*   The number of orders can be very large (up to 10<sup>6</sup>).
*   The system should handle multiple users submitting orders concurrently.
*   Price and quantity values should be accurate to at least 6 decimal places.
*   You can assume that user IDs are unique.
*   You can assume that order IDs are unique.

**Example:**

```python
# Example Input (stream of orders)
orders = [
    {"order_id": "1", "user_id": "A", "order_type": "BUY", "price": 10.0, "quantity": 1.0, "timestamp": 1678886400},
    {"order_id": "2", "user_id": "B", "order_type": "SELL", "price": 9.5, "quantity": 0.5, "timestamp": 1678886401},
    {"order_id": "3", "user_id": "C", "order_type": "SELL", "price": 10.0, "quantity": 0.8, "timestamp": 1678886402},
    {"order_id": "4", "user_id": "D", "order_type": "BUY", "price": 9.8, "quantity": 0.3, "timestamp": 1678886403},
    {"order_id": "5", "user_id": "E", "order_type": "BUY", "price": 10.2, "quantity": 0.2, "timestamp": 1678886404},
]

# Example Output (list of trades)
[
    {"trade_id": "trade_1", "buy_order_id": "1", "sell_order_id": "2", "price": 9.5, "quantity": 0.5, "timestamp": 1678886405}, # Assume trade occurs at this timestamp
    {"trade_id": "trade_2", "buy_order_id": "5", "sell_order_id": "2", "price": 9.5, "quantity": 0.0, "timestamp": 1678886406},
    {"trade_id": "trade_3", "buy_order_id": "5", "sell_order_id": "3", "price": 10.0, "quantity": 0.2, "timestamp": 1678886407},
    {"trade_id": "trade_4", "buy_order_id": "1", "sell_order_id": "3", "price": 10.0, "quantity": 0.3, "timestamp": 1678886408},
    {"trade_id": "trade_5", "buy_order_id": "4", "sell_order_id": "3", "price": 9.8, "quantity": 0.3, "timestamp": 1678886409}
]
```

**Scoring:**

Your solution will be evaluated based on:

*   **Correctness:** The accuracy of the order matching and trade execution.
*   **Efficiency:** The speed and memory usage of your algorithm.
*   **Scalability:** The ability of your system to handle a large number of orders.
*   **Concurrency:**  The ability to handle concurrent order submissions.
*   **Code Clarity:** The readability and maintainability of your code.
*   **Adherence to Constraints:** Compliance with all specified constraints.

Good luck!
