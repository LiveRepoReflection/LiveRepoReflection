package tx_coordinator;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;
    // Using a short timeout for test purposes (in milliseconds)
    private static final long TIMEOUT_MS = 500;

    @BeforeEach
    public void setUp() {
        // Initialize the coordinator and configure its timeout value.
        coordinator = new TransactionCoordinator();
        coordinator.setTimeout(TIMEOUT_MS);
    }

    @AfterEach
    public void tearDown() {
        coordinator.shutdown();
    }

    // Dummy implementation of the Service interface for testing purposes.
    private static class TestService implements Service {
        private final String serviceId;
        private final boolean failOnPrepare;
        private final boolean simulateDelay;
        private final long delayMillis;
        public final List<String> actionLog = new ArrayList<>();

        public TestService(String serviceId, boolean failOnPrepare, boolean simulateDelay, long delayMillis) {
            this.serviceId = serviceId;
            this.failOnPrepare = failOnPrepare;
            this.simulateDelay = simulateDelay;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String transactionId) {
            if (simulateDelay) {
                try {
                    // Delay is longer than the coordinator timeout to simulate a timeout.
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            actionLog.add("prepare:" + transactionId);
            return !failOnPrepare;
        }

        @Override
        public void commit(String transactionId) {
            actionLog.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            actionLog.add("rollback:" + transactionId);
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        String transactionId = "tx-success";
        TestService serviceA = new TestService("A", false, false, 0);
        TestService serviceB = new TestService("B", false, false, 0);

        coordinator.registerService("A", serviceA);
        coordinator.registerService("B", serviceB);

        List<String> participants = Arrays.asList("A", "B");
        TransactionStatus result = coordinator.initiateTransaction(transactionId, participants);

        // Expect the transaction to be committed
        assertEquals(TransactionStatus.COMMITTED, result);

        // Verify that each service got prepared and committed.
        assertTrue(serviceA.actionLog.contains("prepare:" + transactionId));
        assertTrue(serviceA.actionLog.contains("commit:" + transactionId));

        assertTrue(serviceB.actionLog.contains("prepare:" + transactionId));
        assertTrue(serviceB.actionLog.contains("commit:" + transactionId));
    }

    @Test
    public void testRollbackWhenPrepareFails() {
        String transactionId = "tx-rollback";
        // Service A succeeds; Service B fails during prepare.
        TestService serviceA = new TestService("A", false, false, 0);
        TestService serviceB = new TestService("B", true, false, 0);

        coordinator.registerService("A", serviceA);
        coordinator.registerService("B", serviceB);

        List<String> participants = Arrays.asList("A", "B");
        TransactionStatus result = coordinator.initiateTransaction(transactionId, participants);

        // Expect the transaction to be rolled back
        assertEquals(TransactionStatus.ROLLED_BACK, result);

        // Both services should have prepared; however, rollback should be called.
        assertTrue(serviceA.actionLog.contains("prepare:" + transactionId));
        assertTrue(serviceA.actionLog.contains("rollback:" + transactionId));

        assertTrue(serviceB.actionLog.contains("prepare:" + transactionId));
        assertTrue(serviceB.actionLog.contains("rollback:" + transactionId));
    }

    @Test
    public void testTimeoutTriggersRollback() {
        String transactionId = "tx-timeout";
        // Service A responds normally; Service B simulates a delay to trigger timeout.
        TestService serviceA = new TestService("A", false, false, 0);
        // Delay is set to be longer than coordinator timeout.
        TestService serviceB = new TestService("B", false, true, TIMEOUT_MS + 500);

        coordinator.registerService("A", serviceA);
        coordinator.registerService("B", serviceB);

        List<String> participants = Arrays.asList("A", "B");
        TransactionStatus result = coordinator.initiateTransaction(transactionId, participants);

        // Expect the transaction to be rolled back due to timeout.
        assertEquals(TransactionStatus.ROLLED_BACK, result);

        // Verify that rollback was triggered.
        assertTrue(serviceA.actionLog.contains("prepare:" + transactionId));
        assertTrue(serviceA.actionLog.contains("rollback:" + transactionId));

        // Service B may not have completed prepare if timed out.
        // Depending on implementation, it might record a prepare or not.
        assertTrue(serviceB.actionLog.contains("rollback:" + transactionId));
    }

    @Test
    public void testIdempotencyOfPrepareCommitRollback() {
        String transactionId = "tx-idempotent";
        TestService serviceA = new TestService("A", false, false, 0);

        coordinator.registerService("A", serviceA);

        List<String> participants = Collections.singletonList("A");
        TransactionStatus firstResult = coordinator.initiateTransaction(transactionId, participants);
        // First transaction should commit successfully.
        assertEquals(TransactionStatus.COMMITTED, firstResult);

        // Invoke the same transaction again; idempotency should ensure no duplicate calls are made.
        TransactionStatus secondResult = coordinator.initiateTransaction(transactionId, participants);
        assertEquals(TransactionStatus.COMMITTED, secondResult);

        // Count occurrences to check idempotency. Only one prepare and one commit per service.
        long prepareCount = serviceA.actionLog.stream().filter(s -> s.equals("prepare:" + transactionId)).count();
        long commitCount = serviceA.actionLog.stream().filter(s -> s.equals("commit:" + transactionId)).count();

        assertEquals(1, prepareCount);
        assertEquals(1, commitCount);
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int transactionCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(4);
        CountDownLatch latch = new CountDownLatch(transactionCount);

        List<TransactionStatus> results = Collections.synchronizedList(new ArrayList<>());

        // Register two services that always succeed.
        TestService serviceA = new TestService("A", false, false, 0);
        TestService serviceB = new TestService("B", false, false, 0);
        coordinator.registerService("A", serviceA);
        coordinator.registerService("B", serviceB);

        for (int i = 0; i < transactionCount; i++) {
            final int txNum = i;
            executor.submit(() -> {
                String txId = "tx-concurrent-" + txNum;
                List<String> participants = Arrays.asList("A", "B");
                TransactionStatus status = coordinator.initiateTransaction(txId, participants);
                results.add(status);
                latch.countDown();
            });
        }
        // Wait for all transactions to complete.
        boolean completed = latch.await(5, TimeUnit.SECONDS);
        executor.shutdownNow();
        assertTrue(completed);

        // All transactions should commit.
        for (TransactionStatus status : results) {
            assertEquals(TransactionStatus.COMMITTED, status);
        }
    }
}