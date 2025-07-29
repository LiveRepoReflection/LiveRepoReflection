## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator for a microservices architecture. Multiple services need to perform operations atomically. If any service fails, all operations across all services must be rolled back.

You are given a cluster of `n` microservices. Each microservice `i` has an ID from `0` to `n-1`. Each microservice exposes an API endpoint `executeTransaction(transactionId, operationData)` and `rollbackTransaction(transactionId)`.

Your task is to implement a `TransactionCoordinator` class with the following functionalities:

1.  **`begin()`:** Starts a new distributed transaction. Returns a unique transaction ID (UUID).

2.  **`register(transactionId, serviceId, operationData)`:** Registers a service with the coordinator for a specific transaction. `serviceId` represents the ID of the microservice (`0` to `n-1`). `operationData` is service-specific data required to execute the transaction. This function should ensure that the transaction exists and that the service ID is valid.

3.  **`commit(transactionId)`:** Attempts to commit the distributed transaction. This involves the following steps:

    *   **Prepare Phase:** The coordinator sends a "prepare" message to each registered service. For simplicity, assume that the prepare phase always succeeds.

    *   **Commit Phase:** The coordinator invokes the `executeTransaction(transactionId, operationData)` endpoint on each registered service **concurrently**.

        *   If all services execute successfully (no exceptions thrown), the transaction is considered committed. Return `true`.
        *   If any service fails during execution, the transaction is considered failed. Proceed to the rollback phase.

4.  **`rollback(transactionId)`:** Rolls back a failed transaction. This involves invoking the `rollbackTransaction(transactionId)` endpoint on each service that was registered for the transaction **concurrently**. After rollback, the transaction is considered aborted.

**Constraints and Requirements:**

*   **Atomicity:** The system must ensure atomicity of transactions. Either all registered operations are executed successfully, or all are rolled back in case of any failure.
*   **Concurrency:**  `commit()` and `rollback()` must execute the operations on services concurrently using multithreading/parallelism.
*   **Idempotency:** The implementation *does not* need to worry about idempotency. Assume that `executeTransaction()` and `rollbackTransaction()` are *not* idempotent.
*   **Fault Tolerance:** The coordinator itself is assumed to be reliable. You don't need to handle coordinator failures. The microservices are assumed to be reliable during the execution and rollback phases.
*   **Scalability:**  While you don't need to implement actual distributed communication, the design should be scalable to a large number of services and concurrent transactions. Consider the data structures and algorithms used and their time/space complexity.
*   **Error Handling:** Implement robust error handling. Throw exceptions for invalid transaction IDs, invalid service IDs, and any other error conditions.
*   **Service Interface:** You *cannot* modify the `executeTransaction()` or `rollbackTransaction()` service endpoint signatures.
*   **Optimization:** The `register` calls are frequent, and `commit` and `rollback` are less frequent, but have high performance requirements. Optimize for fast `commit` and `rollback` times, while maintaining reasonable `register` performance.

**Assumptions:**

*   You are given a mock implementation of the microservices that simulates network calls and potential failures (see `MockMicroservice` below).
*   You can use any standard Java libraries and data structures.

**Code Structure:**

```java
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.ArrayList;
import java.util.Collections;

class MockMicroservice {
    private final int serviceId;

    public MockMicroservice(int serviceId) {
        this.serviceId = serviceId;
    }

    //Simulates calling the microservice
    public void executeTransaction(UUID transactionId, String operationData) {
        // Simulate some work and potential failure
        try {
            Thread.sleep((long)(Math.random() * 100)); // Simulate variable execution time
            if (Math.random() < 0.1) { // Simulate a 10% chance of failure
                throw new RuntimeException("Service " + serviceId + " failed to execute transaction " + transactionId);
            }
            System.out.println("Service " + serviceId + " executed transaction " + transactionId + " with data: " + operationData);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Service " + serviceId + " interrupted during transaction " + transactionId, e);
        }
    }

    public void rollbackTransaction(UUID transactionId) {
        // Simulate rollback
        try {
            Thread.sleep((long)(Math.random() * 50)); // Simulate variable rollback time
            System.out.println("Service " + serviceId + " rolled back transaction " + transactionId);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Service " + serviceId + " interrupted during rollback of transaction " + transactionId, e);
        }
    }
}


public class TransactionCoordinator {

    private final int numServices;
    private final MockMicroservice[] services;

    // Use ConcurrentHashMap for thread safety
    private final Map<UUID, List<ServiceOperation>> transactions = new ConcurrentHashMap<>();

    // Thread pool for concurrent execution/rollback
    private final ExecutorService executor;


    public TransactionCoordinator(int numServices) {
        this.numServices = numServices;
        this.services = new MockMicroservice[numServices];
        for (int i = 0; i < numServices; i++) {
            this.services[i] = new MockMicroservice(i);
        }
        this.executor = Executors.newFixedThreadPool(numServices); // Adjust pool size as needed
    }

    public UUID begin() {
        UUID transactionId = UUID.randomUUID();
        transactions.put(transactionId, Collections.synchronizedList(new ArrayList<>())); // Thread-safe List
        return transactionId;
    }


    public void register(UUID transactionId, int serviceId, String operationData) {
        // TODO: Implement registration logic
    }

    public boolean commit(UUID transactionId) {
        // TODO: Implement commit logic
        return false;
    }

    public void rollback(UUID transactionId) {
        // TODO: Implement rollback logic
    }


    //Helper class to store service operations
    private static class ServiceOperation {
        int serviceId;
        String operationData;

        public ServiceOperation(int serviceId, String operationData) {
            this.serviceId = serviceId;
            this.operationData = operationData;
        }
    }


    public static void main(String[] args) {
        // Example Usage
        TransactionCoordinator coordinator = new TransactionCoordinator(5); // 5 microservices

        UUID txId = coordinator.begin();
        System.out.println("Started transaction: " + txId);

        coordinator.register(txId, 0, "Operation data for service 0");
        coordinator.register(txId, 1, "Operation data for service 1");
        coordinator.register(txId, 2, "Operation data for service 2");

        boolean committed = coordinator.commit(txId);
        System.out.println("Transaction " + txId + " committed: " + committed);

        // Example of a failed transaction
        UUID failedTxId = coordinator.begin();
        coordinator.register(failedTxId, 0, "Data for service 0");
        coordinator.register(failedTxId, 3, "This service might fail"); // Service 3 is more likely to fail

        boolean failedCommit = coordinator.commit(failedTxId);
        System.out.println("Transaction " + failedTxId + " committed: " + failedCommit); // Should print false.
    }
}

```

**Your task is to complete the implementation of the `TransactionCoordinator` class, including the `register`, `commit`, and `rollback` methods.**  Focus on correctness, concurrency, and scalability.  Consider the time and space complexity of your solution.
