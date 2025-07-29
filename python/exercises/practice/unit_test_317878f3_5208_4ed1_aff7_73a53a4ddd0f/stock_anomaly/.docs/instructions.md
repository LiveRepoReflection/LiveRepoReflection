Okay, here's a challenging Python coding problem designed to test advanced skills, efficiency, and attention to detail.

**Problem Title:** Scalable Real-Time Anomaly Detection in High-Frequency Stock Data

**Problem Description:**

You are working for a high-frequency trading firm. Your task is to design and implement a real-time anomaly detection system for stock price data. The system should be able to process a continuous stream of stock price updates (ticks) and identify anomalous price movements within a defined time window.

Each tick contains the following information:
*   `timestamp` (nanoseconds since epoch, integer)
*   `stock_id` (string representing the stock ticker symbol, e.g., "GOOG", "AAPL")
*   `price` (floating-point number)
*   `volume` (integer representing the number of shares traded)

An anomaly is defined as a significant deviation from the expected price behavior within a specified time window. You will use a dynamic z-score based approach to identify anomalies.

**Requirements:**

1.  **Real-time Processing:** The system must be able to process incoming ticks in real-time with minimal latency. Assume a high volume of ticks (millions per second) across many different `stock_id` values.

2.  **Dynamic Z-score Calculation:** For each `stock_id`, maintain a sliding time window of the last `W` seconds of price data. Within this window, calculate the mean (`μ`) and standard deviation (`σ`) of the prices. A tick is considered anomalous if its price deviates from the mean by more than `Z` standard deviations (i.e., `|price - μ| > Z * σ`). The mean and standard deviation should be efficiently updated with each new tick, without recomputing on the entire window.

3.  **Scalability:** The system needs to handle a large number of different `stock_id` values concurrently. You must design your solution to scale efficiently as the number of monitored stocks increases.

4.  **Time Window Management:** Implement a mechanism to efficiently manage the sliding time window. Expired ticks (ticks older than `W` seconds) must be removed from the window as new ticks arrive.

5.  **Anomaly Reporting:** When an anomaly is detected, the system should report it, including the `timestamp`, `stock_id`, `price`, `volume`, `μ`, `σ`, and z-score of the anomalous tick.

6.  **Memory Efficiency:** Minimize memory usage. Storing all ticks for all stocks in memory is not feasible. Use data structures and algorithms that allow for efficient memory utilization.

7. **Persistence:** Implement a mechanism to persist anomalies detected in a log file.

**Constraints:**

*   `W` (Window Size): 60 seconds (fixed)
*   `Z` (Z-score Threshold): 3.0 (fixed)
*   You must use Python for your solution.
*   You are allowed to use standard Python libraries (e.g., `collections`, `datetime`, `math`). However, the use of external libraries such as `NumPy` or `Pandas` is permitted only if it significantly improves performance and memory efficiency, and you must justify their use.
*   Your solution should be thread-safe (consider concurrent access to per-stock data).

**Input:**

The input is a continuous stream of ticks. You can simulate this stream using a generator function that yields tick dictionaries.

**Output:**

The system should output anomaly reports to standard output and persist these anomalies to a log file. The format of the anomaly report should be:

```
Anomaly: timestamp=<timestamp>, stock_id=<stock_id>, price=<price>, volume=<volume>, mu=<mu>, sigma=<sigma>, z_score=<z_score>
```

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The accuracy of anomaly detection.
*   **Performance:** The throughput of the system (ticks processed per second) and the latency of anomaly detection.
*   **Scalability:** The ability to handle a large number of `stock_id` values.
*   **Memory Efficiency:** The memory footprint of the system.
*   **Code Quality:** The clarity, readability, and maintainability of your code.
*   **Concurrency:** Thread safety and proper handling of concurrent access.

This problem requires a strong understanding of data structures, algorithms, concurrency, and real-time processing. Good luck!
