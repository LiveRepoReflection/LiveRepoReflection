import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinator {

    public enum TransactionStatus {
        PREPARING, COMMITTED, ROLLED_BACK, FAILED
    }

    public interface Service {
        boolean prepare(String transactionId);
        void commit(String transactionId);
        void rollback(String transactionId);
    }

    private final ConcurrentMap<String, TransactionStatus> transactionStatusMap = new ConcurrentHashMap<>();
    private final ExecutorService executorService = Executors.newCachedThreadPool();

    public String startTransaction(List<Service> services) {
        final String txId = UUID.randomUUID().toString();
        transactionStatusMap.put(txId, TransactionStatus.PREPARING);
        executorService.submit(() -> {
            try {
                boolean allPrepared = true;
                List<Future<Boolean>> prepareFutures = new ArrayList<>();
                for (Service service : services) {
                    prepareFutures.add(executorService.submit(() -> service.prepare(txId)));
                }
                for (Future<Boolean> future : prepareFutures) {
                    if (!future.get()) {
                        allPrepared = false;
                        break;
                    }
                }
                if (allPrepared) {
                    List<Future<?>> commitFutures = new ArrayList<>();
                    for (Service service : services) {
                        commitFutures.add(executorService.submit(() -> {
                            service.commit(txId);
                            return null;
                        }));
                    }
                    for (Future<?> future : commitFutures) {
                        future.get();
                    }
                    transactionStatusMap.put(txId, TransactionStatus.COMMITTED);
                } else {
                    List<Future<?>> rollbackFutures = new ArrayList<>();
                    for (Service service : services) {
                        rollbackFutures.add(executorService.submit(() -> {
                            service.rollback(txId);
                            return null;
                        }));
                    }
                    for (Future<?> future : rollbackFutures) {
                        future.get();
                    }
                    transactionStatusMap.put(txId, TransactionStatus.ROLLED_BACK);
                }
            } catch (Exception e) {
                transactionStatusMap.put(txId, TransactionStatus.FAILED);
            }
        });
        return txId;
    }

    public TransactionStatus getTransactionStatus(String txId) {
        return transactionStatusMap.get(txId);
    }

    public void shutdown() {
        executorService.shutdown();
    }
}