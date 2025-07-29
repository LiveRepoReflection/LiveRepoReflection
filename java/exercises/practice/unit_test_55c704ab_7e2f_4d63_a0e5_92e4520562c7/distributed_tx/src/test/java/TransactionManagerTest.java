import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Timeout;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.*;

public class TransactionManagerTest {

    // SimulatedService to mimic microservice behavior for different operations.
    static class SimulatedService {
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private final boolean rollbackSuccess;
        private final int transientFailures; // number of transient failures to simulate per operation
        private final Map<String, AtomicLong> failureCounters = new ConcurrentHashMap<>();

        public SimulatedService(boolean prepareSuccess, boolean commitSuccess, boolean rollbackSuccess, int transientFailures) {
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
            this.rollbackSuccess = rollbackSuccess;
            this.transientFailures = transientFailures;
        }

        public boolean call(String operation, long transactionId) throws Exception {
            // Initialize counter if not present.
            failureCounters.putIfAbsent(operation, new AtomicLong(0));
            long currFailures = failureCounters.get(operation).get();
            if (currFailures < transientFailures) {
                failureCounters.get(operation).incrementAndGet();
                throw new Exception("Transient failure on " + operation);
            }
            if ("prepare".equals(operation)) {
                return prepareSuccess;
            } else if ("commit".equals(operation)) {
                return commitSuccess;
            } else if ("rollback".equals(operation)) {
                return rollbackSuccess;
            } else {
                throw new Exception("Unknown operation: " + operation);
            }
        }

        // Reset failure counters for reuse in different tests
        public void resetCounters() {
            failureCounters.clear();
        }
    }

    // TestTransactionManager extends the production TransactionManager to override callService behavior.
    static class TestTransactionManager extends TransactionManager {
        private final Map<String, SimulatedService> serviceMap = new ConcurrentHashMap<>();

        public void setServiceBehavior(String serviceEndpoint, SimulatedService service) {
            serviceMap.put(serviceEndpoint, service);
        }

        @Override
        protected boolean callService(String serviceEndpoint, String operation, long transactionId) throws Exception {
            SimulatedService svc = serviceMap.get(serviceEndpoint);
            // If no behavior set for this service, default to success.
            if (svc == null) {
                return true;
            }
            // Implement retry logic: 3 retries with exponential backoff.
            int maxRetries = 3;
            int attempt = 0;
            long backoff = 100; // milliseconds
            while (true) {
                try {
                    return svc.call(operation, transactionId);
                } catch (Exception e) {
                    attempt++;
                    if (attempt >= maxRetries) {
                        throw e;
                    }
                    Thread.sleep(backoff);
                    backoff *= 2;
                }
            }
        }
    }

    private TestTransactionManager txManager;

    @BeforeEach
    public void setup() {
        txManager = new TestTransactionManager();
    }

    @Test
    public void testBeginTransactionGeneratesUniqueIds() {
        Set<Long> ids = new HashSet<>();
        for (int i = 0; i < 100; i++) {
            long id = txManager.begin();
            assertFalse(ids.contains(id), "Transaction ID should be unique");
            ids.add(id);
        }
    }

    @Test
    public void testSuccessfulCommit() throws Exception {
        long txId = txManager.begin();
        // Setup two services with all operations succeeding.
        String service1 = "http://service1";
        String service2 = "http://service2";
        txManager.enlist(txId, service1);
        txManager.enlist(txId, service2);

        txManager.setServiceBehavior(service1, new SimulatedService(true, true, true, 0));
        txManager.setServiceBehavior(service2, new SimulatedService(true, true, true, 0));

        boolean commitResult = txManager.commit(txId);
        assertTrue(commitResult, "Commit should succeed when all services operate correctly.");
    }

    @Test
    public void testPrepareFailureTriggersRollback() throws Exception {
        long txId = txManager.begin();
        String service1 = "http://service1";
        String service2 = "http://failPrepareService";
        txManager.enlist(txId, service1);
        txManager.enlist(txId, service2);

        // service1 succeeds in all phases, service2 fails in prepare.
        txManager.setServiceBehavior(service1, new SimulatedService(true, true, true, 0));
        txManager.setServiceBehavior(service2, new SimulatedService(false, true, true, 0)); // prepare fails

        boolean commitResult = txManager.commit(txId);
        assertFalse(commitResult, "Commit should fail if any service fails during prepare.");

        boolean rollbackResult = txManager.rollback(txId);
        assertTrue(rollbackResult, "Rollback should succeed when all enlisted services can rollback.");
    }

    @Test
    public void testCommitFailureTriggersRollback() throws Exception {
        long txId = txManager.begin();
        String service1 = "http://service1";
        String service2 = "http://failCommitService";
        txManager.enlist(txId, service1);
        txManager.enlist(txId, service2);

        // Both services prepare successfully, but service2 fails during commit.
        txManager.setServiceBehavior(service1, new SimulatedService(true, true, true, 0));
        txManager.setServiceBehavior(service2, new SimulatedService(true, false, true, 0)); // commit fails

        boolean commitResult = txManager.commit(txId);
        assertFalse(commitResult, "Commit should fail if any service fails during commit.");

        boolean rollbackResult = txManager.rollback(txId);
        assertTrue(rollbackResult, "Rollback should succeed even if commit partially failed.");
    }

    @Test
    public void testRollbackFailure() throws Exception {
        long txId = txManager.begin();
        String service1 = "http://service1";
        String service2 = "http://rollbackFailService";
        txManager.enlist(txId, service1);
        txManager.enlist(txId, service2);

        // Setup scenario where commit fails on service2 triggering rollback,
        // but rollback fails on service2.
        txManager.setServiceBehavior(service1, new SimulatedService(true, true, true, 0));
        txManager.setServiceBehavior(service2, new SimulatedService(true, false, false, 0)); // commit fails, rollback fails

        boolean commitResult = txManager.commit(txId);
        assertFalse(commitResult, "Commit should fail if any service fails during commit.");

        boolean rollbackResult = txManager.rollback(txId);
        assertFalse(rollbackResult, "Rollback should fail if any service fails during rollback.");
    }

    @Test
    public void testTransientFailuresAreRetried() throws Exception {
        long txId = txManager.begin();
        String service1 = "http://transientService";
        txManager.enlist(txId, service1);

        // Setup a service that fails once transiently on each operation.
        txManager.setServiceBehavior(service1, new SimulatedService(true, true, true, 1));

        boolean commitResult = txManager.commit(txId);
        assertTrue(commitResult, "Commit should eventually succeed after transient failures are retried.");
    }

    @Test
    @Timeout(5)
    public void testConcurrentTransactions() throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        int numTransactions = 50;
        CountDownLatch latch = new CountDownLatch(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        // Each transaction uses a dedicated service endpoint.
        for (int i = 0; i < numTransactions; i++) {
            final int index = i;
            Future<Boolean> future = executor.submit(() -> {
                long txId = txManager.begin();
                String serviceEndpoint = "http://concurrentService" + index;
                txManager.enlist(txId, serviceEndpoint);
                // All operations succeed.
                txManager.setServiceBehavior(serviceEndpoint, new SimulatedService(true, true, true, 0));
                boolean commitResult = txManager.commit(txId);
                latch.countDown();
                return commitResult;
            });
            futures.add(future);
        }
        latch.await();
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully.");
        }
        executor.shutdown();
    }
}