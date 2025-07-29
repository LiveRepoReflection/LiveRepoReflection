## Problem: Scalable Transaction Aggregation

You are tasked with designing and implementing a system for efficiently aggregating financial transactions.  Imagine a high-volume e-commerce platform that processes millions of transactions daily.  These transactions need to be categorized and aggregated in real-time to generate reports for various business units.

**Input:** A continuous stream of transaction records. Each record is a dictionary (or a similar data structure) containing the following keys:

*   `transaction_id`: A unique string identifier for the transaction.
*   `timestamp`: An integer representing the Unix timestamp of the transaction.
*   `amount`: A float representing the transaction amount.
*   `category`: A string representing the category of the transaction (e.g., "Electronics", "Books", "Clothing").
*   `user_id`: An integer representing the ID of the user who made the transaction.

**Output:**  A system that can efficiently provide the following aggregated information on demand:

1.  **Total transaction amount per category for a given time window:** Given a category and a start and end timestamp, return the sum of all transaction amounts for that category within the specified time window.

2.  **Top K users by transaction amount for a given time window and category:** Given a category, a start and end timestamp, and an integer K, return a list of the top K users who spent the most within that category and time window, along with their total spending.  The list should be sorted in descending order of spending.

**Constraints:**

*   **Scalability:** The system should be able to handle a very large volume of incoming transactions and provide query results with low latency.  Assume the transaction stream is unbounded.
*   **Real-time aggregation:** Queries should return results based on the most up-to-date data available.  Strive for minimal delay between transaction arrival and query availability.
*   **Memory Efficiency:**  The system should be designed to minimize memory usage.  Storing all transactions in memory is not feasible.
*   **Time Window Queries:** The system must efficiently handle queries with arbitrary time windows.
*   **Category Diversity:** The number of transaction categories is large and potentially growing.
*   **K Value:**  The value of K in the "Top K users" query can vary.
*   **Timestamp Range:** The timestamp can be very large.

**Requirements:**

*   Design and implement the core data structures and algorithms for efficient transaction aggregation.
*   Consider the trade-offs between different data structures and algorithms in terms of memory usage, query performance, and update complexity.
*   Provide a clear explanation of your design choices and the reasoning behind them.
*   Pay special attention to algorithmic complexity and strive for optimal performance.

**Bonus (Optional, but highly recommended for a truly challenging solution):**

*   Implement a mechanism for persisting aggregated data to disk for recovery in case of system failures.
*   Design a system that can handle out-of-order transaction arrivals (transactions arriving with timestamps that are earlier than the latest timestamp already processed). How would you handle late arriving data?
*   Explore the use of distributed data structures or databases for even greater scalability.
