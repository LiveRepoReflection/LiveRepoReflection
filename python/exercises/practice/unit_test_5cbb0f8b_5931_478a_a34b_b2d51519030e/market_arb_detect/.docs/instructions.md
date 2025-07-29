Okay, here's a challenging problem designed to test a programmer's ability to handle complex data structures, optimize for performance, and address numerous edge cases within a real-world-ish scenario.

## Problem: Real-Time Market Data Aggregation and Analysis

**Description:**

You are tasked with building a system to process real-time market data for a stock exchange. The exchange receives a high volume of price quotes and trade executions for various stocks. Your system needs to efficiently aggregate this data and provide real-time analytics, specifically focusing on order book reconstruction and identifying potential arbitrage opportunities.

**Input:**

The system receives two types of data streams:

1.  **Price Quotes (Bids and Asks):** Each quote consists of:
    *   `timestamp` (milliseconds since epoch - integer)
    *   `stock_symbol` (string - e.g., "AAPL", "GOOG", "MSFT")
    *   `side` (string - "bid" or "ask")
    *   `price` (float - price per share)
    *   `quantity` (integer - number of shares)
2.  **Trade Executions:** Each execution consists of:
    *   `timestamp` (milliseconds since epoch - integer)
    *   `stock_symbol` (string)
    *   `price` (float - execution price)
    *   `quantity` (integer - number of shares traded)

The data arrives in chronological order (based on timestamp), but the volume is very high (potentially millions of messages per second).  Data for different stock symbols can be interleaved.

**Requirements:**

1.  **Order Book Reconstruction:** For each stock symbol, maintain a real-time order book.  The order book should store bids and asks, ordered by price (highest bid first, lowest ask first).  The order book must efficiently handle insertions (new quotes), updates (price/quantity changes), and deletions (quote cancellations due to trade executions or explicit cancellations).
2.  **Arbitrage Detection:** Continuously monitor the order books for potential arbitrage opportunities. An arbitrage opportunity exists if the highest bid price for a stock is greater than the lowest ask price. When an arbitrage opportunity is detected, output the `timestamp` and `stock_symbol` of the event.  The output should be in chronological order.
3.  **Data Retention Policy:**  Quotes in the order book should have a limited lifespan. Any quote older than `K` milliseconds (a configurable parameter) should be automatically removed from the order book. This is to prevent stale data from affecting arbitrage detection.
4.  **Efficiency:** The system must be highly efficient in terms of both memory usage and processing time.  The high data volume demands optimized data structures and algorithms.  Minimize latency in arbitrage detection.
5.  **Scalability:**  The system should be designed to handle a large number of different stock symbols concurrently.
6.  **Concurrency:** The system must be thread-safe to handle concurrent updates from multiple data streams.
7.  **Memory Constraint:** You are limited to a maximum of `M` GB of memory for your data structures. Exceeding this limit may result in a crash.

**Output:**

Output a list of arbitrage opportunities, with each entry containing the `timestamp` and `stock_symbol` when the arbitrage condition is first detected. Each arbitrage opportunity should only be reported once, even if the condition persists. If an arbitrage opportunity disappears and then reappears, it should be reported again.

**Constraints:**

*   `K` (data retention window): 1000 <= K <= 60000 (milliseconds)
*   `M` (memory limit): 4 <= M <= 16 (GB)
*   Number of stock symbols: Up to 100,000.
*   Price: Positive floating-point numbers with precision up to 4 decimal places.
*   Quantity: Positive integers.
*   Timestamps are monotonically increasing.

**Example:**

```
Input (Example Data):
Quote: 1678886400000, AAPL, bid, 170.00, 100
Quote: 1678886400001, AAPL, ask, 170.50, 50
Quote: 1678886400002, GOOG, bid, 2500.00, 20
Quote: 1678886400003, GOOG, ask, 2501.00, 10
Quote: 1678886400004, AAPL, ask, 169.90, 20  // Arbitrage opportunity for AAPL
Quote: 1678886400005, MSFT, bid, 280.00, 30
Quote: 1678886400006, MSFT, ask, 280.20, 15
Execution: 1678886400007, AAPL, 169.90, 20  // Resolve arbitrage
Quote: 1678886400008, AAPL, bid, 170.10, 30  // Arbitrage reappears
Quote: 1678886400009, GOOG, ask, 2499.00, 5 // Arbitrage opportunity for GOOG
```

```
Output:
1678886400004, AAPL
1678886400008, AAPL
1678886400009, GOOG
```

**Considerations:**

*   Choosing the right data structures for the order book is critical (e.g., balanced trees, heaps).
*   Efficiently handling the data retention policy (removing old quotes) is important.
*   Think about how to handle concurrent access to the order books.
*   Be mindful of memory usage, especially given the large number of stock symbols. Can you share any data structures?
*   Optimize for low-latency arbitrage detection.

This problem is designed to be challenging and requires a solid understanding of data structures, algorithms, and concurrent programming. Good luck!
