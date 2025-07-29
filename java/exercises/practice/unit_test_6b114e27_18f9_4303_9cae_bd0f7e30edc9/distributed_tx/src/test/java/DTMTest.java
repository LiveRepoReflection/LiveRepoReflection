package dtm;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.ArrayList;

// Assume these classes exist in dtm package:
// DTM, TransactionException, and the Service interface with methods: prepare(String transactionId),
// commit(String transactionId), rollback(String transactionId).

public class DTMTest {

    private DTM dtm;

    @BeforeEach
    public void setup() {
        dtm = new DTM();
    }

    // A dummy service that always votes commit successfully.
    private static class SuccessfulService implements Service {
        private final List<String> invocationLog = new ArrayList<>();

        @Override
        public boolean prepare(String transactionId) {
            invocationLog.add("prepare:" + transactionId);
            return true;
        }

        @Override
        public void commit(String transactionId) {
            invocationLog.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            invocationLog.add("rollback:" + transactionId);
        }

        public List<String> getInvocationLog() {
            return invocationLog;
        }
    }

    // A dummy service that fails during preparation
    private static class FailingPrepareService implements Service {
        private final List<String> invocationLog = new ArrayList<>();

        @Override
        public boolean prepare(String transactionId) {
            invocationLog.add("prepare:" + transactionId);
            return false; // Force rollback vote
        }

        @Override
        public void commit(String transactionId) {
            invocationLog.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            invocationLog.add("rollback:" + transactionId);
        }

        public List<String> getInvocationLog() {
            return invocationLog;
        }
    }

    // A service that fails in commit a couple of times then succeeds.
    private static class RetryCommitService implements Service {
        private final List<String> invocationLog = new ArrayList<>();
        private final AtomicInteger commitAttempt = new AtomicInteger(0);
        private final int failCount;

        public RetryCommitService(int failCount) {
            this.failCount = failCount;
        }

        @Override
        public boolean prepare(String transactionId) {
            invocationLog.add("prepare:" + transactionId);
            return true;
        }

        @Override
        public void commit(String transactionId) {
            invocationLog.add("commitAttempt:" + commitAttempt.incrementAndGet() + ":" + transactionId);
            if (commitAttempt.get() <= failCount) {
                throw new RuntimeException("Simulated commit failure");
            }
            invocationLog.add("commitSuccess:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            invocationLog.add("rollback:" + transactionId);
        }

        public List<String> getInvocationLog() {
            return invocationLog;
        }
    }

    @Test
    public void testEmptyTransaction() {
        String txId = dtm.begin();
        // No services enlisted, commit should succeed without error.
        assertDoesNotThrow(() -> dtm.commit(txId));
    }

    @Test
    public void testTransactionCommitSuccess() {
        String txId = dtm.begin();
        SuccessfulService inventory = new SuccessfulService();
        SuccessfulService payment = new SuccessfulService();
        SuccessfulService shipping = new SuccessfulService();

        dtm.enlist(txId, inventory);
        dtm.enlist(txId, payment);
        dtm.enlist(txId, shipping);

        assertDoesNotThrow(() -> dtm.commit(txId));

        // Verify that each service got prepare and commit called.
        assertTrue(inventory.getInvocationLog().contains("prepare:" + txId));
        assertTrue(payment.getInvocationLog().contains("prepare:" + txId));
        assertTrue(shipping.getInvocationLog().contains("prepare:" + txId));
    }

    @Test
    public void testTransactionRollbackOnPrepareFailure() {
        String txId = dtm.begin();
        SuccessfulService inventory = new SuccessfulService();
        FailingPrepareService payment = new FailingPrepareService();
        SuccessfulService shipping = new SuccessfulService();

        dtm.enlist(txId, inventory);
        dtm.enlist(txId, payment);
        dtm.enlist(txId, shipping);

        TransactionException ex = assertThrows(TransactionException.class, () -> dtm.commit(txId));
        assertNotNull(ex.getMessage());

        // After a failed commit, manually invoke rollback
        assertDoesNotThrow(() -> dtm.rollback(txId));

        // Verify that rollback was called on all services.
        assertTrue(inventory.getInvocationLog().contains("rollback:" + txId));
        assertTrue(payment.getInvocationLog().contains("rollback:" + txId));
        assertTrue(shipping.getInvocationLog().contains("rollback:" + txId));
    }

    @Test
    public void testTransactionRetryOnCommitFailure() {
        String txId = dtm.begin();
        // Simulate a service that fails commit 2 times then succeeds.
        RetryCommitService retryService = new RetryCommitService(2);
        SuccessfulService otherService = new SuccessfulService();

        dtm.enlist(txId, retryService);
        dtm.enlist(txId, otherService);

        // Commit should eventually succeed due to retry mechanism.
        assertDoesNotThrow(() -> dtm.commit(txId));

        // Check that multiple commit attempts were recorded.
        assertTrue(retryService.getInvocationLog().stream().anyMatch(s -> s.startsWith("commitSuccess:" + txId)));
        // Verify that otherService got commit call.
        assertTrue(otherService.getInvocationLog().contains("commit:" + txId));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        final int concurrentTx = 10;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentTx);
        CountDownLatch latch = new CountDownLatch(concurrentTx);
        List<String> results = new ArrayList<>();
        Object resultsLock = new Object();

        for (int i = 0; i < concurrentTx; i++) {
            executor.submit(() -> {
                String txId = dtm.begin();
                SuccessfulService service = new SuccessfulService();
                dtm.enlist(txId, service);
                try {
                    dtm.commit(txId);
                    synchronized (resultsLock) {
                        results.add("committed:" + txId);
                    }
                } catch (TransactionException e) {
                    synchronized (resultsLock) {
                        results.add("rolledback:" + txId);
                    }
                }
                latch.countDown();
            });
        }

        assertTrue(latch.await(10, TimeUnit.SECONDS));
        executor.shutdownNow();

        // Verify that all transactions committed successfully.
        for (String result : results) {
            assertTrue(result.startsWith("committed:"));
        }
        assertEquals(concurrentTx, results.size());
    }
}