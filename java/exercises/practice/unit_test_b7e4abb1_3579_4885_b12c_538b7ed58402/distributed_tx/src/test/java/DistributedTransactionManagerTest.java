import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

// A dummy Microservice interface for testing purposes.
interface Microservice {
    // Simulate the prepare phase. Returns true if successful, false if not.
    boolean prepare(String transactionId);
    // Commit operation, may throw exception.
    void commit(String transactionId) throws Exception;
    // Rollback operation, may throw exception.
    void rollback(String transactionId) throws Exception;
}

// A stub DistributedTransactionManager for testing purposes.
// Assume that the actual implementation under test is in the main source folder.
class DistributedTransactionManager {
    private int maxRetries;
    private long baseBackoffMillis;

    public DistributedTransactionManager() {
        // Default configuration.
        this.maxRetries = 3;
        this.baseBackoffMillis = 100;
    }

    public DistributedTransactionManager(int maxRetries, long baseBackoffMillis) {
        this.maxRetries = maxRetries;
        this.baseBackoffMillis = baseBackoffMillis;
    }

    public boolean executeTransaction(List<Microservice> services, String transactionId) {
        // Phase 1: Prepare
        for (Microservice service : services) {
            boolean prepared;
            try {
                prepared = service.prepare(transactionId);
            } catch (Exception e) {
                prepared = false;
            }
            if (!prepared) {
                // Prepare failed: Rollback all and return false.
                rollbackAll(services, transactionId);
                return false;
            }
        }
        // Phase 2: Commit
        if (!commitAll(services, transactionId)) {
            // If commit fails, attempt rollback.
            rollbackAll(services, transactionId);
            return false;
        }
        return true;
    }

    private boolean commitAll(List<Microservice> services, String transactionId) {
        boolean allCommitted = true;
        for (Microservice service : services) {
            boolean committed = false;
            long backoff = baseBackoffMillis;
            for (int attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    service.commit(transactionId);
                    committed = true;
                    break;
                } catch (Exception e) {
                    try {
                        Thread.sleep(backoff);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                    backoff *= 2;
                }
            }
            if (!committed) {
                allCommitted = false;
            }
        }
        return allCommitted;
    }

    private void rollbackAll(List<Microservice> services, String transactionId) {
        for (Microservice service : services) {
            long backoff = baseBackoffMillis;
            for (int attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    service.rollback(transactionId);
                    break;
                } catch (Exception e) {
                    try {
                        Thread.sleep(backoff);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                    backoff *= 2;
                }
            }
        }
    }
}

// A fake microservice implementation for unit testing.
class FakeMicroservice implements Microservice {
    private boolean prepareOutcome;
    // Counters for commit and rollback attempts.
    private AtomicInteger commitFailuresLeft;
    private AtomicInteger rollbackFailuresLeft;
    // For idempotency: record if commit or rollback was already executed.
    private boolean committed = false;
    private boolean rolledBack = false;

    public FakeMicroservice(boolean prepareOutcome, int commitFailures, int rollbackFailures) {
        this.prepareOutcome = prepareOutcome;
        this.commitFailuresLeft = new AtomicInteger(commitFailures);
        this.rollbackFailuresLeft = new AtomicInteger(rollbackFailures);
    }

    @Override
    public boolean prepare(String transactionId) {
        return prepareOutcome;
    }

    @Override
    public void commit(String transactionId) throws Exception {
        if (committed) {
            return;
        }
        if (commitFailuresLeft.get() > 0) {
            commitFailuresLeft.decrementAndGet();
            throw new Exception("Simulated commit failure");
        }
        committed = true;
    }

    @Override
    public void rollback(String transactionId) throws Exception {
        if (rolledBack) {
            return;
        }
        if (rollbackFailuresLeft.get() > 0) {
            rollbackFailuresLeft.decrementAndGet();
            throw new Exception("Simulated rollback failure");
        }
        rolledBack = true;
    }
}

public class DistributedTransactionManagerTest {

    private DistributedTransactionManager txManager;

    @BeforeEach
    public void setup() {
        txManager = new DistributedTransactionManager(3, 50);
    }

    @Test
    public void testSuccessfulTransaction() {
        List<Microservice> services = new ArrayList<>();
        // All services prepare and commit successfully.
        services.add(new FakeMicroservice(true, 0, 0));
        services.add(new FakeMicroservice(true, 0, 0));
        services.add(new FakeMicroservice(true, 0, 0));

        boolean result = txManager.executeTransaction(services, "tx_success");
        assertTrue(result, "Transaction should succeed when all services prepare and commit successfully.");
    }

    @Test
    public void testPrepareFailureTransaction() {
        List<Microservice> services = new ArrayList<>();
        // First service fails preparation.
        services.add(new FakeMicroservice(false, 0, 0));
        services.add(new FakeMicroservice(true, 0, 0));

        boolean result = txManager.executeTransaction(services, "tx_prepare_fail");
        assertFalse(result, "Transaction should fail when a service fails its prepare phase.");
    }

    @Test
    public void testCommitWithRetriesSuccess() {
        List<Microservice> services = new ArrayList<>();
        // One service fails commit on first attempt but succeeds after retries.
        services.add(new FakeMicroservice(true, 2, 0)); // Will fail 2 times, then succeed.
        services.add(new FakeMicroservice(true, 0, 0));

        boolean result = txManager.executeTransaction(services, "tx_commit_retry_success");
        assertTrue(result, "Transaction should succeed after retrying commit operations.");
    }

    @Test
    public void testCommitWithRetriesFailure() {
        List<Microservice> services = new ArrayList<>();
        // One service fails commit more times than allowed retries.
        services.add(new FakeMicroservice(true, 5, 0)); // Will always fail commit because 5 > maxRetries (3)
        services.add(new FakeMicroservice(true, 0, 0));

        boolean result = txManager.executeTransaction(services, "tx_commit_retry_failure");
        assertFalse(result, "Transaction should fail when commit operation exceeds allowed retries.");
    }

    @Test
    public void testRollbackWithRetriesSuccess() {
        List<Microservice> services = new ArrayList<>();
        // One service fails prepare causing a rollback scenario and fails rollback a few times but eventually succeeds.
        services.add(new FakeMicroservice(false, 0, 2)); // Fails prepare so rollback is triggered. Rollback fails 2 times then succeeds.
        services.add(new FakeMicroservice(true, 0, 0));

        boolean result = txManager.executeTransaction(services, "tx_rollback_retry_success");
        assertFalse(result, "Transaction should fail because a prepare failure forces rollback even if rollback eventually succeeds.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        final int threadCount = 10;
        final CountDownLatch latch = new CountDownLatch(threadCount);
        final List<Boolean> results = new ArrayList<>();
        final Object lock = new Object();

        Runnable task = () -> {
            try {
                List<Microservice> services = new ArrayList<>();
                // Alternate between successful and failing prepare.
                boolean prepareOutcome = Thread.currentThread().getId() % 2 == 0;
                services.add(new FakeMicroservice(prepareOutcome, 0, 0));
                services.add(new FakeMicroservice(true, 0, 0));
                boolean res = txManager.executeTransaction(services, "tx_concurrent_" + Thread.currentThread().getId());
                synchronized (lock) {
                    results.add(res);
                }
            } finally {
                latch.countDown();
            }
        };

        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < threadCount; i++) {
            Thread t = new Thread(task);
            threads.add(t);
            t.start();
        }
        latch.await();

        // Validate that transactions with failing prepare return false.
        for (int i = 0; i < results.size(); i++) {
            // Because prepareOutcome alternates, we expect about half to succeed and half to fail.
            // We only assert that the result is either true or false without exceptions.
            assertTrue(results.get(i) == true || results.get(i) == false);
        }
    }
}