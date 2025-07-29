Okay, here's a Rust coding problem designed to be challenging, incorporating several of the elements you suggested:

## Problem: Distributed Transaction Orchestrator

**Description:**

You are tasked with building a simplified distributed transaction orchestrator. In a distributed system, a single logical transaction might involve operations across multiple independent services. To ensure data consistency, we need a mechanism to coordinate these operations, ensuring either all succeed or all fail (atomicity).

This problem focuses on the "happy path" and rollback scenarios. We'll simulate services and their operations and require you to implement the core orchestration logic.

**Scenario:**

Imagine an e-commerce system where placing an order involves:

1.  **Reserving Inventory:**  Decrementing the stock count in the Inventory Service.
2.  **Charging Payment:**  Processing the payment through the Payment Service.
3.  **Creating Order:**  Creating a new order record in the Order Service.

Each service exposes a simplified API:

*   `InventoryService::reserve(item_id: u32, quantity: u32) -> Result<(), String>`
*   `PaymentService::charge(user_id: u32, amount: u32) -> Result<(), String>`
*   `OrderService::create_order(user_id: u32, items: Vec<(u32, u32)>) -> Result<u32, String>` (Returns the new order ID on success.)
*   Each service has its own `rollback()` function with parameters match to its main function.

These methods return `Result<(), String>`, indicating success or an error message on failure.  The `OrderService::create_order` returns `Result<u32, String>`.

**Your Task:**

Implement a `TransactionOrchestrator` in Rust with the following functionality:

1.  **`execute_transaction(user_id: u32, items: Vec<(u32, u32)>, amount: u32)`:** This method orchestrates the distributed transaction.
    *   It takes a user ID, a list of items with quantities (item ID, quantity), and the total amount to charge.
    *   It calls the services in the following order: Inventory Service, Payment Service, Order Service.
    *   If all calls succeed, it returns `Ok(order_id)` with the ID of the created order.
    *   If any call fails, it **must** trigger a rollback of all previously successful operations in **reverse order**.  The orchestrator needs to keep track of which operations succeeded and their necessary rollback data.
    *   If a rollback operation fails, log the error (using `println!` for simplicity) and continue with the remaining rollbacks.  Do **not** stop the rollback process. The system should attempt to revert all changes even if some rollbacks fail.
    *   If any part of the main transaction or rollback fails, return `Err(error_message)` with a descriptive error message.

2.  **Service Simulation:**
    *   You are provided with dummy implementations of `InventoryService`, `PaymentService`, and `OrderService`. These services have a configurable probability of failure (e.g., 20% chance to return an error).  This simulates real-world service unreliability.
    *   The services also track the number of reserve, charge, and create_order calls made.

**Constraints and Considerations:**

*   **Error Handling:**  Robust error handling is crucial. Ensure that error messages are informative and that the rollback process is as resilient as possible.  Handle potential panics gracefully.
*   **Rollback Order:**  Rollback operations **must** be performed in the reverse order of the original operations.
*   **Idempotency (Bonus):** Consider the implications of idempotency.  If a rollback fails and is retried, can it cause issues? (This doesn't need to be solved, but it's something to consider).
*   **Concurrency (Out of Scope):**  For simplicity, assume single-threaded execution.  In a real system, you would need to handle concurrency issues.
*   **Optimizations (Not Required):** You don't need to focus on performance optimizations for this problem, but be mindful of the complexity of your solution.

**Example:**

```
let mut orchestrator = TransactionOrchestrator::new(
    InventoryService::new(0.2), // 20% failure rate
    PaymentService::new(0.2),   // 20% failure rate
    OrderService::new(0.2),     // 20% failure rate
);

let result = orchestrator.execute_transaction(123, vec![(1, 2), (3, 1)], 100);

match result {
    Ok(order_id) => println!("Transaction successful! Order ID: {}", order_id),
    Err(err) => println!("Transaction failed: {}", err),
}
```

**Grading Criteria:**

*   Correctness:  Does the orchestrator correctly execute transactions when all services succeed?  Does it correctly rollback when a service fails?
*   Error Handling:  Does the orchestrator handle errors gracefully and provide informative error messages?  Does it continue the rollback process even if some rollbacks fail?
*   Code Structure:  Is the code well-structured, readable, and maintainable?
*   Adherence to Constraints: Does the solution respect the constraints outlined in the problem description?

This problem challenges the solver to think about distributed systems, error handling, and transaction management. The probabilistic failure of the simulated services adds an element of realism and forces the solver to consider edge cases and resilience. Good luck!
