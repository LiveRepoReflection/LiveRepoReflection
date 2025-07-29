import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assertions;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTxCoordinatorTest {

    public enum TransactionStatus {
        COMMITTED, ROLLEDBACK
    }

    public static class Transaction {
        String id;
        List<String> serviceIds;
        String operation;

        public Transaction(String id, List<String> serviceIds, String operation) {
            this.id = id;
            this.serviceIds = serviceIds;
            this.operation = operation;
        }
    }

    public interface Service {
        boolean prepare(String transactionId, String operation) throws Exception;
        void commit(String transactionId) throws Exception;
        void rollback(String transactionId) throws Exception;
    }

    public static class DummyService implements Service {
        public enum Mode { NORMAL, FAIL_PREPARE, TIMEOUT }

        private final String serviceId;
        private final Mode mode;
        private final List<String> commitLog = new ArrayList<>();
        private final List<String> rollbackLog = new ArrayList<>();

        public DummyService(String serviceId, Mode mode) {
            this.serviceId = serviceId;
            this.mode = mode;
        }

        @Override
        public boolean prepare(String transactionId, String operation) throws Exception {
            if (mode == Mode.TIMEOUT) {
                // Sleep longer than the coordinator timeout (assumed to be 5000ms)
                Thread.sleep(6000);
            }
            if (mode == Mode.FAIL_PREPARE) {
                return false;
            }
            return true;
        }

        @Override
        public void commit(String transactionId) {
            commitLog.add(transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            rollbackLog.add(transactionId);
        }

        public boolean isCommitted(String transactionId) {
            return commitLog.contains(transactionId);
        }

        public boolean isRolledBack(String transactionId) {
            return rollbackLog.contains(transactionId);
        }
    }

    // Dummy implementation of the Distributed Transaction Coordinator.
    // This implementation simulates the two-phase commit protocol.
    public static class DistributedTxCoordinator {
        private final Map<String, Service> serviceRegistry;
        private final ExecutorService executor = Executors.newCachedThreadPool();

        public DistributedTxCoordinator(Map<String, Service> serviceRegistry) {
            this.serviceRegistry = serviceRegistry;
        }

        public TransactionStatus processTransaction(Transaction tx) {
            // Phase 1: Prepare Phase
            Map<String, Future<Boolean>> futures = new HashMap<>();
            for (String serviceId : tx.serviceIds) {
                Service service = serviceRegistry.get(serviceId);
                Future<Boolean> future = executor.submit(() -> {
                    try {
                        return service.prepare(tx.id, tx.operation);
                    } catch (Exception e) {
                        return false;
                    }
                });
                futures.put(serviceId, future);
            }

            boolean allPrepared = true;
            for (Map.Entry<String, Future<Boolean>> entry : futures.entrySet()) {
                try {
                    boolean result = entry.getValue().get(5, TimeUnit.SECONDS);
                    if (!result) {
                        allPrepared = false;
                    }
                } catch (Exception e) {
                    allPrepared = false;
                }
            }

            // Phase 2: Commit or Rollback Phase
            for (String serviceId : tx.serviceIds) {
                Service service = serviceRegistry.get(serviceId);
                try {
                    if (allPrepared) {
                        service.commit(tx.id);
                    } else {
                        service.rollback(tx.id);
                    }
                } catch (Exception e) {
                    // In this test stub, exceptions in commit/rollback are not propagated.
                }
            }

            return allPrepared ? TransactionStatus.COMMITTED : TransactionStatus.ROLLEDBACK;
        }

        public void shutdown() {
            executor.shutdownNow();
        }
    }

    private Map<String, Service> serviceRegistry;
    private DistributedTxCoordinator coordinator;

    @BeforeEach
    public void setup() {
        serviceRegistry = new HashMap<>();
    }

    @Test
    public void testSuccessfulCommit() {
        String txId = "tx1";
        DummyService serviceA = new DummyService("ServiceA", DummyService.Mode.NORMAL);
        DummyService serviceB = new DummyService("ServiceB", DummyService.Mode.NORMAL);
        serviceRegistry.put("ServiceA", serviceA);
        serviceRegistry.put("ServiceB", serviceB);

        coordinator = new DistributedTxCoordinator(serviceRegistry);
        Transaction tx = new Transaction(txId, Arrays.asList("ServiceA", "ServiceB"), "transferFunds");
        TransactionStatus status = coordinator.processTransaction(tx);

        Assertions.assertEquals(TransactionStatus.COMMITTED, status);
        Assertions.assertTrue(serviceA.isCommitted(txId));
        Assertions.assertTrue(serviceB.isCommitted(txId));
        coordinator.shutdown();
    }

    @Test
    public void testFailureRollback() {
        String txId = "tx2";
        DummyService serviceA = new DummyService("ServiceA", DummyService.Mode.NORMAL);
        DummyService serviceB = new DummyService("ServiceB", DummyService.Mode.FAIL_PREPARE);
        serviceRegistry.put("ServiceA", serviceA);
        serviceRegistry.put("ServiceB", serviceB);

        coordinator = new DistributedTxCoordinator(serviceRegistry);
        Transaction tx = new Transaction(txId, Arrays.asList("ServiceA", "ServiceB"), "transferFunds");
        TransactionStatus status = coordinator.processTransaction(tx);

        Assertions.assertEquals(TransactionStatus.ROLLEDBACK, status);
        Assertions.assertTrue(serviceA.isRolledBack(txId));
        Assertions.assertTrue(serviceB.isRolledBack(txId));
        coordinator.shutdown();
    }

    @Test
    public void testTimeoutRollback() {
        String txId = "tx3";
        DummyService serviceA = new DummyService("ServiceA", DummyService.Mode.NORMAL);
        DummyService serviceB = new DummyService("ServiceB", DummyService.Mode.TIMEOUT);
        serviceRegistry.put("ServiceA", serviceA);
        serviceRegistry.put("ServiceB", serviceB);

        coordinator = new DistributedTxCoordinator(serviceRegistry);
        Transaction tx = new Transaction(txId, Arrays.asList("ServiceA", "ServiceB"), "transferFunds");
        TransactionStatus status = coordinator.processTransaction(tx);

        Assertions.assertEquals(TransactionStatus.ROLLEDBACK, status);
        Assertions.assertTrue(serviceA.isRolledBack(txId));
        Assertions.assertTrue(serviceB.isRolledBack(txId));
        coordinator.shutdown();
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService testExecutor = Executors.newFixedThreadPool(numTransactions);
        List<Future<TransactionStatus>> futures = new ArrayList<>();
        AtomicInteger txCounter = new AtomicInteger(100);

        DummyService serviceA = new DummyService("ServiceA", DummyService.Mode.NORMAL);
        DummyService serviceB = new DummyService("ServiceB", DummyService.Mode.NORMAL);
        DummyService serviceC = new DummyService("ServiceC", DummyService.Mode.NORMAL);
        serviceRegistry.put("ServiceA", serviceA);
        serviceRegistry.put("ServiceB", serviceB);
        serviceRegistry.put("ServiceC", serviceC);

        coordinator = new DistributedTxCoordinator(serviceRegistry);

        for (int i = 0; i < numTransactions; i++) {
            futures.add(testExecutor.submit(() -> {
                String txId = "tx" + txCounter.getAndIncrement();
                Transaction tx = new Transaction(txId, Arrays.asList("ServiceA", "ServiceB", "ServiceC"), "transferFunds");
                return coordinator.processTransaction(tx);
            }));
        }

        for (Future<TransactionStatus> future : futures) {
            TransactionStatus status = future.get();
            Assertions.assertEquals(TransactionStatus.COMMITTED, status);
        }

        coordinator.shutdown();
        testExecutor.shutdownNow();
    }
}