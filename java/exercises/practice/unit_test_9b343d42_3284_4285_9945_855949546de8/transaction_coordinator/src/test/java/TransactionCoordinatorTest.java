package transaction_coordinator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

public class TransactionCoordinatorTest {

    // Dummy implementation of the ParticipantService interface to simulate service behavior.
    static class DummyService implements ParticipantService {
        private final String serviceId;
        private final String vote; // "commit" or "abort"
        private final long prepareDelayMillis;
        private final long commitDelayMillis;
        private final long rollbackDelayMillis;
        private final int maxFailures; // number of times to fail during prepare before succeeding
        private final AtomicInteger failureCount = new AtomicInteger(0);

        public DummyService(String serviceId, String vote, long prepareDelayMillis, long commitDelayMillis, long rollbackDelayMillis, int maxFailures) {
            this.serviceId = serviceId;
            this.vote = vote;
            this.prepareDelayMillis = prepareDelayMillis;
            this.commitDelayMillis = commitDelayMillis;
            this.rollbackDelayMillis = rollbackDelayMillis;
            this.maxFailures = maxFailures;
        }

        @Override
        public String prepare(String transactionId, String operation) throws Exception {
            Thread.sleep(prepareDelayMillis);
            // Simulate failures for retry mechanism.
            if (failureCount.getAndIncrement() < maxFailures) {
                throw new Exception("Simulated prepare failure for service " + serviceId);
            }
            return vote;
        }

        @Override
        public void commit(String transactionId) throws Exception {
            Thread.sleep(commitDelayMillis);
            // In a real scenario, commit logic would be here.
        }

        @Override
        public void rollback(String transactionId) throws Exception {
            Thread.sleep(rollbackDelayMillis);
            // In a real scenario, rollback logic would be here.
        }
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        // All participating services vote "commit" and respond within acceptable time.
        Map<String, ParticipantService> services = new HashMap<>();
        Map<String, String> operations = new HashMap<>();
        for (int i = 1; i <= 3; i++) {
            String serviceId = "service" + i;
            services.put(serviceId, new DummyService(serviceId, "commit", 100, 100, 100, 0));
            operations.put(serviceId, "operation" + i);
        }
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction("txn_success", services, operations);
        Assertions.assertTrue(result, "Transaction should be committed successfully");
    }

    @Test
    public void testTransactionRollbackDueToAbortVote() throws Exception {
        // One service votes "abort", so the transaction should rollback.
        Map<String, ParticipantService> services = new HashMap<>();
        Map<String, String> operations = new HashMap<>();
        
        services.put("service1", new DummyService("service1", "commit", 100, 100, 100, 0));
        operations.put("service1", "op1");
        
        services.put("service2", new DummyService("service2", "abort", 100, 100, 100, 0));
        operations.put("service2", "op2");
        
        services.put("service3", new DummyService("service3", "commit", 100, 100, 100, 0));
        operations.put("service3", "op3");

        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction("txn_abort", services, operations);
        Assertions.assertFalse(result, "Transaction should rollback due to an abort vote");
    }

    @Test
    public void testTransactionTimeoutInPreparePhase() throws Exception {
        // Simulate a timeout in the prepare phase by delaying one service beyond the coordinator's timeout threshold.
        Map<String, ParticipantService> services = new HashMap<>();
        Map<String, String> operations = new HashMap<>();
        
        services.put("service1", new DummyService("service1", "commit", 100, 100, 100, 0));
        operations.put("service1", "op1");
        
        // This service delays its prepare call to simulate a timeout.
        services.put("service2", new DummyService("service2", "commit", 500, 100, 100, 0));
        operations.put("service2", "op2");

        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction("txn_timeout", services, operations);
        Assertions.assertFalse(result, "Transaction should rollback due to timeout in prepare phase");
    }

    @Test
    public void testRetryMechanismOnPrepareFailure() throws Exception {
        // Simulate a service that fails a couple of times during prepare before eventually succeeding.
        Map<String, ParticipantService> services = new HashMap<>();
        Map<String, String> operations = new HashMap<>();
        
        // service1 will fail twice then succeed.
        services.put("service1", new DummyService("service1", "commit", 100, 100, 100, 2));
        operations.put("service1", "op1");
        
        services.put("service2", new DummyService("service2", "commit", 100, 100, 100, 0));
        operations.put("service2", "op2");

        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction("txn_retry", services, operations);
        Assertions.assertTrue(result, "Transaction should commit successfully after retries during prepare");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Test handling multiple concurrent transactions.
        int numberOfTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numberOfTransactions);
        CountDownLatch latch = new CountDownLatch(numberOfTransactions);
        ConcurrentMap<String, Boolean> results = new ConcurrentHashMap<>();

        for (int i = 0; i < numberOfTransactions; i++) {
            final int txnNum = i;
            executor.submit(() -> {
                try {
                    Map<String, ParticipantService> services = new HashMap<>();
                    Map<String, String> operations = new HashMap<>();
                    // For even-numbered transactions, all services commit.
                    // For odd-numbered transactions, one service votes "abort".
                    String voteForService2 = (txnNum % 2 == 0) ? "commit" : "abort";
                    
                    services.put("service1", new DummyService("service1", "commit", 50, 50, 50, 0));
                    operations.put("service1", "op1");
                    
                    services.put("service2", new DummyService("service2", voteForService2, 50, 50, 50, 0));
                    operations.put("service2", "op2");

                    TransactionCoordinator coordinator = new TransactionCoordinator();
                    boolean res = coordinator.executeTransaction("txn_concurrent_" + txnNum, services, operations);
                    results.put("txn_concurrent_" + txnNum, res);
                } catch (Exception e) {
                    results.put("txn_concurrent_" + txnNum, false);
                } finally {
                    latch.countDown();
                }
            });
        }
        latch.await();
        executor.shutdown();

        // Verify the results of concurrent transactions.
        for (int i = 0; i < numberOfTransactions; i++) {
            String txnKey = "txn_concurrent_" + i;
            if (i % 2 == 0) {
                Assertions.assertTrue(results.get(txnKey), "Transaction " + txnKey + " should be committed");
            } else {
                Assertions.assertFalse(results.get(txnKey), "Transaction " + txnKey + " should be rolled back");
            }
        }
    }
}