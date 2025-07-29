# Transaction Aggregator

This module provides an efficient solution for aggregating financial transactions in real-time. It's designed to handle high-volume transaction streams and provide fast responses to analytical queries.

## Features

- Add transactions to the system in constant time
- Query total transaction amount by category within a time window
- Get top K users by transaction amount for a category within a time window
- Efficient memory management with removal of old transactions
- Caching of query results for improved performance

## Design Choices

### Data Structure Design

1. **Transactions by Category**: The main storage uses sorted lists indexed by category. This allows for efficient binary search operations when querying specific time windows.

2. **User Transactions**: A nested dictionary structure keeps track of transactions by user and category, enabling efficient computation of user spending totals.

3. **Cache System**: A time-limited caching mechanism stores results of previous queries to improve performance for repeated queries.

### Optimizations

- **Binary Search**: All time-based operations use binary search for O(log n) time complexity when locating data in time windows.
- **Selective Caching**: Only historical queries are cached, as real-time data may change frequently.
- **Memory Management**: Old transactions can be pruned to maintain memory efficiency while preserving query accuracy.

## Performance Characteristics

- Add transaction: O(log n) time (due to binary insertion)
- Query total by category: O(log n) for cache miss, O(1) for cache hit
- Query top users: O(m log n + m log m) where m is number of users and n is transactions per user
- Memory usage: O(t) where t is the total number of transactions stored

## Usage
