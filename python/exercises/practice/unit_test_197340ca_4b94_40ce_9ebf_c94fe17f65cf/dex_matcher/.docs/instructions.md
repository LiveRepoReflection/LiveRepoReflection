Okay, here's a challenging Python coding problem designed with your specifications in mind.

## Problem: Decentralized Order Book Matching Engine

### Question Description

You are tasked with designing and implementing a simplified, yet highly efficient, matching engine for a decentralized exchange (DEX).  Unlike centralized exchanges that have a single, central order book, this DEX operates with multiple independent "shard" nodes, each holding a fragment of the total order book.  These shards do *not* communicate with each other directly.

Each shard node maintains its own local order book for a single trading pair (e.g., BTC/USDT).  Orders consist of a `price`, `quantity`, and `side` (buy or sell).  The exchange operates continuously, receiving a constant stream of new orders and cancellations.

Your task is to implement the core matching logic for a *single* shard node, with specific emphasis on *optimizing* for both latency and throughput.

**Input:**

Your shard node receives orders and cancellations via a message queue. Each message will be one of two types:

1.  **Order Placement:**  A new order to be added to the order book.  The order will contain:
    *   `order_id`: A unique identifier for the order (string).
    *   `timestamp`: The time the order was received (integer, milliseconds since epoch).
    *   `price`: The price at which the order is placed (integer, representing price * 10^8 to avoid floating point precision issues).
    *   `quantity`: The quantity of the asset to buy or sell (integer).
    *   `side`:  `"buy"` or `"sell"`.

2.  **Order Cancellation:** A request to cancel an existing order. The cancellation will contain:
    *   `order_id`: The ID of the order to cancel (string).
    *   `timestamp`: The time the cancellation was received (integer, milliseconds since epoch).

**Output:**

For each incoming order placement message, your engine must determine if the order can be immediately matched against existing orders in the book.

*   If a match (or partial match) occurs, you must generate trade execution messages. Each trade execution message should contain:
    *   `taker_order_id`: The ID of the order that initiated the trade (the new order).
    *   `maker_order_id`: The ID of the existing order in the book that was matched against.
    *   `price`: The price at which the trade occurred (integer, price * 10^8).
    *   `quantity`: The quantity of the asset traded (integer).
    *   `timestamp`: The timestamp of the trade execution (integer, milliseconds since epoch).

*   If the new order is not fully filled, it is added to the order book.  Orders in the book should be sorted by price (highest bid first, lowest ask first) and then by timestamp (FIFO within a price level).

*   If no match occurs, the new order is added to the order book.

For each incoming order cancellation message, you should remove the corresponding order from the order book. If the order does not exist, ignore the cancellation.

**Constraints and Requirements:**

*   **Performance is Critical:**  Your solution *must* be highly optimized for both low latency (the time to process each message) and high throughput (the number of messages processed per second).  Naive implementations will likely time out.
*   **Memory Efficiency:**  Minimize memory usage.  Large order books can consume significant memory.
*   **Atomicity:** Matching must be atomic. Either the entire trade executes according to the rules, or it doesn't execute at all.
*   **No External Communication:** Your shard node *cannot* communicate with other shard nodes.  All data must be maintained locally.
*   **Integer Arithmetic:** Use integer arithmetic throughout to avoid floating-point precision issues. All prices represent price * 10^8.
*   **Concurrency (Optional, but Highly Recommended):**  While you only need to implement the core matching logic for a single thread, consider how your design could be extended to handle concurrent message processing (e.g., using multiple threads or asynchronous programming).  Solutions that are inherently thread-safe will be viewed favorably.
*   **Realistic Scale:**  Your solution should be able to handle a sustained rate of 10,000 order placement/cancellation messages per second with an order book containing up to 1 million orders.
*   **Edge Cases:**  Consider various edge cases, such as:
    *   Orders with zero quantity.
    *   Cancellations of non-existent orders.
    *   Orders that completely fill multiple existing orders.
    *   Orders that partially fill multiple existing orders.
    *   Zero-price orders (while unusual, they might exist).
*   **Clarity and Maintainability:** While performance is paramount, your code should also be well-structured, documented, and easy to understand.
*   **Order IDs are Unique:** You can assume order IDs are globally unique.

**Example:**

Initial Order Book: Empty

Incoming Message 1:

```json
{
    "type": "order",
    "order_id": "order1",
    "timestamp": 1678886400000,
    "price": 1000000000,
    "quantity": 10,
    "side": "buy"
}
```

Output: No trades generated.  `order1` is added to the buy side of the order book.

Incoming Message 2:

```json
{
    "type": "order",
    "order_id": "order2",
    "timestamp": 1678886400001,
    "price": 1000000000,
    "quantity": 5,
    "side": "sell"
}
```

Output:

```json
[
    {
        "taker_order_id": "order2",
        "maker_order_id": "order1",
        "price": 1000000000,
        "quantity": 5,
        "timestamp": 1678886400001
    }
]
```

`order1`'s quantity is reduced to 5. `order2` is fully filled.

Incoming Message 3:

```json
{
    "type": "cancel",
    "order_id": "order1",
    "timestamp": 1678886400002
}
```

Output: No trades generated.  `order1` is removed from the order book.

This problem requires careful consideration of data structures, algorithms, and optimization techniques. Good luck!
