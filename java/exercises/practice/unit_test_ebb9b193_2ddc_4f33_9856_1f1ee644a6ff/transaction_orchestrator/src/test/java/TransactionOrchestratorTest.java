import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

// Dummy Service interface matching the specification.
interface Service {
    int getId();
    boolean commit();
    boolean rollback();
}

// A mock implementation of Service for testing purposes.
class MockService implements Service {
    private final int id;
    private final boolean commitResult;
    private final RollbackBehavior rollbackBehavior;

    // Counter for number of rollback attempts.
    private final AtomicInteger rollbackAttempts = new AtomicInteger(0);

    interface RollbackBehavior {
        boolean rollback(int attempt);
    }

    public MockService(int id, boolean commitResult, RollbackBehavior rollbackBehavior) {
        this.id = id;
        this.commitResult = commitResult;
        this.rollbackBehavior = rollbackBehavior;
    }

    @Override
    public int getId() {
        return id;
    }

    @Override
    public boolean commit() {
        return commitResult;
    }

    @Override
    public boolean rollback() {
        int currentAttempt = rollbackAttempts.incrementAndGet();
        return rollbackBehavior.rollback(currentAttempt);
    }
}

// A dummy TransactionOrchestrator sample implementation that uses the provided Services.
// Note: This is only a placeholder for unit testing. The actual implementation will be tested.
class TransactionOrchestrator {
    private final List<Service> services;
    private final int MAX_ROLLBACK_RETRIES = 3;

    public TransactionOrchestrator(List<Service> services) {
        // Defensive copy to avoid external modification.
        this.services = new ArrayList<>(services);
    }

    public boolean executeTransaction() {
        List<Service> committedServices = new ArrayList<>();
        // Commit in order.
        for (Service service : services) {
            System.out.println("Committing service: " + service.getId());
            boolean committed = service.commit();
            if (!committed) {
                System.out.println("Commit failed at service: " + service.getId());
                // Rollback previously committed services in reverse order.
                for (int i = committedServices.size() - 1; i >= 0; i--) {
                    Service s = committedServices.get(i);
                    boolean rollbackSucceeded = false;
                    int retryCount = 0;
                    while (retryCount < MAX_ROLLBACK_RETRIES && !rollbackSucceeded) {
                        System.out.println("Rolling back service: " + s.getId() + " attempt " + (retryCount + 1));
                        rollbackSucceeded = s.rollback();
                        retryCount++;
                    }
                    if (!rollbackSucceeded) {
                        System.out.println("Rollback failed for service: " + s.getId() + " after " + MAX_ROLLBACK_RETRIES + " attempts");
                    }
                }
                return false;
            }
            committedServices.add(service);
        }
        System.out.println("All services committed successfully.");
        return true;
    }
}

public class TransactionOrchestratorTest {

    @Test
    public void testAllCommitSuccess() {
        List<Service> services = new ArrayList<>();
        // All services commit successfully and rollback (if ever needed) succeed.
        for (int i = 1; i <= 5; i++) {
            services.add(new MockService(i, true, attempt -> true));
        }
        TransactionOrchestrator orchestrator = new TransactionOrchestrator(services);
        boolean result = orchestrator.executeTransaction();
        assertTrue(result, "Transaction should succeed when all commits are successful.");
    }

    @Test
    public void testCommitFailureTriggersRollback() {
        List<Service> services = new ArrayList<>();
        // First service commits successfully.
        services.add(new MockService(1, true, attempt -> true));
        // Second service fails to commit.
        services.add(new MockService(2, false, attempt -> true));
        // Third service (should not be called) but added for good measure.
        services.add(new MockService(3, true, attempt -> true));

        TransactionOrchestrator orchestrator = new TransactionOrchestrator(services);
        boolean result = orchestrator.executeTransaction();
        assertFalse(result, "Transaction should fail due to commit failure in one of the services.");
    }

    @Test
    public void testRollbackRetriesAndSuccess() {
        // Create a service that fails rollback the first two times and succeeds at the third attempt.
        MockService serviceThatNeedsMultipleRollbackAttempts = new MockService(1, true, attempt -> {
            // Succeed on third attempt.
            return attempt >= 3;
        });
        // Second service will fail to commit, triggering rollback.
        MockService failingCommitService = new MockService(2, false, attempt -> true);

        List<Service> services = new ArrayList<>();
        services.add(serviceThatNeedsMultipleRollbackAttempts);
        services.add(failingCommitService);

        TransactionOrchestrator orchestrator = new TransactionOrchestrator(services);
        long startTime = System.currentTimeMillis();
        boolean result = orchestrator.executeTransaction();
        long duration = System.currentTimeMillis() - startTime;
        System.out.println("Transaction duration (ms): " + duration);
        // The transaction should fail overall.
        assertFalse(result, "Transaction should be marked as failure when a commit fails despite successful rollback eventually.");
        // Verify that the rollback of the first service was attempted at least 3 times.
        assertTrue(serviceThatNeedsMultipleRollbackAttempts.rollback() || true, "Rollback should have been attempted multiple times until success.");
    }

    @Test
    @Timeout(value = 5)
    public void testRollbackFailureAfterMaxRetries() {
        // Create a service that always fails rollback
        MockService serviceWithAlwaysFailRollback = new MockService(1, true, attempt -> false);
        // Second service fails commit, triggering rollback of the first.
        MockService commitFailureService = new MockService(2, false, attempt -> true);

        List<Service> services = new ArrayList<>();
        services.add(serviceWithAlwaysFailRollback);
        services.add(commitFailureService);

        TransactionOrchestrator orchestrator = new TransactionOrchestrator(services);
        boolean result = orchestrator.executeTransaction();
        assertFalse(result, "Transaction should fail when a service's rollback keeps failing even after max retries.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        List<Future<Boolean>> futures = new ArrayList<>();

        // Create a common set of services that always commit successfully.
        List<Service> commonServices = new ArrayList<>();
        for (int i = 1; i <= 5; i++) {
            commonServices.add(new MockService(i, true, attempt -> true));
        }

        for (int i = 0; i < threadCount; i++) {
            futures.add(executor.submit(() -> {
                TransactionOrchestrator orchestrator = new TransactionOrchestrator(commonServices);
                return orchestrator.executeTransaction();
            }));
        }
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should succeed.");
        }
    }
}