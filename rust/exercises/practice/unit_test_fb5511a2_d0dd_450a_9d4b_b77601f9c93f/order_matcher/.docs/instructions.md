## Problem: Decentralized Order Matching Engine

**Description:**

You are tasked with building a simplified decentralized order matching engine for a cryptocurrency exchange. This engine operates on a blockchain and must be highly efficient, resilient to network partitions, and resistant to manipulation.

Each order is represented as a transaction on the blockchain. The engine maintains the *order book*, a collection of buy and sell orders for a specific asset pair (e.g., BTC/USD).  The goal is to implement a system that efficiently matches compatible buy and sell orders based on price and time priority, and executes trades.

**Constraints and Requirements:**

1.  **Data Structure:** The order book must be maintained in a distributed and fault-tolerant manner. You should use a suitable data structure that allows for efficient insertion, deletion, and retrieval of orders based on price and timestamp. Consider the trade-offs between different data structures (e.g., balanced trees, heaps, distributed hash tables) in terms of performance, consistency, and complexity.

2.  **Matching Algorithm:** Implement a matching algorithm that prioritizes orders based on price and timestamp (First-In, First-Out within each price level). A buy order can be matched with one or more sell orders, and vice-versa, as long as the price condition is met. Your algorithm should minimize latency and maximize throughput.

3.  **Concurrency and Consistency:** The system must handle concurrent order submissions from multiple users across the network. Ensure that the order book remains consistent despite concurrent modifications and potential network partitions. Explore techniques like optimistic concurrency control or distributed consensus algorithms to achieve this.

4.  **Partial Fills:** Implement support for partial fills, where an order can be partially executed if there is insufficient liquidity to fulfill it completely. The remaining portion of the order should remain in the order book.

5.  **Order Cancellation:** Allow users to cancel their orders. The cancellation process should be efficient and ensure that the cancelled order is removed from the order book atomically.

6.  **Malicious Actors:** The system should be designed to be resilient against certain types of attacks. Consider how to mitigate front-running (where someone observes an order and places a similar order ahead of it) and other manipulation attempts.  Perfect prevention is not required, but demonstrate awareness of these issues and propose reasonable defenses.

7.  **Scalability:** The engine should be scalable to handle a large number of orders and users. Consider how your design can be distributed across multiple nodes in the network to increase capacity and fault tolerance.

8.  **Gas Optimization:** In a blockchain environment, transaction fees (gas) are a crucial consideration. Your implementation should strive to minimize the gas cost associated with order submissions, cancellations, and trade executions.

9. **Numerical Stability:** Ensure that calculations involving order prices and quantities are performed with sufficient precision to avoid rounding errors that could lead to unfair trades or loss of funds.

**Input:**

The input consists of a stream of order events, each representing a transaction on the blockchain. Each event contains the following information:

*   `timestamp`:  A monotonically increasing integer representing the time of the event.
*   `order_id`: A unique identifier for the order.
*   `user_id`: A unique identifier for the user submitting the order.
*   `side`:  Either "buy" or "sell".
*   `price`: The price at which the order is placed.
*   `quantity`:  The quantity of the asset to be bought or sold.
*   `action`: Either "new" (for a new order) or "cancel" (to cancel an existing order).

**Output:**

The output consists of a stream of trade events, each representing a successful match between a buy and a sell order. Each event contains the following information:

*   `timestamp`: The timestamp of the trade.
*   `buy_order_id`: The `order_id` of the buy order that was matched.
*   `sell_order_id`: The `order_id` of the sell order that was matched.
*   `price`: The price at which the trade was executed.
*   `quantity`: The quantity of the asset that was traded.

**Example:**

*Input:*

```
{timestamp: 1, order_id: "buy1", user_id: "user1", side: "buy", price: 100, quantity: 10, action: "new"}
{timestamp: 2, order_id: "sell1", user_id: "user2", side: "sell", price: 100, quantity: 5, action: "new"}
{timestamp: 3, order_id: "sell2", user_id: "user3", side: "sell", price: 99, quantity: 5, action: "new"}
{timestamp: 4, order_id: "buy2", user_id: "user4", side: "buy", price: 101, quantity: 10, action: "new"}
```

*Possible Output:*

```
{timestamp: 2, buy_order_id: "buy1", sell_order_id: "sell1", price: 100, quantity: 5}
{timestamp: 3, buy_order_id: "buy2", sell_order_id: "sell2", price: 99, quantity: 5}
{timestamp: 4, buy_order_id: "buy2", sell_order_id: "buy1", price: 100, quantity: 5}  //Partial fill of buy1
```

**Note:**

This problem is intentionally open-ended. There are many possible solutions, each with its own trade-offs. Your task is to design a solution that balances efficiency, robustness, and security, while considering the constraints of a decentralized environment. Focus on clear code, well-reasoned design choices, and a thorough explanation of your approach.  Consider aspects like data structure choices, concurrency strategies, and resilience to network issues.
