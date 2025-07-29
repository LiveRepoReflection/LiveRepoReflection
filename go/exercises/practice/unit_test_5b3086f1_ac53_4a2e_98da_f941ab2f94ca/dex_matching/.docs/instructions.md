Okay, challenge accepted. Here's a problem designed to be quite difficult, requiring a good understanding of data structures, algorithms, and optimization.

## Problem: Decentralized Order Book Matching Engine

### Problem Description

You are tasked with building a core component of a decentralized exchange (DEX): an order book matching engine. This engine operates within a blockchain environment where computational resources are limited and gas costs are a significant concern. The engine must efficiently match buy and sell orders submitted by different users, considering price, quantity, and a decentralized timestamp representing the order's submission time to the blockchain.

**Specifics:**

1.  **Orders:** An order is defined as a tuple: `(order_id, user_id, side, price, quantity, timestamp)`.
    *   `order_id`: A unique string identifying the order.
    *   `user_id`: A unique string identifying the user placing the order.
    *   `side`: Either "buy" or "sell".
    *   `price`: An integer representing the price per unit.
    *   `quantity`: An integer representing the number of units to buy or sell.
    *   `timestamp`: An integer representing the block number when the order was submitted (used for priority).

2.  **Order Book:**  Maintain separate sorted order books for buy orders (bids) and sell orders (asks). Bids should be sorted in descending order of price (highest price first), then by ascending order of timestamp (earliest timestamp first). Asks should be sorted in ascending order of price (lowest price first), then by ascending order of timestamp (earliest timestamp first).  This is crucial for fair market principles.

3.  **Matching Logic:** When a new order is received, the engine must attempt to match it against existing orders in the opposite order book.
    *   A buy order can match with a sell order if the buy price is greater than or equal to the sell price.
    *   A sell order can match with a buy order if the sell price is less than or equal to the buy price.
    *   Matching should occur iteratively, starting with the best-priced order in the opposite book.
    *   If a match occurs, execute the trade by transferring the minimum of the buy and sell quantities.
    *   Update the quantities of the matched orders accordingly.
    *   If an order is fully filled (quantity becomes 0), remove it from the order book.
    *   Continue matching until the new order is fully filled or no more matching orders are available.

4.  **Trade Execution:** When a trade occurs, generate a trade record: `(buy_order_id, sell_order_id, price, quantity)`.

5.  **Gas Optimization:** This is critical.  The solution should minimize memory allocation, minimize iterations, and avoid unnecessary computations.  Consider using efficient data structures and algorithms to achieve optimal performance.  Inefficient solutions may fail due to time or memory constraints during evaluation.

6.  **Concurrency:** The matching engine should be designed with concurrency in mind, even though the core matching logic may need to be serialized to maintain order book integrity.  Consider how you might structure the code to allow for parallel order ingestion and processing in a real-world system.  While not directly tested for concurrency in this simplified problem, your design should reflect awareness of these challenges.

**Input:**

A stream of orders represented as tuples, as defined above.

**Output:**

A list of trade records, as defined above, generated during the matching process.

**Constraints:**

*   The number of orders can be very large (up to 10<sup>6</sup>).
*   Prices and quantities are integers within a reasonable range (e.g., 1 to 10<sup>6</sup>).
*   Order IDs and User IDs are unique strings.
*   Timestamp represents block number and is ever increasing.
*   The solution must be efficient in terms of both time and memory.
*   The order book must be correctly maintained according to the sorting rules.
*   The solution must be deterministic.  Given the same input, the output must always be the same.

**Example:**

(This is a simplified example, and your solution must handle a much larger and more complex set of orders)

Input:

```
("order1", "user1", "buy", 100, 10, 1)
("order2", "user2", "sell", 95, 5, 2)
("order3", "user3", "sell", 100, 7, 3)
```

Output:

```
[
  ("order1", "order2", 100, 5),
  ("order1", "order3", 100, 5)
]
```

**Reasoning for Difficulty:**

*   **Data Structure Choice:** The choice of data structures for the order books significantly impacts performance.  A balanced tree (e.g., AVL tree, red-black tree) or a heap-based structure are good candidates, but require careful implementation in Go.  Naive implementations (e.g., using slices and sorting) will likely be too slow for large inputs.
*   **Matching Algorithm:** Optimizing the matching algorithm is crucial.  The iterative matching process must be efficient, and the solution should avoid unnecessary iterations.
*   **Edge Cases:**  Numerous edge cases need to be handled correctly, such as partially filled orders, orders with the same price and timestamp, and empty order books.
*   **Gas Optimization (Memory and Time):** The "gas optimization" requirement forces candidates to think critically about memory allocation and computational complexity.
*   **Concurrency Considerations:**  While not directly tested, the prompt asks candidates to consider concurrency, adding a layer of design complexity.
*   **Sorting and Priority:** The specific sorting requirements on price and timestamp add complexity to the data structure implementation and order book maintenance.

This problem requires a strong understanding of algorithms, data structures, and system design principles, making it a challenging and sophisticated problem suitable for a high-level programming competition. Good luck!
