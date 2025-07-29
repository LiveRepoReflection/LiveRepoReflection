Okay, I'm ready to craft a challenging Javascript coding problem. Here's the problem description:

## Problem: Decentralized Order Matching Engine

### Project Name

`decentralized-order-matching`

### Question Description

You are tasked with designing and implementing a core component of a decentralized exchange (DEX): an order matching engine.  This engine will operate on a blockchain, simulated here for simplicity.  It needs to efficiently match buy and sell orders for a single asset pair (e.g., ETH/DAI).

**Core Requirements:**

1.  **Order Book:** Implement an in-memory order book. The order book should maintain separate lists of buy orders (bids) and sell orders (asks). Orders should be sorted based on price: buy orders in descending order (highest price first), and sell orders in ascending order (lowest price first). If multiple orders have the same price, they should be sorted by timestamp (oldest first).

2.  **Order Structure:** Orders should have the following structure:

    ```javascript
    {
        id: string, // Unique order ID (UUIDv4)
        type: 'buy' | 'sell',
        price: number, // Price per unit of asset
        quantity: number, // Amount of asset to buy or sell
        timestamp: number // Unix timestamp in milliseconds
        trader: string //unique trader ID
    }
    ```

3.  **Matching Algorithm:** Implement a matching algorithm that, upon receiving a new order, attempts to match it against existing orders in the order book.

    *   If a match is found (i.e., a buy order's price is greater than or equal to a sell order's price, or vice-versa), execute the trade.  The trade should execute the maximum possible quantity between the two orders.
    *   If the incoming order is partially filled, add the remaining quantity back to the order book.
    *   If the incoming order is completely filled, discard it.
    *   If no match is found, add the incoming order to the appropriate side of the order book.

4.  **Trade Execution:** When a trade is executed, generate a `Trade` object:

    ```javascript
    {
        buyOrderId: string,
        sellOrderId: string,
        price: number,
        quantity: number,
        timestamp: number
    }
    ```

5.  **Order Cancellation:** Implement a function to cancel an existing order by its `id`.

6.  **Get Order Book State:** Implement a function to return a snapshot of the current order book state, including both the buy and sell orders (sorted as described above).

7. **Concurrency:** The matching engine must be thread-safe. Assume multiple concurrent requests to add, cancel and retrieve orders.

**Constraints and Considerations:**

*   **Immutability:** The core order book data structure (especially the lists of orders) should be treated as immutable. Each modification (adding, canceling, or executing orders) should create a new version of the order book. This simulates the append-only nature of a blockchain.  You can use techniques like creating copies of arrays or using immutable data structures libraries if desired.
*   **Gas Efficiency (Simulated):** While this is Javascript and not a real blockchain, strive for efficient algorithms.  Avoid unnecessary loops or computations. Be mindful of the computational complexity of your matching algorithm.
*   **Order ID collisions:** The probability of order ID collisions should be negligible.
*   **Partial Orders:** Your solution must handle partial order fills correctly, updating the remaining quantity and adding partially filled orders back to the order book.
*   **Timestamp Accuracy:** Timestamps should be as accurate as possible (using `Date.now()`). Timestamp accuracy is crucial for order matching fairness.
*   **Large Number of Orders:** The order book should be able to handle a large number of orders (e.g., 10,000+).  Consider the performance implications of your data structures and algorithms as the order book grows.
*   **Edge Cases:** Handle edge cases such as:

    *   Orders with zero or negative quantity.
    *   Orders with zero or negative price.
    *   Attempting to cancel non-existent orders.
    *   Empty order book scenarios.
*   **Floating Point Precision:** Be aware of potential floating-point precision issues when dealing with prices and quantities.  Consider using libraries like `decimal.js` or `big.js` if necessary to ensure accurate calculations.

**API:**

You must implement the following API:

```javascript
class MatchingEngine {
    constructor();
    addOrder(order: Order): void;
    cancelOrder(orderId: string): boolean; // Returns true if the order was successfully cancelled, false otherwise.
    getOrderBook(): { bids: Order[], asks: Order[] };
}

interface Order {
    id: string;
    type: 'buy' | 'sell';
    price: number;
    quantity: number;
    timestamp: number;
    trader: string;
}

interface Trade {
    buyOrderId: string;
    sellOrderId: string;
    price: number;
    quantity: number;
    timestamp: number;
}
```

**Scoring:**

The solution will be judged based on:

*   **Correctness:**  Does the matching engine correctly match orders and generate trades according to the rules?
*   **Efficiency:** How efficiently does the matching engine process orders, especially with a large order book?
*   **Immutability:** Is the order book data treated as immutable?
*   **Concurrency:** Is the engine thread-safe?
*   **Edge Case Handling:**  Are all edge cases handled correctly?
*   **Code Clarity:** Is the code well-structured, readable, and maintainable?

This problem requires a good understanding of data structures, algorithms, concurrency, and attention to detail. Good luck!
