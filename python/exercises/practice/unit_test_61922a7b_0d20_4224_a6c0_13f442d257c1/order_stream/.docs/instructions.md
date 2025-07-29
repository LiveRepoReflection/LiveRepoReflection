## Problem: Scalable Real-Time Order Book Reconstruction

**Problem Description:**

You are tasked with building a system that reconstructs a real-time order book from a stream of market data events. An order book is a list of buy (bid) and sell (ask) orders organized by price level. Your system must efficiently handle a massive volume of incoming order events and maintain an accurate, up-to-date representation of the order book.

**Input:**

Your system will receive a continuous stream of order events. Each event is represented as a tuple with the following structure:

`(timestamp, order_id, side, price, quantity, event_type)`

Where:

*   `timestamp` (int): The time the event occurred, represented as milliseconds since epoch.
*   `order_id` (string): A unique identifier for the order.
*   `side` (string): Either "buy" (bid) or "sell" (ask).
*   `price` (float): The price of the order.
*   `quantity` (int): The quantity of shares in the order.
*   `event_type` (string): The type of event:
    *   "new": A new order is placed on the book.
    *   "cancel": An existing order is canceled (quantity becomes 0).
    *   "execute": An existing order is partially or fully executed. The quantity in the event is the amount executed, which must be subtracted from the existing order’s quantity.

The input stream is not guaranteed to be perfectly ordered by timestamp. There may be some out-of-order events, but the out-of-order window is guaranteed to be relatively small (e.g., no more than 100 milliseconds). The stream can be very large (GBs per hour).

**Output:**

Your system should provide a function `get_order_book(side, depth)` that returns a list representing the top `depth` levels of the order book for the specified `side`.

*   `side` (string): Either "buy" or "sell".
*   `depth` (int): The number of price levels to return.

The returned list should be sorted by price (descending for "buy", ascending for "sell"). Each element in the list should be a tuple: `(price, quantity)`.

**Constraints:**

*   **Scalability:** Your system must handle a high volume of incoming order events (e.g., 100,000+ events per second).
*   **Accuracy:** The order book must accurately reflect the current state based on all processed events.  Events must be processed in chronological order based on timestamp.
*   **Low Latency:** The `get_order_book()` function must return results quickly.  Minimize the time it takes to retrieve the order book.
*   **Memory Efficiency:** The system should use memory efficiently, especially when dealing with a large number of active orders.
*   **Timestamp Handling:**  Account for the possibility of out-of-order events. You need to ensure that events are processed in the correct chronological order.
*   **Edge Cases:** Consider scenarios such as:
    *   Duplicate order IDs (handle gracefully, e.g., ignore the later event).
    *   "cancel" or "execute" events for non-existent order IDs (handle gracefully, e.g., ignore the event).
    *   Zero or negative quantities in "execute" events (handle gracefully, e.g., ignore the event or raise an exception).
    *   Empty order book (return an empty list).
    *   `depth` larger than the number of available price levels.

**Example:**

Assume the following events are processed:

```
events = [
    (1678886400000, "order1", "buy", 100.0, 100, "new"),
    (1678886400001, "order2", "buy", 99.5, 50, "new"),
    (1678886400002, "order3", "sell", 100.5, 75, "new"),
    (1678886400003, "order1", "buy", 100.0, 50, "execute"), # Partially execute order1
    (1678886400004, "order4", "sell", 101.0, 25, "new"),
    (1678886400005, "order2", "buy", 99.5, 50, "cancel")  #cancel order2
]
```

Then:

```
get_order_book("buy", 2)  # Returns [(100.0, 50), (99.5, 0)] (order2 is canceled)
get_order_book("sell", 1) # Returns [(100.5, 75)]
```

**Judging Criteria:**

*   **Correctness:** The order book must accurately reflect the current state based on all processed events.
*   **Performance:** The system should handle a large volume of events with low latency.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Handling of Edge Cases:** The system should gracefully handle all specified edge cases.
*   **Efficiency:** Efficient data structures and algorithms are required to pass, with O(log n) operations for most actions.
