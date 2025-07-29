## Question: Decentralized Order Matching Engine (DOME)

**Description:**

You are tasked with designing and implementing a core component of a decentralized order matching engine (DOME) for a cryptocurrency exchange. In a DOME, orders are not centrally managed but distributed across a network of nodes. Your component will be responsible for receiving order updates from various nodes, maintaining a consistent order book, and efficiently matching compatible orders.

**Specifically, you must implement the following functionalities:**

1.  **Order Representation:** Define a Go struct to represent an order. An order must contain the following information:

    *   `OrderID` (string): A unique identifier for the order.
    *   `Symbol` (string): The trading pair (e.g., "BTCUSD").
    *   `OrderType` (enum: "Buy", "Sell").
    *   `Price` (float64): The price at which the order is placed.
    *   `Quantity` (int): The quantity of the asset to be traded.
    *   `Timestamp` (int64): The time the order was created, in nanoseconds since the Unix epoch.
    *   `NodeID` (string): ID of the node that submitted the order.

2.  **Order Book Management:** Implement an in-memory order book for a single `Symbol`. The order book should efficiently store and retrieve buy and sell orders separately.  Use appropriate data structures (e.g., priority queues, balanced trees) to optimize for the following operations:

    *   `AddOrder(order Order)`: Adds a new order to the order book.
    *   `RemoveOrder(orderID string)`: Removes an order from the order book given its `OrderID`.
    *   `GetBestBid()`: Returns the highest bid price (best buy order) in the order book.  Returns `0` if no bids exist.
    *   `GetBestAsk()`: Returns the lowest ask price (best sell order) in the order book. Returns `0` if no asks exist.
    *   `GetOrders(orderType string)`: Returns all orders of a given type ("Buy" or "Sell") sorted by price (descending for buy orders, ascending for sell orders) and then by timestamp.

3.  **Order Matching:** Implement a matching algorithm that continuously attempts to match compatible buy and sell orders in the order book. When a match is found, the following actions must occur atomically:

    *   A trade execution event must be generated.  Assume you have a `TradeExecution` struct with fields like `BuyOrderID`, `SellOrderID`, `Price`, `Quantity`, and `Timestamp`. You need to package a list of `TradeExecution` structs in a way that it can be returned as a matching result.
    *   The matched quantities must be deducted from the respective orders.
    *   If an order is fully filled, it must be removed from the order book.

    Your matching algorithm must prioritize price and then time (price-time priority).  That is, orders with the best price should be matched first.  If multiple orders have the same price, the order with the earliest timestamp should be matched first.  The algorithm should run continuously in a separate goroutine.

4.  **Concurrency and Data Consistency:** The order book must be thread-safe. Multiple goroutines (simulating different nodes submitting orders) should be able to concurrently access and modify the order book without data races or inconsistencies. Use appropriate synchronization primitives (e.g., mutexes, read-write locks) to ensure data integrity.  Strive for minimal lock contention to maximize performance.

5.  **Order Validation:** Implement validation logic to ensure that incoming orders are valid. Validation checks should include:

    *   `OrderID` is unique within the order book.
    *   `Symbol` is supported (assume a predefined list of supported symbols).
    *   `Price` is positive.
    *   `Quantity` is positive.
    *   `Timestamp` is within a reasonable range (e.g., not in the future).

    Invalid orders should be rejected with appropriate error messages.

6.  **Performance Optimization:** The DOME should be optimized for high throughput and low latency. Consider the following optimizations:

    *   Efficient data structures for order book management.
    *   Minimal lock contention.
    *   Avoidance of unnecessary memory allocations.
    *   Consider the use of goroutines and channels for concurrent processing.

**Constraints:**

*   **Scalability:** The solution should be designed to handle a large number of orders (millions) and a high order submission rate (thousands per second).
*   **Correctness:** The matching algorithm must be correct and ensure that trades are executed at the best possible price for both buyers and sellers.
*   **Consistency:** The order book must remain consistent even under high load and concurrent access.
*   **Latency:** The time it takes to match an order should be minimized.
*   **Memory Usage:** The memory footprint of the order book should be kept as low as possible.
*   You should aim to write clean, well-documented, and idiomatic Go code.
*   Assume a fixed number of supported symbols.

**Bonus (Optional):**

*   Implement a mechanism for handling order cancellations.
*   Implement a persistence layer to store and retrieve the order book from a database.
*   Implement circuit breaker pattern to stop processing order updates if the matching engine falls behind significantly.
*   Implement monitoring and metrics to track the performance of the DOME.

This problem requires a deep understanding of data structures, algorithms, concurrency, and system design principles. It challenges you to build a performant and reliable order matching engine that can handle the demands of a decentralized exchange. Good luck!
