import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import java.util.*;
import java.util.concurrent.*;
import transaction_coordinator.BankingService;
import transaction_coordinator.TransactionCoordinator;
import transaction_coordinator.TransactionFailureException;
import transaction_coordinator.TransactionTimeoutException;

class TransactionCoordinatorTest {

    static class DummyBankingService implements BankingService {
        private final String name;
        private final boolean prepareSucceeds;
        private boolean committed = false;
        private boolean rolledBack = false;

        public DummyBankingService(String name, boolean prepareSucceeds) {
            this.name = name;
            this.prepareSucceeds = prepareSucceeds;
        }

        @Override
        public boolean prepare(String transactionId) {
            return prepareSucceeds;
        }

        @Override
        public void commit(String transactionId) {
            committed = true;
        }

        @Override
        public void rollback(String transactionId) {
            rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    static class DelayedBankingService implements BankingService {
        private final String name;
        private final long delayMillis;
        private final boolean prepareSucceeds;
        private boolean committed = false;
        private boolean rolledBack = false;

        public DelayedBankingService(String name, long delayMillis, boolean prepareSucceeds) {
            this.name = name;
            this.delayMillis = delayMillis;
            this.prepareSucceeds = prepareSucceeds;
        }

        @Override
        public boolean prepare(String transactionId) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return prepareSucceeds;
        }

        @Override
        public void commit(String transactionId) {
            committed = true;
        }

        @Override
        public void rollback(String transactionId) {
            rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    @Test
    void testSuccessfulTransaction() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        DummyBankingService service1 = new DummyBankingService("BankA", true);
        DummyBankingService service2 = new DummyBankingService("BankB", true);
        List<BankingService> services = Arrays.asList(service1, service2);

        String txnId = coordinator.beginTransaction(services);
        coordinator.performOperation(txnId, "dummy_operation");
        coordinator.commitTransaction(txnId);

        Assertions.assertTrue(service1.isCommitted(), "Service1 should have committed.");
        Assertions.assertTrue(service2.isCommitted(), "Service2 should have committed.");
    }

    @Test
    void testPrepareFailureTransaction() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        DummyBankingService service1 = new DummyBankingService("BankA", false);
        DummyBankingService service2 = new DummyBankingService("BankB", true);
        List<BankingService> services = Arrays.asList(service1, service2);

        String txnId = coordinator.beginTransaction(services);
        coordinator.performOperation(txnId, "dummy_operation");

        Assertions.assertThrows(TransactionFailureException.class, () -> {
            coordinator.commitTransaction(txnId);
        }, "Expected a TransactionFailureException on prepare failure.");

        Assertions.assertTrue(service1.isRolledBack(), "Service1 should have rolled back.");
        Assertions.assertTrue(service2.isRolledBack(), "Service2 should have rolled back.");
    }

    @Test
    void testTimeoutOnPrepare() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        // Assuming the coordinator's prepare timeout is less than 2000ms.
        DelayedBankingService delayedService = new DelayedBankingService("BankDelayed", 3000, true);
        DummyBankingService service2 = new DummyBankingService("BankB", true);
        List<BankingService> services = Arrays.asList(delayedService, service2);

        String txnId = coordinator.beginTransaction(services);
        coordinator.performOperation(txnId, "dummy_operation");

        Assertions.assertThrows(TransactionTimeoutException.class, () -> {
            coordinator.commitTransaction(txnId);
        }, "Expected a TransactionTimeoutException due to prepare timeout.");

        Assertions.assertTrue(delayedService.isRolledBack(), "Delayed service should have rolled back on timeout.");
        Assertions.assertTrue(service2.isRolledBack(), "Service2 should have rolled back on timeout.");
    }

    @Test
    void testMultipleConcurrentTransactions() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < 10; i++) {
            futures.add(executor.submit(() -> {
                DummyBankingService service1 = new DummyBankingService("BankA", true);
                DummyBankingService service2 = new DummyBankingService("BankB", true);
                List<BankingService> services = Arrays.asList(service1, service2);
                String txnId = coordinator.beginTransaction(services);
                coordinator.performOperation(txnId, "dummy_operation");
                coordinator.commitTransaction(txnId);
                return service1.isCommitted() && service2.isCommitted();
            }));
        }

        for (Future<Boolean> future : futures) {
            try {
                Boolean result = future.get(5, TimeUnit.SECONDS);
                Assertions.assertTrue(result, "Concurrent transaction should commit successfully.");
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                Assertions.fail("Concurrent transaction failed: " + e.getMessage());
            }
        }
        executor.shutdown();
    }

    @Test
    void testRollbackTransaction() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        DummyBankingService service1 = new DummyBankingService("BankA", true);
        DummyBankingService service2 = new DummyBankingService("BankB", true);
        List<BankingService> services = Arrays.asList(service1, service2);

        String txnId = coordinator.beginTransaction(services);
        coordinator.performOperation(txnId, "dummy_operation");
        coordinator.rollbackTransaction(txnId);

        Assertions.assertTrue(service1.isRolledBack(), "Service1 should have rolled back.");
        Assertions.assertTrue(service2.isRolledBack(), "Service2 should have rolled back.");
    }
}