Okay, here's a challenging Rust coding problem designed to push the boundaries of algorithmic efficiency and data structure mastery.

**Problem Title: Decentralized Order Matching Engine**

**Problem Description:**

You are tasked with building a core component of a decentralized exchange (DEX): an efficient order matching engine. This engine operates within a blockchain environment with limited computational resources and high transaction costs. It needs to handle a continuous stream of buy and sell orders for a specific asset pair (e.g., BTC/USDT) and match them according to price and time priority.

**Constraints:**

*   **Decentralized Nature:** Assume the matching logic executes within a smart contract. This implies:
    *   **Gas Limit:**  The execution of each matching round (processing a batch of orders) must stay within a tight gas limit. Exceeding this limit will revert the transaction, rendering the orders unprocessed.
    *   **Limited Storage:** Smart contract storage is expensive. Minimize the amount of data stored on-chain.
    *   **Deterministic Execution:** The matching algorithm must be deterministic, ensuring all nodes on the blockchain arrive at the same result given the same input.
*   **Order Structure:** Orders have the following attributes:
    *   `order_id`: A unique identifier for the order (u64).
    *   `timestamp`: The time the order was submitted (u64, representing milliseconds since epoch).
    *   `order_type`:  Either "buy" or "sell" (enum).
    *   `price`: The price at which the order is willing to buy or sell (u64, representing the price * 10^8).
    *   `quantity`: The amount of the asset to buy or sell (u64, representing the quantity * 10^8).
*   **Matching Logic:**
    1.  **Price Priority:** Buy orders are matched with the highest available sell orders, and sell orders are matched with the lowest available buy orders.
    2.  **Time Priority (Within Price):** If multiple orders have the same price, the order with the earliest timestamp is matched first.
    3.  **Partial Fills:** Orders can be partially filled.  If a buy order of quantity `X` matches a sell order of quantity `Y` where `X > Y`, the sell order is completely filled, and the buy order is updated with the remaining quantity `X - Y`.
    4.  **Order Cancellation:** Orders can be cancelled.  A cancellation request contains only the `order_id`. Cancelled orders should not be considered for matching.
*   **Efficiency:** The engine needs to handle a large volume of orders (up to 100,000) within a reasonable timeframe and gas limit.
*   **Data Structures:** You are free to choose your data structures for storing orders. However, you must justify your choice in terms of gas efficiency and storage optimization. You cannot use external libraries.
*   **Input:** A vector of `Order` and `Cancellation` structs.
*   **Output:** A vector of `Trade` structs. A `Trade` represents a successful match between a buy and sell order. It contains:
    *   `buy_order_id`: The `order_id` of the buy order.
    *   `sell_order_id`: The `order_id` of the sell order.
    *   `price`: The price at which the trade occurred.
    *   `quantity`: The quantity traded.
*   **Gas Limit Awareness:** You must provide benchmarks showing the gas consumption of your solution with varying numbers of orders.

**Specific Requirements:**

1.  Implement the order matching engine in Rust.
2.  Optimize for gas efficiency, considering the limitations of a smart contract environment.
3.  Minimize on-chain storage.
4.  Handle order cancellations correctly.
5.  Include thorough unit tests covering various scenarios, including edge cases.
6.  Provide benchmarks demonstrating the gas consumption of your solution.
7.  Include a well-documented explanation of your design choices, including the data structures used and why they were selected. Explain the time and space complexity of your matching algorithm.

**Grading Criteria:**

*   **Correctness:** The engine must correctly match orders according to the specified logic.
*   **Efficiency:** The solution with the lowest gas consumption for a given number of orders will be considered more efficient.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.
*   **Testing:** The unit tests must cover a wide range of scenarios and edge cases.
*   **Documentation:** The design explanation must be clear, concise, and well-justified.

Good luck! This will require careful consideration of data structures and algorithms to optimize for the constrained environment.
