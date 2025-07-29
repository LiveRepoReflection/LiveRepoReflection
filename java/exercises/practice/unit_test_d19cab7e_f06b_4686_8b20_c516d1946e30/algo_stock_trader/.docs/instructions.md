## The Algorithmic Stock Trader's Dream

**Problem Description:**

You are developing a sophisticated stock trading algorithm for a high-frequency trading firm. The algorithm analyzes a continuous stream of real-time stock data to identify and execute profitable trades. The core of the algorithm relies on efficiently identifying arbitrage opportunities across multiple exchanges.

Specifically, you are given a stream of stock price updates for a set of `N` stocks, traded across `M` different exchanges. Each stock has a unique ID, and each exchange has a unique ID.  The price updates arrive in a random order, meaning you might receive multiple updates for the same stock on the same exchange, or for different stocks on different exchanges, all interleaved in the input stream.

Your task is to design a system that can efficiently detect and report arbitrage opportunities. An arbitrage opportunity exists when it is possible to buy a stock on one exchange and simultaneously sell it on another exchange at a higher price, making a profit (ignoring transaction fees and slippage for the sake of simplicity).

**Input:**

The input consists of a continuous stream of price updates. Each update is represented as a tuple: `(timestamp, stock_id, exchange_id, price)`.

*   `timestamp`: A long integer representing the time the update was received (in milliseconds since epoch).  Updates are *not* guaranteed to be in chronological order.
*   `stock_id`: An integer representing the unique ID of the stock. (1 <= `stock_id` <= `N`)
*   `exchange_id`: An integer representing the unique ID of the exchange. (1 <= `exchange_id` <= `M`)
*   `price`: A double representing the price of the stock on the given exchange at the given timestamp.

**Output:**

Your system should output a list of arbitrage opportunities as they are detected. Each arbitrage opportunity should be represented as a tuple: `(stock_id, buy_exchange_id, sell_exchange_id, buy_price, sell_price, timestamp)`.

*   `stock_id`: The ID of the stock involved in the arbitrage.
*   `buy_exchange_id`: The ID of the exchange where the stock should be bought.
*   `sell_exchange_id`: The ID of the exchange where the stock should be sold.
*   `buy_price`: The price at which the stock should be bought.
*   `sell_price`: The price at which the stock should be sold.
*   `timestamp`: The timestamp of the *later* of the two prices used in the arbitrage.

**Constraints and Requirements:**

1.  **Real-time Performance:** The system must process the stream of updates with minimal latency.  The firm expects to process hundreds of thousands of updates per second.
2.  **Arbitrage Detection Threshold:** Only report arbitrage opportunities where the price difference ( `sell_price` - `buy_price` ) is greater than or equal to a given threshold `min_profit`. This value will be provided as a constructor argument.
3.  **Data Staleness:** Consider that stock prices are constantly changing. An arbitrage opportunity is considered invalid if the time difference between the `buy` and `sell` prices exceeds a maximum staleness threshold, `max_staleness` (in milliseconds). This value will be provided as a constructor argument.
4.  **Memory Usage:** Minimize memory usage. The system should be able to handle a large number of stocks and exchanges without running out of memory.
5.  **Concurrency:** The input stream can be multi-threaded. Your data structures must be thread-safe.
6.  **Update Frequency:** The frequency of price updates for different stocks and exchanges can vary significantly. Some stocks might have updates every millisecond, while others might only have updates every few seconds.
7.  **Handling Late Data:** You may occasionally receive price updates out of order due to network latency.
8.  **N, M Range:** N and M can each range up to 10,000.
9.  **min_profit Range:** 0.01 <= min_profit <= 10.00
10. **max_staleness Range:** 100 <= max_staleness <= 5000

**Example:**

Let's say `min_profit = 0.5` and `max_staleness = 1000`.

Input Stream (example):

```
(1678886400000, 1, 1, 10.0)  // stock_id 1, exchange_id 1, price 10.0 at timestamp 1678886400000
(1678886400100, 1, 2, 10.7)  // stock_id 1, exchange_id 2, price 10.7 at timestamp 1678886400100
(1678886400200, 1, 1, 10.2)
(1678886400300, 1, 3, 9.5)
```

Output:

```
[(1, 1, 2, 10.0, 10.7, 1678886400100)]
```

Explanation:

At timestamp 1678886400100, an arbitrage opportunity exists for stock 1. Buy on exchange 1 at price 10.0 (timestamp 1678886400000) and sell on exchange 2 at price 10.7 (timestamp 1678886400100). The profit (10.7 - 10.0 = 0.7) is greater than `min_profit` (0.5), and the time difference (1678886400100 - 1678886400000 = 100) is less than `max_staleness` (1000). The timestamp of the arbitrage is the later timestamp of the buy and sell, so 1678886400100.  The update to 10.2 on exchange 1 doesn't create an arbitrage opportunity meeting the profit threshold given the current prices. The update to 9.5 on exchange 3 doesn't create an arbitrage opportunity meeting the profit threshold given the current prices.

**Judging Criteria:**

*   **Correctness:** The system must accurately identify all valid arbitrage opportunities and not report any false positives.
*   **Performance:** The system must process the input stream with minimal latency and meet the throughput requirements.
*   **Memory Efficiency:** The system must use memory efficiently and avoid memory leaks.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Concurrency Handling:** The system must correctly handle concurrent updates to the price data.

This problem requires a combination of efficient data structures, algorithmic thinking, and careful attention to detail to handle the real-time and concurrent nature of the input stream. Good luck!
