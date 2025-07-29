## Question: Distributed Transaction Coordinator

### Description

You are tasked with building a simplified distributed transaction coordinator in JavaScript. This coordinator is responsible for ensuring atomicity across multiple independent services. Atomicity, in this context, means that a transaction either commits successfully across all services or rolls back entirely, leaving the system in a consistent state.

Imagine a scenario involving an e-commerce platform where placing an order requires actions across multiple services:

1.  **Inventory Service:** Checks if the requested items are in stock and reserves them.
2.  **Payment Service:** Charges the customer's credit card.
3.  **Shipping Service:** Creates a shipping label and schedules the package for pickup.
4.  **Order Service:** Records the order details.

If any of these steps fail, the entire transaction must be rolled back to maintain data consistency.

Your goal is to implement a `TransactionCoordinator` class that manages these distributed transactions. This class will receive a series of asynchronous actions (functions) to execute in sequence. Each action can potentially succeed or fail. If an action fails, the coordinator must trigger a rollback process, executing a corresponding "compensating action" (undo function) for each successfully completed action.

**Requirements:**

1.  **`TransactionCoordinator` Class:**
    *   `constructor()`: Initializes the coordinator.
    *   `addAction(action, compensate)`: Adds an asynchronous action and its corresponding compensating action to the transaction.  `action` and `compensate` are both functions that return Promises.  `action` represents the operation to be performed, and `compensate` is the function that reverses that operation.
    *   `run()`: Executes all actions in sequence. If all actions succeed, it returns a Promise that resolves to `true`. If any action fails, it triggers the rollback process and returns a Promise that resolves to `false`.
    *   Actions should be executed serially, one after the other. Don't execute them in parallel.

2.  **Asynchronous Actions:** Each `action` provided to `addAction` is an asynchronous function (returns a Promise). The Promise should either resolve (success) or reject (failure).

3.  **Compensating Actions (Rollback):**
    *   If any action fails, the coordinator must execute the `compensate` actions in reverse order of their corresponding `action`s.
    *   Compensating actions must also be asynchronous (return a Promise) and should resolve on success or reject on failure.
    *   If a compensating action fails, log the error message (using `console.error`) and continue the rollback process with the remaining actions.  Do not halt the rollback process due to a compensation failure.  The rollback process needs to try to revert as much as possible.

4.  **Error Handling:**
    *   Each `action` and `compensate` should have proper error handling.  Any rejected promises should be caught to prevent unhandled promise rejections.
    *   Log any errors that occur during the execution of `action` or `compensate` functions.

5.  **Optimization:** The solution should be designed to minimize the time it takes to run the transaction in both successful and rollback scenarios.  Consider the overhead of managing promises and the impact of asynchronous operations.

6.  **Constraints:**

    *   The actions should be executed in the order they are added.
    *   You cannot assume the actions are idempotent (i.e., running them multiple times will have the same effect as running them once). The compensating actions must revert the original actions to bring the system to the correct state.
    *   You are allowed to use standard JavaScript features (ES6+) and built-in modules. Avoid using external libraries.
    *   The system must continue to function gracefully even if compensating actions fail.

7.  **Edge Cases:**

    *   Empty transaction (no actions added).
    *   All actions succeed.
    *   First action fails.
    *   Last action fails.
    *   Multiple actions fail.
    *   Some compensating actions fail.
    *   Actions and compensating actions with varying execution times.

This problem assesses your understanding of asynchronous programming, error handling, distributed systems concepts, and the ability to design and implement a robust transaction management system. The difficulty lies in handling the asynchronous nature of the operations, ensuring proper error handling during both forward execution and rollback, and optimizing for performance.
