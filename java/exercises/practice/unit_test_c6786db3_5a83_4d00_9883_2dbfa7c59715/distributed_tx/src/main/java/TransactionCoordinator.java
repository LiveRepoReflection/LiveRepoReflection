import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
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
        this.executor = Executors.newFixedThreadPool(numServices); // Adjust pool size as needed
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