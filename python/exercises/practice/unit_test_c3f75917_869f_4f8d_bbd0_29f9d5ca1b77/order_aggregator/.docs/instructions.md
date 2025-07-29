## Question: Scalable Order Book Aggregator

### Project Description

You are tasked with building a highly scalable order book aggregator. This aggregator will receive a stream of limit orders from multiple exchanges and maintain an aggregated order book. The challenge lies in efficiently processing a large volume of orders in real-time while providing accurate and up-to-date order book information.

**Real-World Scenario:** Imagine you're building a core component for a high-frequency trading platform. You need to combine order data from multiple exchanges to give traders the best possible view of market depth and price.

**Input:**

Your system will receive a continuous stream of `Order` objects. Each `Order` will have the following attributes:

*   `exchange_id`: A string identifying the exchange the order originates from (e.g., "ExchangeA", "ExchangeB").
*   `order_id`: A unique integer ID for the order within that exchange.
*   `timestamp`: An integer representing the time the order was received (Unix epoch milliseconds).
*   `side`: An enumeration of "BID" (buy) or "ASK" (sell).
*   `price`: A floating-point number representing the order price.
*   `quantity`: An integer representing the number of shares being offered or requested.
*   `action`: An enumeration of "NEW", "AMEND", or "CANCEL".

    *   `NEW`: A new order is being placed.
    *   `AMEND`: An existing order's quantity is being updated.  You will receive the `order_id` of the order to amend, and the `quantity` to change it to. Price can be assumed to be the same.
    *   `CANCEL`: An existing order is being completely removed. You will receive the `order_id` of the order to cancel.

**Output:**

Your system should provide a method, `get_top_n_levels(side, n)`, that returns the top `n` levels of the aggregated order book for the specified `side`.  "Top" refers to the best prices. For "BID" side, it's the highest prices; for "ASK" side, it's the lowest prices.

The return value should be a list of tuples, sorted by price (descending for BID, ascending for ASK), where each tuple contains `(price, quantity)`.  If there are fewer than `n` levels, return all available levels.

**Example:**

```python
# Example Order:
Order(exchange_id="ExchangeA", order_id=123, timestamp=1678886400000, side="BID", price=100.0, quantity=100, action="NEW")

# Expected output for get_top_n_levels("BID", 2):
# [(100.0, 100), (99.5, 50)]  # Assuming 99.5 with quantity 50 is the next best bid
```

**Constraints and Requirements:**

*   **Scalability:** Your system must handle a high volume of incoming orders (millions per second).
*   **Low Latency:**  `get_top_n_levels` must return quickly, as traders need real-time information.
*   **Accuracy:** The aggregated order book must accurately reflect the current state based on the order stream.
*   **Memory Efficiency:** Minimize memory usage.  Holding every single order in memory indefinitely is not an option.
*   **Concurrency:**  The order stream and `get_top_n_levels` calls will be executed concurrently.  Ensure thread safety.
*   **Price Precision:** Prices are floating-point numbers. Be aware of potential precision issues when comparing or aggregating prices.  Consider using a fixed-point representation or an appropriate tolerance for comparisons.
*   **Order ID Uniqueness:** Order IDs are only unique *per exchange*. The aggregator must handle orders with the same ID from different exchanges.
*   **"Stale" Data Handling:** Exchanges may send delayed or out-of-order updates.  You need to handle this gracefully, potentially ignoring outdated orders based on their timestamp.  Assume orders older than a certain configurable threshold (e.g., 5 seconds) are stale and should be ignored.

**Bonus Challenges:**

*   Implement a mechanism to handle exchange downtime. If an exchange stops sending updates, how do you ensure its orders are eventually removed from the aggregated book?
*   Implement a way to track the contribution of each exchange to the aggregated order book.
*   Add support for order types beyond limit orders (e.g., market orders, iceberg orders).

This problem requires careful consideration of data structures, algorithms, concurrency, and system design principles. A naive solution will likely fail to meet the scalability and latency requirements. Think carefully about how to optimize your implementation. Good luck!
