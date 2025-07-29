Okay, here's a problem designed to be challenging and complex, suitable for a high-level programming competition using Go.

## Problem: Decentralized Order Book Aggregation

**Problem Description:**

You are tasked with building a decentralized order book aggregator. Multiple independent exchanges ("shards") each maintain their own order books for a specific trading pair (e.g., BTC/USD). Your system needs to efficiently aggregate these fragmented order books to provide a global, unified view to traders.

Each shard exposes an API endpoint that returns a snapshot of its order book. The order book is represented as a list of *limit orders*, each with a price, quantity, and a timestamp indicating when the order was placed.  Your system must periodically poll these endpoints, merge the received data, and present a combined order book.

However, there are several challenges:

1.  **Network Latency and Unreliability:** Network conditions between your system and the shards are variable. Some shards might be slow to respond, temporarily unavailable, or return inconsistent data.  You must handle these situations gracefully, avoiding single points of failure.
2.  **Data Consistency:** Due to network delays and asynchronous updates, shards may have slightly different versions of the order book at any given time.  Your aggregation logic must minimize inconsistencies and present the most accurate view possible, even if it's not perfectly synchronized across all shards.
3.  **Scalability:** The number of shards and the frequency of updates can be high. Your system needs to be designed to handle a large volume of data and requests.  Consider concurrency and efficient data structures.
4.  **Priority and Weighting:** Not all shards are created equal. Some shards might be more reliable or have higher trading volume. Your system must allow administrators to assign weights to each shard, influencing its contribution to the aggregated order book. Higher weight shards should have a greater impact on the final aggregated book.
5.  **Order Book Depth:** The aggregated order book should have a configurable depth.  The system should only display the top *N* bids and *N* asks (where *N* is a parameter provided at runtime), prioritizing orders with the best prices.
6. **Stale Data Handling:** Order data from some shards might be significantly delayed and effectively "stale". You must implement a mechanism to detect and discard stale order data based on a configurable maximum age (e.g., ignore orders older than 5 seconds).
7. **Real-time Updates:** The aggregated order book must be updated continuously, reflecting the latest data from the shards. Traders should be able to subscribe to these updates and receive them with minimal latency.

**Input:**

*   A configuration file specifying the API endpoints for each shard, along with its assigned weight.  The weight is a floating-point number (e.g., 1.0, 0.5, 2.0).
*   A maximum order book depth (*N*) - an integer representing the number of bids and asks to display.
*   A maximum data staleness duration (in seconds) - a float representing how long order data can be considered valid after its timestamp.

**Output:**

*   A continuously updated, aggregated order book, consisting of the top *N* bids and top *N* asks.  The output should be sorted by price (highest bid first, lowest ask first) and timestamp (oldest orders first within each price level).
*   The system should also expose metrics (e.g., number of updates received, average latency per shard) for monitoring purposes.

**Constraints:**

*   The number of shards can be up to 100.
*   The depth (*N*) can be up to 50.
*   The staleness duration can range from 1 to 10 seconds.
*   The system should be resilient to network failures and data inconsistencies.
*   The system should be scalable and efficient, capable of handling a high volume of updates.

**Judging Criteria:**

*   Correctness: The aggregated order book should accurately reflect the data from the shards, considering weights, depth, and staleness.
*   Efficiency: The system should be able to handle a large volume of updates with minimal latency.
*   Robustness: The system should be resilient to network failures and data inconsistencies.
*   Scalability: The system should be designed to handle a large number of shards.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Real-time Update Speed: Updates to the aggregated order book should be reflected rapidly.

This problem combines elements of distributed systems, data aggregation, and real-time data processing, making it a challenging and realistic programming competition task. Good luck!
