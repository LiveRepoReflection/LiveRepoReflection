import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import static org.junit.jupiter.api.Assertions.*;

public class TransactionManagerTest {

    private TransactionManager tm;

    @BeforeEach
    public void setup() {
        tm = new TransactionManager();
    }

    @Test
    public void testBeginTransactionSuccess() {
        Set<Integer> services = new HashSet<>(Arrays.asList(0, 1, 2));
        boolean started = tm.beginTransaction(1, services);
        assertTrue(started, "Transaction should be started successfully");
    }

    @Test
    public void testBeginTransactionDuplicate() {
        Set<Integer> services = new HashSet<>(Arrays.asList(0, 1));
        boolean firstAttempt = tm.beginTransaction(2, services);
        boolean secondAttempt = tm.beginTransaction(2, services);
        assertTrue(firstAttempt, "First transaction start should succeed");
        assertFalse(secondAttempt, "Second transaction with duplicate ID should fail");
    }

    @Test
    public void testCommitTransactionSuccess() {
        Set<Integer> services = new HashSet<>(Arrays.asList(1, 2, 3));
        int txnId = 100;
        assertTrue(tm.beginTransaction(txnId, services), "Transaction should be started");
        // All services prepare successfully
        for (Integer serviceId : services) {
            boolean prepared = tm.prepare(txnId, serviceId);
            assertTrue(prepared, "Service " + serviceId + " should prepare successfully");
        }
        boolean commitResult = tm.commitTransaction(txnId);
        assertTrue(commitResult, "Commit should succeed if all services prepared");
        assertTrue(tm.isTransactionSuccessful(txnId), "Transaction state should be successful");
    }

    @Test
    public void testCommitTransactionFailureDueToMissingPrepare() {
        Set<Integer> services = new HashSet<>(Arrays.asList(4, 5, 6));
        int txnId = 200;
        assertTrue(tm.beginTransaction(txnId, services), "Transaction should be started");
        // Only prepare for some of the services
        boolean prepared1 = tm.prepare(txnId, 4);
        boolean prepared2 = tm.prepare(txnId, 5);
        assertTrue(prepared1, "Service 4 should prepare successfully");
        assertTrue(prepared2, "Service 5 should prepare successfully");
        // Service 6 did not prepare, simulating a refusal or missing prepare call.
        boolean commitResult = tm.commitTransaction(txnId);
        assertFalse(commitResult, "Commit should fail if any service did not prepare");
        assertFalse(tm.isTransactionSuccessful(txnId), "Transaction should not be successful");
    }

    @Test
    public void testRollbackTransactionSuccess() {
        Set<Integer> services = new HashSet<>(Arrays.asList(7, 8));
        int txnId = 300;
        assertTrue(tm.beginTransaction(txnId, services), "Transaction should be started");
        // Even if prepare is called, a rollback should mark the transaction as failed.
        for (Integer serviceId : services) {
            boolean prepared = tm.prepare(txnId, serviceId);
            assertTrue(prepared, "Service " + serviceId + " should prepare successfully");
        }
        boolean rollbackResult = tm.rollbackTransaction(txnId);
        assertTrue(rollbackResult, "Rollback should succeed");
        assertFalse(tm.isTransactionSuccessful(txnId), "Transaction state should be not successful after rollback");
    }

    @Test
    public void testRollbackNonExistentTransaction() {
        int txnId = 400;
        boolean rollbackResult = tm.rollbackTransaction(txnId);
        assertFalse(rollbackResult, "Rollback should fail for non-existent transaction");
    }

    @Test
    @Timeout(5)
    public void testConcurrentAccess() throws InterruptedException {
        int numberOfThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numberOfThreads);
        final int txnId = 500;
        Set<Integer> services = new HashSet<>();
        // Create 20 services for this transaction.
        for (int i = 0; i < 20; i++) {
            services.add(i);
        }
        // Begin transaction before concurrent access.
        assertTrue(tm.beginTransaction(txnId, services), "Transaction should be initiated for concurrent test");

        CountDownLatch latch = new CountDownLatch(services.size());
        // Concurrently call prepare on each service.
        for (Integer serviceId : services) {
            executor.execute(() -> {
                boolean result = tm.prepare(txnId, serviceId);
                assertTrue(result, "Service " + serviceId + " should prepare successfully in concurrent access");
                latch.countDown();
            });
        }
        latch.await();
        // Now commit concurrently in a single thread.
        boolean commitResult = tm.commitTransaction(txnId);
        assertTrue(commitResult, "Commit should succeed after all prepares in concurrent scenario");
        assertTrue(tm.isTransactionSuccessful(txnId), "Transaction should be successful after commit");
        executor.shutdown();
    }
}