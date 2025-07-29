## Question: Distributed Transaction Orchestrator

### Question Description

You are tasked with building a simplified distributed transaction orchestrator. In a microservices architecture, ensuring data consistency across multiple services during a transaction is crucial. This problem focuses on orchestrating transactions across several "resource managers" (simulated as functions).

Your solution should implement a `TransactionOrchestrator` class that manages a series of operations across these resource managers. Each operation can either succeed or fail. If any operation fails, the orchestrator must roll back all previously successful operations to maintain consistency.

The `TransactionOrchestrator` should accept a series of operations at initialization. Each operation will be an object with the following structure:

```javascript
{
  resourceManagerId: string, // Unique identifier for the resource manager.
  forward: async (data: any) => Promise<boolean>, // Asynchronous function to perform the action. Returns true on success, false on failure.
  rollback: async (data: any) => Promise<boolean>, // Asynchronous function to undo the action. Returns true on success, false on failure.
  data: any // Data needed for forward and rollback operations.  This will be shared between forward and rollback.
}
```

The `TransactionOrchestrator` class should have a `run()` method that executes these operations sequentially.  If an operation fails during the forward execution, the `run()` method should then execute the `rollback` functions of all previously successful operations in reverse order.

**Constraints and Considerations:**

*   **Asynchronous Operations:** The `forward` and `rollback` functions are asynchronous, simulating network latency and other real-world delays.
*   **Idempotency:** Resource managers may receive the same rollback request multiple times (due to network issues or orchestrator retries). Your rollback functions must be idempotent – they should only perform the rollback action once, even if called multiple times. Implement a mechanism to track which rollbacks have already been executed.
*   **Concurrency:** While the forward operations are executed sequentially, rollbacks should be performed concurrently to minimize rollback time.
*   **Error Handling:** The `run()` method should catch and handle errors during both forward and rollback operations. If a rollback operation fails, log the error including the `resourceManagerId`, but continue with the remaining rollbacks. The system should be as resilient as possible to handle failure.
*   **Optimization:** Minimize the overall execution time, especially during the rollback phase. Concurrency and efficient data structures are key.
*   **Logging:** Implement basic logging to track the progress of the transaction, including successful forwards, failed forwards, successful rollbacks, and failed rollbacks. This logging doesn't need to be sophisticated; simple `console.log` statements are sufficient.
*   **Resource Manager Simulation:** You do not need to implement actual resource managers. The `forward` and `rollback` functions will be provided as part of the input. Assume they interact with external systems.  Focus on the orchestration logic.
*   **Memory Management:** Consider potential memory leaks if the system is run for extended periods with many transactions.  While garbage collection is automatic, designing to minimize unnecessary object creation and holding references is important.
*   **Scalability:** While this is a single-machine problem, consider how the design could be adapted to a distributed environment. What changes would be necessary? (This doesn't need to be implemented, just considered in the design).

**Expected Output:**

The `run()` method should return a boolean: `true` if all forward operations succeeded, and `false` if any operation failed (requiring a rollback).

**Example:**

```javascript
const operations = [
  {
    resourceManagerId: "RM1",
    forward: async (data) => { console.log("RM1 forward"); return true; },
    rollback: async (data) => { console.log("RM1 rollback"); return true; },
    data: {value: 1}
  },
  {
    resourceManagerId: "RM2",
    forward: async (data) => { console.log("RM2 forward"); return false; }, // This will cause a rollback
    rollback: async (data) => { console.log("RM2 rollback"); return true; },
    data: {value: 2}
  }
];

const orchestrator = new TransactionOrchestrator(operations);
const result = await orchestrator.run();
console.log(result); // Output: false
// Expected console output (order may vary due to concurrency):
// RM1 forward
// RM2 forward
// RM1 rollback
// false
```

Good luck! This problem requires careful consideration of error handling, concurrency, and data consistency in a distributed environment.
