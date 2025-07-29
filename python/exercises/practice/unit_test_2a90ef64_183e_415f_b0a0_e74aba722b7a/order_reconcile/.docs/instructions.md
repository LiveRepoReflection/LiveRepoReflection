Okay, here's your challenging programming competition problem:

## Problem: Decentralized Order Book Reconciliation

**Description:**

You are building a core component for a new decentralized exchange (DEX). A key part of any exchange is the order book, which contains all the active buy and sell orders. In a decentralized environment, order books are often replicated and maintained by multiple independent nodes. This introduces the challenge of ensuring consistency across these distributed order books.

Your task is to implement a system that reconciles potentially inconsistent order books from multiple nodes, identifying discrepancies and producing a merged, consistent view of the order book.

**Input:**

The input will consist of a list of order books, each representing the state of the order book on a different node. Each order book is represented as a dictionary (or equivalent data structure in your chosen language) containing two lists: `bids` (buy orders) and `asks` (sell orders).

Each order (bid or ask) is represented as a tuple: `(price, quantity, order_id)`.

*   `price`: A positive floating-point number representing the price of the order.
*   `quantity`: A positive integer representing the quantity of the asset being bought or sold.
*   `order_id`: A unique string identifying the order. This is a UUID.

Example input:

```python
[
    {
        "bids": [(100.0, 5, "order1"), (99.5, 3, "order2")],
        "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
    },
    {
        "bids": [(100.0, 5, "order1"), (99.0, 2, "order5")],
        "asks": [(101.0, 2, "order3"), (102.0, 1, "order6")]
    },
    {
        "bids": [(100.0, 5, "order1")],
        "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
    }
]
```

**Output:**

Your system should produce a single, reconciled order book, also represented as a dictionary with `bids` and `asks` lists. The reconciled order book should:

1.  **Include all unique orders** present in any of the input order books.
2.  **Resolve quantity discrepancies** by taking the *largest* quantity for a given `order_id` across all order books.  If an `order_id` only appears in one order book, use that quantity.
3.  **Prioritize orders based on price** Bids should be sorted in descending order by price (highest bid first). Asks should be sorted in ascending order by price (lowest ask first).
4.  **Break ties in price** by using the `order_id`.  Smaller `order_id` strings should come earlier in the ordering. This is standard string comparison.

Example output (for the example input above):

```python
{
    "bids": [(100.0, 5, "order1"), (99.5, 3, "order2"), (99.0, 2, "order5")],
    "asks": [(101.0, 2, "order3"), (101.5, 4, "order4"), (102.0, 1, "order6")]
}
```

**Constraints:**

*   The number of input order books can range from 1 to 100.
*   Each order book can contain up to 10,000 orders.
*   Prices are positive floating-point numbers.
*   Quantities are positive integers.
*   `order_id` strings are unique across *all* order books.
*   The solution must be efficient in terms of both time and space complexity. Naive solutions that iterate through all order books for every order will likely time out.
*   Consider that in a real system, nodes could have delays in processing, so the reconcilation process is called periodically to ensure order book consistency.
* The code must be robust and handle potential edge cases.

**Bonus Challenges:**

1.  **Fault Tolerance:**  Simulate a scenario where some order books are corrupted (e.g., missing data, invalid formats). Your system should gracefully handle these errors and produce the best possible reconciled order book from the valid data.
2.  **Real-Time Updates:** Consider how you would adapt your system to handle a stream of updates (new orders, cancellations, modifications) to the order books in real-time.

This problem tests your ability to work with complex data structures, implement efficient algorithms, handle edge cases, and reason about the challenges of distributed systems. Good luck!
