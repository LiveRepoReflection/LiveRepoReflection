Okay, here's a challenging Go programming problem:

## Project Name

```
OptimalOrderPlacement
```

## Question Description

You are building a high-frequency trading system for a cryptocurrency exchange.  The exchange's order book is represented as a stream of events: new orders, cancellations, and trades.  Your task is to design and implement a system that, given a series of these events, can efficiently determine the *optimal* price and quantity to place a market order to buy a specific cryptocurrency, subject to the following constraints:

**Input:**

*   A stream of order book events (as described below).
*   A target quantity `Q` of the cryptocurrency to acquire.
*   A maximum acceptable slippage `S` (as a percentage). Slippage is defined as `(Execution Price - Best Bid Price) / Best Bid Price`, where Execution Price is the volume-weighted average price you actually pay to acquire the target quantity.
*   A maximum order size limit `L`.  This is the largest single order the system can place. This is to simulate exchange limitations.
*   A commission rate `C` (as a percentage) charged on the total execution price.

**Order Book Events:**

Each event is represented as a string with the following possible formats:

*   `NEW,side,price,quantity`  - A new order is placed. `side` is either `BID` (buy) or `ASK` (sell). `price` and `quantity` are positive integers.
*   `CANCEL,side,price,quantity` - An order is cancelled.  `side`, `price`, and `quantity` are as above.  The cancelled order is guaranteed to have existed in the order book.
*   `TRADE,side,price,quantity` - A trade occurred. `side`, `price`, and `quantity` are as above. This means orders from the order book have been executed and removed.

**Output:**

Your program should output two numbers representing the optimal market order placement:

*   The optimal price `P` to place the market order such that the slippage is minimized while achieving the target quantity `Q` or as close to it as possible. If there is no order on the ask side, the price should be -1.
*   The expected execution quantity `Qe` which is the quantity that can be acquired at the optimal price `P`.

**Constraints and Considerations:**

*   **Real-time Performance:** The system must process events and determine the optimal order placement *very* quickly (think sub-millisecond average latency).  This means you need to optimize your data structures and algorithms.
*   **Event-Driven Architecture:**  The system should be designed to handle a continuous stream of events, not just a single batch.
*   **Order Book Depth:** The order book can have a significant depth (many levels of bids and asks).  Your solution should scale well with the number of orders.
*   **Partial Fulfillment:**  If the order book does not contain enough liquidity to fulfill the target quantity `Q` while staying within the slippage tolerance `S`, your system should acquire as much as possible within the slippage constraint.
*   **Edge Cases:**
    *   Empty order book.
    *   Target quantity `Q` is zero.
    *   Slippage `S` is zero.
    *   Order book contains only bids or only asks.
    *   `L` is smaller than the smallest order in the order book.
*   **Optimal Price Determination:** The "optimal" price is defined as the *lowest* price at which you can reasonably acquire the requested quantity while minimizing slippage.  You might not need to consume the entire order book.
*   **Handling Invalid Input:**  Gracefully handle invalid event formats.
*   **Commission:** The commission `C` affects the slippage calculation. Slippage = `((Execution Price * (1 + C)) - Best Bid Price) / Best Bid Price`

**Example:**

Let's say the current order book contains the following asks:

*   ASK, 100, 5
*   ASK, 101, 10
*   ASK, 102, 15

And the best bid is 99.

If `Q = 10`, `S = 0.02` (2%), `L = 1000`, and `C = 0` (0%), the system should determine:

1.  Buying 5 units at price 100
2.  Buying 5 units at price 101

The execution price would be: `(5 * 100 + 5 * 101) / 10 = 100.5`
The slippage would be: `(100.5 - 99) / 99 = 0.01515` (1.515%) which is less than 2%

The output should be:

`101 10`
(This is the highest price reached.)

If `Q = 30` and `S = 0.02`, the system needs to also consider `ASK, 102, 15`.
The execution price would be: `(5 * 100 + 10 * 101 + 15 * 102) / 30 = 101.333`
The slippage would be: `(101.333 - 99) / 99 = 0.02356` (2.356%) which is greater than 2%

In this case, the output should still be `101 15`. This is because even if the target quantity cannot be achieved, the maximum ask price before the slippage exceeds 2% is 101 and the total number of acquired units at the best price is 15.

**Evaluation Criteria:**

*   **Correctness:**  Does the system produce the correct optimal price and quantity, satisfying the constraints?
*   **Performance:**  How quickly does the system process events and determine the optimal order placement?
*   **Scalability:**  How well does the system scale with the number of orders in the order book?
*   **Code Quality:**  Is the code well-structured, readable, and maintainable?
*   **Edge Case Handling:** Does the system handle various edge cases gracefully?

This problem requires a solid understanding of data structures (particularly order book representation), algorithms (for efficiently searching and calculating slippage), and system design (for handling a continuous stream of events). Good luck!
