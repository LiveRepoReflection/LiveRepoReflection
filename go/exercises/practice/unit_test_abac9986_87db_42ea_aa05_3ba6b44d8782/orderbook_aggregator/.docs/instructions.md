## The Decentralized Order Book Aggregator

**Problem Description:**

You are tasked with building a decentralized order book aggregator. In a decentralized exchange (DEX) environment, order books are often fragmented across multiple independent nodes. Your aggregator needs to efficiently combine these fragmented order books into a single, unified view, allowing traders to make informed decisions.

**Specifics:**

1.  **Data Source:** You will receive order book data from multiple independent nodes (simulated as separate channels in Go). Each node provides a stream of order book updates. An order book update consists of a list of bids (buy orders) and asks (sell orders).

2.  **Order Representation:** An order is represented by its `price` (integer) and `quantity` (integer).

3.  **Update Frequency:** The update frequency from each node can vary significantly. Some nodes might send updates very frequently, while others might be slower.

4.  **Order Book Structure:** The unified order book should maintain separate sorted lists for bids (highest price first) and asks (lowest price first). You must use an efficient data structure to maintain these sorted lists. Consider the trade-offs between insertion/deletion speed and search speed.

5.  **Aggregation Logic:** When a new order book update arrives from a node, you need to merge it into the unified order book.
    *   Orders with the same price should be aggregated (quantities added).
    *   If the quantity of an order becomes zero or negative after merging, the order should be removed.

6.  **Querying the Order Book:** Implement a function that allows querying the top *N* bids and the top *N* asks from the unified order book at any given time.

7.  **Concurrency:** The aggregator must handle concurrent updates from multiple nodes efficiently. You should leverage Go's concurrency features (goroutines and channels) to achieve this.

8.  **Optimization:** The aggregator should be optimized for low latency. The goal is to minimize the time it takes to process updates and respond to queries.

9.  **Fault Tolerance:** Your solution needs to handle situations where one or more nodes become unavailable (stop sending updates). The aggregator should continue to function with the available data. You do not need to detect the faulty nodes, only handle the fact that some channels might be closed.

10. **Constraints:**
    *   The number of nodes providing order book updates can vary (e.g., 1 to 100).
    *   The number of orders in an order book can be large (e.g., up to 10,000 orders per side).
    *   The price and quantity of orders can be large integers (up to `int64`).
    *   The query function must be efficient, even when the order book is very large. Aim for near O(log N) for fetching the top N orders.

11. **Edge Cases:**
    *   Handle empty order book updates.
    *   Handle duplicate orders in the same update.
    *   Handle cases where a node sends an update with orders that should be removed (negative quantities).
    *   Handle situations where the requested number of top bids/asks (*N*) is larger than the number of available orders.

**Input:**

*   A variable number of channels, each representing a stream of order book updates from a node. Each channel sends `[]Order` for bid and ask.
*   The query function receives an integer *N*, representing the number of top bids and asks to retrieve.

**Output:**

*   The query function returns two slices: a slice of the top *N* bids (sorted by price in descending order) and a slice of the top *N* asks (sorted by price in ascending order).

**Judging Criteria:**

Your solution will be judged based on:

*   **Correctness:** Does the aggregator produce the correct unified order book and return the correct top bids/asks?
*   **Efficiency:** How efficiently does the aggregator process updates and respond to queries?
*   **Concurrency:** Does the aggregator handle concurrent updates correctly and efficiently?
*   **Fault Tolerance:** Does the aggregator continue to function correctly when some nodes become unavailable?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?

This problem requires a solid understanding of data structures, algorithms, concurrency, and optimization techniques. Good luck!
