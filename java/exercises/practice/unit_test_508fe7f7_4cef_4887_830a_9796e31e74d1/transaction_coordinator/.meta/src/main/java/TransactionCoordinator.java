import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class TransactionCoordinator {
    private final Set<Service> services;
    private final ExecutorService executor;

    public TransactionCoordinator(Set<Service> services) {
        this.services = services;
        // Using cached thread pool for scalability and dynamic thread management.
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean executeTransaction(UUID transactionId, Map<Service, OperationData> operations) {
        // Prepare Phase: Execute prepare concurrently for all services.
        List<CompletableFuture<Boolean>> prepareFutures = new ArrayList<>();
        for (Service service : services) {
            OperationData opData = operations.get(service);
            if (opData == null) {
                // If no operation data provided for a service, consider prepare as failure.
                prepareFutures.add(CompletableFuture.completedFuture(false));
            } else {
                CompletableFuture<Boolean> prepareFuture = CompletableFuture.supplyAsync(() -> service.prepare(transactionId, opData), executor);
                prepareFutures.add(prepareFuture);
            }
        }

        CompletableFuture<Void> allPrepare = CompletableFuture.allOf(prepareFutures.toArray(new CompletableFuture[0]));
        boolean prepareSuccess = allPrepare.thenApply(v -> 
            prepareFutures.stream().allMatch(future -> {
                try {
                    return future.get();
                } catch (InterruptedException | ExecutionException e) {
                    return false;
                }
            })
        ).join();

        if (prepareSuccess) {
            // Commit Phase: Execute commit concurrently for all services.
            List<CompletableFuture<Void>> commitFutures = services.stream()
                .map(service -> CompletableFuture.runAsync(() -> {
                    try {
                        service.commit(transactionId);
                    } catch (Exception e) {
                        System.err.println("Error during commit for transaction " + transactionId + " on service " + service + ": " + e.getMessage());
                    }
                }, executor))
                .collect(Collectors.toList());
            CompletableFuture.allOf(commitFutures.toArray(new CompletableFuture[0])).join();
        } else {
            // Rollback Phase: Execute rollback concurrently for all services.
            List<CompletableFuture<Void>> rollbackFutures = services.stream()
                .map(service -> CompletableFuture.runAsync(() -> {
                    try {
                        service.rollback(transactionId);
                    } catch (Exception e) {
                        System.err.println("Error during rollback for transaction " + transactionId + " on service " + service + ": " + e.getMessage());
                    }
                }, executor))
                .collect(Collectors.toList());
            CompletableFuture.allOf(rollbackFutures.toArray(new CompletableFuture[0])).join();
        }

        return prepareSuccess;
    }
}