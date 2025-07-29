import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.ArrayList;
import java.util.Collections;

public class TransactionCoordinator {

    private final int numServices;
    private final MockMicroservice[] services;

    // Use ConcurrentHashMap for thread safety
    private final Map<UUID, List<ServiceOperation>> transactions = new ConcurrentHashMap<>();

    // Thread pool for concurrent execution/rollback
    private final ExecutorService executor;

    public TransactionCoordinator(int numServices) {
        this.numServices = numServices;
        this.services = createMicroservices(numServices);
        // Create a thread pool with a fixed number of threads to handle concurrent operations
        this.executor = Executors.newFixedThreadPool(numServices);
    }
    
    // Method to support mocking services in tests
    protected MockMicroservice[] createMicroservices(int numServices) {
        MockMicroservice[] services = new MockMicroservice[numServices];
        for (int i = 0; i < numServices; i++) {
            services[i] = new MockMicroservice(i);
        }
        return services;
    }

    public UUID begin() {
        UUID transactionId = UUID.randomUUID();
        transactions.put(transactionId, Collections.synchronizedList(new ArrayList<>()));
        return transactionId;
    }

    public void register(UUID transactionId, int serviceId, String operationData) {
        // Validate the transaction exists
        List<ServiceOperation> operations = transactions.get(transactionId);
        if (operations == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        
        // Validate the service ID
        if (serviceId < 0 || serviceId >= numServices) {
            throw new IllegalArgumentException("Invalid service ID: " + serviceId);
        }
        
        // Register the service operation for this transaction
        operations.add(new ServiceOperation(serviceId, operationData));
    }

    public boolean commit(UUID transactionId) {
        // Validate transaction exists
        List<ServiceOperation> operations = transactions.get(transactionId);
        if (operations == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        
        // If no operations, consider it successful
        if (operations.isEmpty()) {
            return true;
        }
        
        // Create array to hold futures for each operation
        CompletableFuture<Void>[] futures = new CompletableFuture[operations.size()];
        
        // Prepare phase is assumed to succeed, so we'll go directly to commit phase
        AtomicBoolean success = new AtomicBoolean(true);
        CountDownLatch latch = new CountDownLatch(operations.size());
        
        // Execute all operations concurrently
        for (int i = 0; i < operations.size(); i++) {
            final int index = i;
            final ServiceOperation operation = operations.get(i);
            
            futures[i] = CompletableFuture.runAsync(() -> {
                try {
                    services[operation.serviceId].executeTransaction(transactionId, operation.operationData);
                } catch (Exception e) {
                    // Mark transaction as failed
                    success.set(false);
                    System.err.println("Service " + operation.serviceId + " failed during commit: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            }, executor);
        }
        
        try {
            // Wait for all operations to complete
            latch.await();
            
            // If any operation failed, initiate rollback
            if (!success.get()) {
                rollback(transactionId);
                return false;
            }
            
            // All operations successful, return true
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            // Rollback on interruption
            rollback(transactionId);
            return false;
        }
    }

    public void rollback(UUID transactionId) {
        // Validate transaction exists
        List<ServiceOperation> operations = transactions.get(transactionId);
        if (operations == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        
        // If no operations, nothing to rollback
        if (operations.isEmpty()) {
            return;
        }
        
        // Track unique service IDs that participated in this transaction
        // Using a map for O(1) lookup to avoid rolling back the same service multiple times
        Map<Integer, Boolean> participatingServices = new ConcurrentHashMap<>();
        for (ServiceOperation op : operations) {
            participatingServices.put(op.serviceId, true);
        }
        
        // Create array to hold futures for each rollback operation
        CompletableFuture<Void>[] futures = new CompletableFuture[participatingServices.size()];
        CountDownLatch latch = new CountDownLatch(participatingServices.size());
        
        // Execute rollback operations concurrently
        int i = 0;
        for (Integer serviceId : participatingServices.keySet()) {
            futures[i] = CompletableFuture.runAsync(() -> {
                try {
                    services[serviceId].rollbackTransaction(transactionId);
                } catch (Exception e) {
                    // Log rollback failure but continue with other rollbacks
                    System.err.println("Service " + serviceId + " failed during rollback: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            }, executor);
            i++;
        }
        
        try {
            // Wait for all rollback operations to complete
            latch.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println("Rollback was interrupted: " + e.getMessage());
        }
    }

    // Helper class to store service operations
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
        System.out.println("Transaction " + failedTxId + " committed: " + failedCommit); // May print false if service fails

        // Shut down the executor service
        coordinator.executor.shutdown();
    }
}