## Question: Real-Time Order Book Aggregation and Analysis

**Description:**

You are tasked with building a real-time order book aggregator and analyzer for a cryptocurrency exchange. The system receives a continuous stream of order book updates from various market makers. Each update represents a change to the order book's bid or ask side at a specific price level. Your system must efficiently process these updates, maintain an aggregated order book, and provide real-time analytics on the state of the market.

**Input:**

The input consists of a stream of order book update messages. Each message is a dictionary with the following structure:

```python
{
    "timestamp": int,  # Unix timestamp of the update
    "market_maker": str, # Unique identifier for the market maker (e.g., "MM1", "MM2")
    "side": str, # "bid" or "ask"
    "price": float, # Price level of the update
    "size": float,  # Size (quantity) of the order at that price level. Can be positive (add) or negative (remove)
}
```

The updates are not necessarily ordered by timestamp or market maker. Multiple updates for the same `market_maker`, `side`, and `price` can arrive, and the `size` should be cumulatively applied.

**Requirements:**

1.  **Real-Time Aggregation:** Maintain an aggregated order book, representing the total available size at each price level for both bids and asks.
2.  **Order Book Depth:** Limit the order book depth to the top `N` levels on both the bid and ask sides, where `N` is a configurable parameter.  Only maintain the `N` best (highest bid, lowest ask) price levels. If an update would add a level beyond the top `N`, it should be discarded.
3.  **Price Level Consolidation:** If an update results in a price level having a size of zero (or becomes negative due to cumulative updates), that price level must be removed from the order book.
4.  **Efficient Data Structures:** Use appropriate data structures to ensure efficient insertion, deletion, and retrieval of price levels.  Consider the performance implications of your data structure choices.
5.  **Real-Time Analytics:**  Provide a function to calculate the *weighted average price (WAP)* for both the bid and ask sides of the order book. The WAP is calculated as the sum of (price \* size) for each level, divided by the total size. This function should be optimized for speed. Only consider the levels within the order book depth (`N`).
6.  **Concurrency:** The system should be designed to handle a high volume of concurrent updates and analytics requests. Consider thread safety and potential bottlenecks.
7.  **Constraints:**
    *   `N` (order book depth) will be a configurable parameter in the range `[1, 50]`.
    *   The number of market makers will be in the range `[1, 10]`.
    *   Timestamps will be monotonically increasing but not necessarily consecutive.
    *   Price levels will be floating-point numbers with a precision of up to 8 decimal places.
    *   Size values will be floating-point numbers and can be positive or negative.

**Output:**

Your solution should provide the following functionalities:

*   A function to ingest order book updates.
*   A function to retrieve the top `N` levels of the aggregated order book for either the bid or ask side, sorted by price (descending for bids, ascending for asks).
*   A function to calculate the weighted average price (WAP) for the bid and ask sides.

**Evaluation Criteria:**

*   Correctness: The aggregated order book and analytics must be accurate.
*   Efficiency: The system must be able to handle a high volume of updates and analytics requests with minimal latency.
*   Scalability: The design should be scalable to handle a larger number of market makers and a higher update rate.
*   Code Quality: The code should be well-structured, documented, and easy to understand.
*   Concurrency Handling: The solution should be thread-safe and avoid race conditions.

This problem requires a strong understanding of data structures, algorithms, and concurrency. It also requires careful consideration of performance optimization techniques. Good luck!
