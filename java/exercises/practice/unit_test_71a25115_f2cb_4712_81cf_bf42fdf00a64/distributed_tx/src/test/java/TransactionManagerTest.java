import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;

import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

// The following tests assume that TransactionManager and Service interfaces/classes
// have been implemented in the main source tree. The Service interface is assumed to have the following methods:
//   boolean prepare(String transactionId) throws Exception;
//   void commit(String transactionId) throws Exception;
//   void rollback(String transactionId) throws Exception;
// And the TransactionManager is assumed to provide:
//   TransactionManager(long timeoutMillis, int maxCommitRetries)
//   void registerService(String serviceName, Service service)
//   String begin()
//   boolean commitTransaction(String transactionId)
//   void rollbackTransaction(String transactionId)

public class TransactionManagerTest {

    // Dummy implementation of the Service interface for testing purposes.
    static class DummyService implements Service {
        String name;
        boolean prepareResult;
        volatile boolean prepareCalled = false;
        volatile boolean commitCalled = false;
        volatile boolean rollbackCalled = false;
        int commitAttempts = 0;
        int failCommitAttempts; // number of initial commit attempts that should fail
        long delayMillis; // artificial delay to simulate timeout behavior

        public DummyService(String name, boolean prepareResult) {
            this(name, prepareResult, 0, 0);
        }

        public DummyService(String name, boolean prepareResult, int failCommitAttempts, long delayMillis) {
            this.name = name;
            this.prepareResult = prepareResult;
            this.failCommitAttempts = failCommitAttempts;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String transactionId) throws Exception {
            if (delayMillis > 0) {
                Thread.sleep(delayMillis);
            }
            prepareCalled = true;
            return prepareResult;
        }

        @Override
        public void commit(String transactionId) throws Exception {
            if (delayMillis > 0) {
                Thread.sleep(delayMillis);
            }
            commitAttempts++;
            if (commitAttempts <= failCommitAttempts) {
                throw new Exception("Commit failed for service: " + name);
            }
            commitCalled = true;
        }

        @Override
        public void rollback(String transactionId) throws Exception {
            if (delayMillis > 0) {
                Thread.sleep(delayMillis);
            }
            rollbackCalled = true;
        }
    }

    TransactionManager tm;

    @BeforeEach
    public void setUp() {
        // Initialize TransactionManager with a timeout of 2000ms and up to 3 commit retries.
        tm = new TransactionManager(2000, 3);
    }

    @AfterEach
    public void tearDown() {
        tm = null;
    }

    // Test that a transaction commits successfully when all services prepare and commit.
    @Test
    public void testSuccessfulTransaction() throws Exception {
        DummyService serviceA = new DummyService("A", true);
        DummyService serviceB = new DummyService("B", true);

        tm.registerService("A", serviceA);
        tm.registerService("B", serviceB);

        String txId = tm.begin();
        boolean result = tm.commitTransaction(txId);
        assertTrue(result, "Transaction should commit successfully");

        // Verify that prepare and commit were called for both services.
        assertTrue(serviceA.prepareCalled, "Service A should have executed prepare");
        assertTrue(serviceB.prepareCalled, "Service B should have executed prepare");
        assertTrue(serviceA.commitCalled, "Service A should have executed commit");
        assertTrue(serviceB.commitCalled, "Service B should have executed commit");
    }

    // Test that if any service fails during the prepare phase, the transaction is rolled back.
    @Test
    public void testPrepareFailure() throws Exception {
        DummyService serviceA = new DummyService("A", true);
        DummyService serviceB = new DummyService("B", false); // Fails during prepare

        tm.registerService("A", serviceA);
        tm.registerService("B", serviceB);

        String txId = tm.begin();
        boolean result = tm.commitTransaction(txId);
        assertFalse(result, "Transaction should fail due to prepare failure");

        // Prepare must have been called, but commit should not have been executed.
        assertTrue(serviceA.prepareCalled, "Service A should have executed prepare");
        assertTrue(serviceB.prepareCalled, "Service B should have executed prepare");
        assertFalse(serviceA.commitCalled, "Service A should not have executed commit");
        assertFalse(serviceB.commitCalled, "Service B should not have executed commit");

        // Both services should have attempted rollback.
        assertTrue(serviceA.rollbackCalled, "Service A should have executed rollback");
        assertTrue(serviceB.rollbackCalled, "Service B should have executed rollback");
    }

    // Test commit retries: one service fails commit initially but eventually commits after retries.
    @Test
    public void testCommitRetry() throws Exception {
        // Service A succeeds normally; Service B fails commit on the first two attempts.
        DummyService serviceA = new DummyService("A", true);
        DummyService serviceB = new DummyService("B", true, 2, 0);

        tm.registerService("A", serviceA);
        tm.registerService("B", serviceB);

        String txId = tm.begin();
        boolean result = tm.commitTransaction(txId);
        assertTrue(result, "Transaction should commit successfully after commit retries");

        // Service A should have committed successfully.
        assertTrue(serviceA.commitCalled, "Service A should have executed commit");
        // Service B should have attempted commit multiple times.
        assertTrue(serviceB.commitAttempts >= 3, "Service B should have attempted commit retries");
        assertTrue(serviceB.commitCalled, "Service B should eventually commit");
    }

    // Test that a service exceeding the timeout during prepare triggers a rollback.
    @Test
    public void testTimeoutOnPrepare() throws Exception {
        // Reinitialize the TransactionManager with a short timeout of 500ms.
        tm = new TransactionManager(500, 3);

        // Service A responds quickly; Service B delays to simulate timeout.
        DummyService serviceA = new DummyService("A", true);
        DummyService serviceB = new DummyService("B", true, 0, 1000);

        tm.registerService("A", serviceA);
        tm.registerService("B", serviceB);

        String txId = tm.begin();
        boolean result = tm.commitTransaction(txId);
        assertFalse(result, "Transaction should fail due to timeout");

        // At least Service A should attempt rollback.
        assertTrue(serviceA.rollbackCalled, "Service A should have executed rollback on timeout");
    }

    // Test idempotency: repeated commit or rollback calls should yield the same outcome.
    @Test
    public void testIdempotency() throws Exception {
        DummyService serviceA = new DummyService("A", true);
        tm.registerService("A", serviceA);

        String txId = tm.begin();
        boolean result = tm.commitTransaction(txId);
        assertTrue(result, "Transaction should commit successfully");

        // Repeating the commit should not change the state.
        boolean secondCommitResult = tm.commitTransaction(txId);
        assertTrue(secondCommitResult, "Repeated commit should be idempotent");

        // Repeating rollback should also be safe.
        tm.rollbackTransaction(txId);
        tm.rollbackTransaction(txId);

        // Service A should remain committed.
        assertTrue(serviceA.commitCalled, "Service A should remain committed after multiple rollback calls");
    }

    // Test concurrent transactions to ensure thread safety.
    @Test
    public void testConcurrentTransactions() throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        // Create 20 independent transactions running concurrently.
        for (int i = 0; i < 20; i++) {
            tasks.add(() -> {
                DummyService service1 = new DummyService("Service1", true);
                DummyService service2 = new DummyService("Service2", true);
                tm.registerService("Service1", service1);
                tm.registerService("Service2", service2);
                String txId = tm.begin();
                boolean res = tm.commitTransaction(txId);
                return res;
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully");
        }
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
    }
}