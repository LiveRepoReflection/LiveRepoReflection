## Project Name

`NetworkAnomalyDetection`

## Question Description

You are a security analyst tasked with detecting anomalies in network traffic data. You are given a stream of network connection records, each represented by a tuple of the form:

`(timestamp, source_ip, destination_ip, source_port, destination_port, protocol, packet_size)`.

Your goal is to implement a system that can identify potentially malicious or unusual network connections in real-time. Define "unusual" as connections that deviate significantly from established patterns based on the provided historical data.

**Specific Requirements:**

1.  **Data Ingestion:** Implement a data structure and function to efficiently ingest the stream of network connection records. The data structure should allow for fast lookups based on any of the connection record fields.

2.  **Baseline Establishment:** Based on an initial window of `N` records, establish a baseline of "normal" network behavior.  Consider establishing baselines for combinations of fields, such as (source\_ip, destination\_ip, protocol) or (source\_port, destination\_port).  You should use statistical methods to determine these baselines.
    *   Specifically, for each combination of fields you choose to baseline, calculate the mean and standard deviation of the packet sizes observed.

3.  **Anomaly Detection:** After establishing the baseline, for each subsequent record, determine whether it is anomalous. A record is considered anomalous if its `packet_size` deviates by more than `K` standard deviations from the established mean for its corresponding baseline field combinations. Handle the case where the combination of fields for a new record has not been seen before (cold start).

4.  **Adaptive Learning:** The baseline should adapt over time. Implement a mechanism to update the baseline statistics (mean and standard deviation) using a sliding window approach. As new records are processed, the oldest records in the initial window should be removed, and the new records added to the window. This ensures the baseline reflects the most recent network behavior.

5.  **Optimization:** The solution must be highly efficient in terms of both time and memory complexity. The anomaly detection process should be fast enough to handle a high volume of network traffic in real-time.

6.  **Edge Cases and Constraints:**
    *   Handle potential division by zero errors when calculating standard deviation (e.g., when there is only one sample in the window, or all samples have the same value).
    *   Account for potential integer overflows when summing packet sizes.
    *   Consider the memory usage of your data structures, especially when dealing with large datasets.
    *   Handle the cold start problem when a novel field combination is encountered.

7.  **Multiple Valid Approaches:** There are several valid approaches to this problem. For instance, the choice of which fields to use for baseline establishment and the specific statistical methods used can vary.  Solutions will be evaluated based on their accuracy, efficiency, and clarity.

**Input:**

*   A stream of network connection records, where each record is a tuple: `(timestamp: u64, source_ip: String, destination_ip: String, source_port: u16, destination_port: u16, protocol: String, packet_size: u32)`.
*   The baseline window size `N: usize`.
*   The standard deviation threshold `K: f64`.

**Output:**

*   A vector of booleans, where each boolean corresponds to a record in the input stream (after the initial `N` records used for baseline establishment). The boolean should be `true` if the record is considered anomalous, and `false` otherwise.

**Example:**

Imagine `N=5`, `K=2.0`. Your system ingests the first 5 records to establish a baseline. Then, for the 6th record, it checks if its `packet_size` is more than 2 standard deviations away from the mean for its corresponding baselined field combination. If it is, the 6th element in the output vector will be `true`; otherwise, it will be `false`. This process continues for the rest of the input stream.

**Scoring:**

Solutions will be evaluated based on the following criteria:

*   **Correctness:** The solution accurately identifies anomalous network connections.
*   **Efficiency:** The solution processes network traffic in real-time with minimal latency.
*   **Memory Usage:** The solution efficiently uses memory, especially when dealing with large datasets.
*   **Code Quality:** The solution is well-structured, readable, and maintainable.
*   **Robustness:** The solution handles edge cases and potential errors gracefully.
*   **Adaptability:** How well does the solution adapt to changes in network traffic patterns over time?
