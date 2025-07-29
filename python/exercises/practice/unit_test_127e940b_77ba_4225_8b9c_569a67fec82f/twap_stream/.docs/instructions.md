Okay, I'm ready to create a challenging problem.

## Question: Optimized Data Streaming Aggregation

### Question Description

You are building a real-time data analytics platform for a financial exchange. The platform receives a continuous stream of trade data for various assets. Each trade contains the following information:

*   `timestamp` (in milliseconds since epoch, monotonically increasing within a single asset stream).
*   `asset_id` (a string representing the asset, e.g., "AAPL", "GOOG").
*   `price` (a floating-point number representing the trade price).
*   `volume` (an integer representing the number of shares traded).

Your task is to implement a system that efficiently calculates and maintains a set of rolling window aggregations for each asset. Specifically, you need to compute the *Time-Weighted Average Price (TWAP)* for the last N milliseconds of trade data for each asset.

**TWAP Calculation:**

The TWAP for a given time window is calculated as follows:

TWAP = (Sum of (Price \* Volume \* Time Weight)) / (Sum of (Volume \* Time Weight))

Where the Time Weight for each trade is calculated as:

Time Weight = (Trade Timestamp - Start of the Window) / Window Size
**Example:**

Given a window size of `5000` milliseconds and the following trades for asset "XYZ":

| Timestamp | Price | Volume |
| --------- | ----- | ------ |
| 1000      | 100   | 10     |
| 3000      | 110   | 5      |
| 4000      | 120   | 2      |
| 6000      | 130   | 8      |

The TWAP at timestamp `6000` would be calculated considering trades within the window `[1000, 6000]`.

*   Trade 1 (Timestamp 1000): Time Weight = (1000 - 1000) / 5000 = 0; Price \* Volume \* Time Weight = 0; Volume \* Time Weight = 0
*   Trade 2 (Timestamp 3000): Time Weight = (3000 - 1000) / 5000 = 0.4; Price \* Volume \* Time Weight = 110 \* 5 \* 0.4 = 220; Volume \* Time Weight = 5 \* 0.4 = 2
*   Trade 3 (Timestamp 4000): Time Weight = (4000 - 1000) / 5000 = 0.6; Price \* Volume \* Time Weight = 120 \* 2 \* 0.6 = 144; Volume \* Time Weight = 2 \* 0.6 = 1.2
*   Trade 4 (Timestamp 6000): Time Weight = (6000 - 1000) / 5000 = 1; Price \* Volume \* Time Weight = 130 \* 8 \* 1 = 1040; Volume \* Time Weight = 8 \* 1 = 8

TWAP = (0 + 220 + 144 + 1040) / (0 + 2 + 1.2 + 8) = 1404 / 11.2 = 125.357 (approximately)

**Requirements:**

1.  **Real-time Performance:** The system must be able to process a high volume of trade data with minimal latency.  Consider the algorithmic complexity of your solution.
2.  **Memory Efficiency:**  Minimize memory usage, especially as the number of tracked assets and the window size increase. Avoid storing all trade data indefinitely.
3.  **Accuracy:** The TWAP calculation must be accurate to at least 4 decimal places.
4.  **Scalability:** The system should be designed to handle a large number of assets concurrently.
5.  **Concurrency:** Your implementation must be thread-safe, as multiple threads will be feeding the system with trade data for different assets.
6.  **On-demand Queries:**  The system should allow querying the current TWAP for a given asset at any time. If there is no data in the time window, the function should return 0.
7.  **No External Libraries:** You are restricted to using Python's standard library *only* for this question. No external packages like NumPy, Pandas, etc., are allowed. Using `collections` or `heapq` from the standard library is acceptable.

**Input:**

*   The system will receive trade data via a function call: `update_trade(timestamp, asset_id, price, volume)`.
*   Queries for the TWAP will be made via a function call: `get_twap(asset_id)`.
*   The window size (N milliseconds) will be provided during the system's initialization.

**Output:**

*   The `get_twap(asset_id)` function should return the current TWAP for the given asset, rounded to 4 decimal places. If no trades fall within the time window, return 0.0.

**Constraints:**

*   1 <= N (window size) <= 60000 (60 seconds)
*   1 <= timestamp <= 10<sup>12</sup>
*   `asset_id` is a non-empty string consisting of alphanumeric characters.
*   0.01 <= price <= 10000.00
*   1 <= volume <= 1000

This problem challenges you to combine efficient data structures, algorithmic optimization, and concurrent programming techniques to build a performant and scalable real-time data analytics system. Good luck!
