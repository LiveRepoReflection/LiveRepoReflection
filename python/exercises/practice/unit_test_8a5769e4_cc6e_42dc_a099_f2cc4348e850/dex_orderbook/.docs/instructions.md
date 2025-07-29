## Project Name

`Decentralized-Order-Book`

## Question Description

You are tasked with designing a simplified decentralized order book for a cryptocurrency exchange. This order book operates on a blockchain, and your goal is to implement efficient algorithms for handling limit orders, market orders, and order cancellations while considering the gas costs associated with blockchain operations.

**System Overview:**

The order book maintains two sides: the bid side (buy orders) and the ask side (sell orders). Orders are stored in memory but interactions with the order book (adding, canceling, executing) are assumed to be transactions that incur gas costs.

**Data Structures:**

*   Orders: Each order has the following attributes:
    *   `order_id`: Unique identifier (integer).
    *   `user_id`: User placing the order (integer).
    *   `side`: `Bid` or `Ask`.
    *   `price`: Price per unit of the cryptocurrency (integer).
    *   `quantity`: Number of units to buy or sell (integer).
    *   `timestamp`: The time that the order was created. (integer).
*   Order Book: The order book consists of:
    *   A **sorted** list (or other suitable data structure for maintaining sorted order) of `Bid` orders, sorted in descending order of price (highest bid first).  Orders at the same price are sorted in ascending order of timestamp (oldest first).
    *   A **sorted** list (or other suitable data structure for maintaining sorted order) of `Ask` orders, sorted in ascending order of price (lowest ask first). Orders at the same price are sorted in ascending order of timestamp (oldest first).
*   Pending Orders: This is a `dict` like structure that stores the mapping of `order_id` to the order information (as described in the Order data structure).

**Tasks:**

1.  **Implement `add_limit_order(order)`:**
    *   Adds a new limit order to the order book. A limit order specifies the price and quantity at which the user is willing to buy or sell.
    *   If the order matches existing orders on the opposite side of the book (i.e., the bid price is greater than or equal to the lowest ask price, or the ask price is less than or equal to the highest bid price), execute the trades immediately, up to the available quantity on either side.
    *   Otherwise, add the remaining (unfilled) order to the appropriate side of the order book, maintaining the sorted order.
    *   **Gas Cost Consideration:** Assume each insertion/deletion from the order book costs a fixed amount of gas. Prioritize minimizing the number of insertion and deletion operations, especially when handling partial fills.
    *   **Constraint:** The number of orders in each side of the orderbook cannot exceed 1000. If exceeded, raise an exception.

2.  **Implement `execute_market_order(side, quantity)`:**
    *   Executes a market order for the specified `side` (Bid or Ask) and `quantity`. A market order executes immediately at the best available prices in the order book.
    *   Match the market order against existing limit orders on the opposite side of the book until the market order is fully filled or there are no more matching orders.
    *   **Gas Cost Consideration:** Minimize the number of orders touched to fill the market order. Consider the order in which you match orders to minimize gas consumption.
    *   **Constraint:** If a market order cannot be fully filled due to insufficient liquidity, fill as much as possible and return the remaining quantity.

3.  **Implement `cancel_order(order_id)`:**
    *   Cancels an existing order with the given `order_id`.
    *   Remove the order from the order book.
    *   **Gas Cost Consideration:** Cancellation involves searching for the order and removing it. Optimize the search and removal process.
    *   **Constraint:** If the `order_id` does not exist, raise an exception.

**Requirements:**

*   **Efficiency:** The algorithms should be optimized for speed, especially `add_limit_order` and `execute_market_order`, as they are the most frequent operations. Consider the time complexity of your data structures and algorithms.
*   **Gas Optimization:** Minimize the number of read and write operations to the order book, as these translate to gas costs in a blockchain environment.
*   **Data Structure Choice:** Justify your choice of data structures for the order book sides (e.g., sorted lists, trees, heaps) based on their performance characteristics for insertion, deletion, and searching. Consider both time complexity and constant factors.
*   **Concurrency:** While you don't need to implement actual concurrency, consider how your design would handle concurrent access from multiple users submitting orders simultaneously (e.g., using locks or optimistic concurrency control). Describe the potential concurrency issues and your proposed solutions.
*   **Edge Cases:** Handle edge cases such as:
    *   Empty order book.
    *   Orders with zero quantity.
    *   Market orders with extremely large quantities.
    *   Orders with prices that are very high or very low.
*   **Modularity:** Design your code to be modular and well-structured, making it easy to understand, test, and maintain.
*   **Explainability:** Document your code with clear comments explaining the algorithms and data structures used, and the reasoning behind your design choices.  In particular, clearly explain the gas cost implications of your design and how you optimized for them.

**Bonus Challenges:**

*   **Partial Fills:** Implement more sophisticated logic for partial fills, such as allowing users to specify a minimum fill quantity or a "fill or kill" (FOK) order that is either fully filled immediately or completely canceled.
*   **Order Types:** Support additional order types, such as "immediate or cancel" (IOC) orders that execute immediately and cancel any remaining quantity, or "stop-loss" orders that are triggered when the price reaches a certain level.
*   **Market Making:** Implement a simple market-making strategy that automatically places bid and ask orders to provide liquidity to the order book.

This problem requires a deep understanding of data structures, algorithms, and the constraints of a blockchain environment. Good luck!
