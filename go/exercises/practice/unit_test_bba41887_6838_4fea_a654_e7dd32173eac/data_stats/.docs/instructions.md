Okay, here's a problem designed to be challenging and require careful consideration of efficiency and edge cases in Go.

**Project Name:** `optimizing-data-streams`

**Question Description:**

You are building a real-time data processing pipeline for a high-volume sensor network.  Sensors continuously transmit data packets, each containing a timestamp (Unix epoch in milliseconds), a sensor ID (string), and a data value (integer). The data arrives in a chaotic, out-of-order fashion due to network latency and varying sensor transmission rates.

Your task is to design and implement a system that efficiently calculates and provides real-time, sliding-window statistics for each sensor.  Specifically, for each sensor, you need to maintain:

1.  **Windowed Average:** The average data value for the sensor within a specified time window.
2.  **Windowed Standard Deviation:** The standard deviation of the data values for the sensor within the same time window.

The system must support the following operations:

*   **`Ingest(timestamp int64, sensorID string, value int)`:**  Ingests a new data packet into the system. This function *must* be highly optimized for speed as it will be called millions of times per second.

*   **`GetStatistics(sensorID string) (average float64, stdDev float64, found bool)`:**  Retrieves the windowed average and standard deviation for the specified sensor. Returns `found = true` if the sensor has data within the window, otherwise returns `found = false` and arbitrary values for average and stdDev.

**Constraints & Requirements:**

*   **Time Window:** The time window is a fixed duration, `W`, specified at system initialization.  Only data packets with timestamps within `[current_time - W, current_time]` should be considered in the calculations. `current_time` here refers to the latest ingested timestamp.
*   **Out-of-Order Data:** The data is received out of order. Your system must handle this correctly.
*   **High Throughput:** The `Ingest` function must be able to handle a very high volume of data packets with minimal latency.
*   **Memory Efficiency:** Minimize memory usage, especially when dealing with a large number of sensors.  Avoid storing the entire data stream in memory if possible.
*   **Concurrency:** The system must be thread-safe, allowing concurrent calls to `Ingest` and `GetStatistics` from multiple goroutines.
*   **Zero Values:** The system must correctly handle data values that may be zero, negative, or very large. Be mindful of potential integer overflows during calculations.
*   **Edge Cases:** Consider edge cases such as:
    *   No data for a sensor.
    *   Not enough data points within the window to calculate standard deviation (at least two data points are required).  In this case, return stdDev as 0.0 and found = true.
    *   A large number of sensors with sparse data.
*   **Optimization:**  Focus on optimizing the `Ingest` function, as this is the most performance-critical part of the system.  Consider using appropriate data structures and algorithms to achieve the best possible performance.  Pre-calculation and caching strategies may be helpful.
*   **Testability:** Your solution should be easily testable.

**Initial Setup:**
Provide a struct for the data processing system with the following:

```go
type DataStreamProcessor struct {
    // TODO: Add your data structures and synchronization primitives here
}

// NewDataStreamProcessor creates a new DataStreamProcessor with the given time window in milliseconds.
func NewDataStreamProcessor(windowSizeMs int64) *DataStreamProcessor {
    // TODO: Initialize your DataStreamProcessor here
}

// Ingest ingests a new data packet into the system.
func (dsp *DataStreamProcessor) Ingest(timestamp int64, sensorID string, value int) {
    // TODO: Implement the data ingestion logic here
}

// GetStatistics retrieves the windowed average and standard deviation for the specified sensor.
func (dsp *DataStreamProcessor) GetStatistics(sensorID string) (average float64, stdDev float64, found bool) {
    // TODO: Implement the statistics calculation logic here
}
```

This problem requires a good understanding of data structures, algorithms, concurrency, and performance optimization in Go. Good luck!
