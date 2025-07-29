Okay, here's a challenging JavaScript coding problem designed to test advanced skills and optimization.

**Problem Title:** Real-Time Order Book Aggregator

**Problem Description:**

You are tasked with building a real-time order book aggregator for a cryptocurrency exchange. An order book represents all the buy and sell orders for a specific asset (e.g., BTC/USD) at a given time.  Your aggregator needs to efficiently process a continuous stream of order updates and provide aggregated views of the order book.

**Input:**

The input consists of a stream of order updates received as JSON strings. Each update represents a change in the order book and has the following structure:

```json
{
  "timestamp": 1678886400000, // Unix timestamp in milliseconds
  "symbol": "BTC/USD",       // Trading pair symbol
  "side": "buy" | "sell",     // "buy" for bid, "sell" for ask
  "price": 25000.00,        // Price level of the order
  "quantity": 1.5,           // Quantity of the order at the price level. Can be 0 to indicate removal of the level.
  "exchange": "ExchangeA"   // The exchange the order came from
}
```

**Output:**

Your solution must provide the following functionalities:

1.  **Real-time Order Book Reconstruction:** Maintain an accurate, up-to-date representation of the aggregated order book.  The order book should be structured to allow efficient retrieval of the best bid and ask prices.

2.  **Depth Calculation:** Given a `depth` (integer), return the *total* quantity available on both the buy and sell sides within `depth` price levels from the best bid and ask respectively. For example, if depth is 3, you need to sum the quantities of the top 3 bid levels and top 3 ask levels.  If there are fewer than `depth` levels available, sum the available levels.  The price levels must be ranked by most favorable to least favorable.  The returned value should be an object with `buy` and `sell` properties indicating the total quantity on each side.

    ```json
    {
      "buy": 4.2, // Total quantity on the buy side within the specified depth
      "sell": 3.8 // Total quantity on the sell side within the specified depth
    }
    ```

3.  **Weighted Average Price (WAP) Calculation:** Calculate the weighted average price for a specified `quantity`. The WAP should be calculated by traversing the order book (starting from the best bid/ask) until the total quantity is met.  The calculation should consider the price and quantity at each level. Return `null` if the specified quantity is not available on either the buy or sell side.  Allow specification of which *side* to calculate the WAP for. Return a single number representing the price.

**Constraints:**

*   **Performance:**  The system must handle a high volume of order updates with low latency.  Optimize for both update speed and query speed.
*   **Memory Usage:**  Minimize memory consumption, especially as the number of price levels in the order book grows.
*   **Data Consistency:**  Ensure the order book remains consistent even with out-of-order updates (consider timestamp). Older updates should be discarded.
*   **Exchange Aggregation:** Updates may come from multiple exchanges. You need to maintain an aggregated view across all exchanges.
*   **Symbol Specificity:** The system needs to handle multiple symbols simultaneously (e.g., BTC/USD, ETH/USD).
*   **Depth Limit:**  The maximum `depth` value that will be queried is 100.
*   **Quantity Precision:** Quantities are represented with high precision (up to 8 decimal places). Handle floating-point calculations carefully to avoid rounding errors.
*   **Edge Cases:**
    *   Handle cases where an order update arrives for a price level that doesn't exist yet.
    *   Handle cases where an order update reduces the quantity at a price level to zero (remove the level).
    *   Handle scenarios where there are no buy or sell orders in the order book.
    *   Handle out-of-order updates gracefully using the timestamp.

**Requirements:**

*   Implement the core data structures and algorithms for managing the order book.
*   Provide clear interfaces for updating the order book and querying data.
*   Write well-documented code that is easy to understand and maintain.
*   Consider the trade-offs between different data structures and algorithms to achieve optimal performance.

**Bonus:**

*   Implement a garbage collection mechanism to periodically remove stale or inactive symbols from memory.
*   Provide a way to persist the order book to disk for recovery after a system restart.
*   Implement circuit breakers to handle situations where one or more exchanges are unavailable.

This problem challenges your ability to design and implement a high-performance, real-time system with complex data management requirements. Good luck!
