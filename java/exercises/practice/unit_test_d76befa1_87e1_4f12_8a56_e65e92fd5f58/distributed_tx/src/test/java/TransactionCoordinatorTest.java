import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

// Assuming that the following classes/interfaces exist in the project:
// - Service
// - TransactionCoordinator
// - TransactionContext

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new TransactionCoordinator();
    }

    // Dummy service that always succeeds in prepare, commit, rollback.
    private static class SuccessfulService implements Service {
        public final AtomicInteger prepareCount = new AtomicInteger(0);
        public final AtomicInteger commitCount = new AtomicInteger(0);
        public final AtomicInteger rollbackCount = new AtomicInteger(0);

        @Override
        public boolean prepare(TransactionContext context) {
            prepareCount.incrementAndGet();
            return true;
        }

        @Override
        public void commit(TransactionContext context) {
            commitCount.incrementAndGet();
        }

        @Override
        public void rollback(TransactionContext context) {
            rollbackCount.incrementAndGet();
        }
    }

    // Dummy service that fails during prepare.
    private static class FailingPrepareService implements Service {
        public final AtomicInteger prepareCount = new AtomicInteger(0);
        public final AtomicInteger rollbackCount = new AtomicInteger(0);

        @Override
        public boolean prepare(TransactionContext context) {
            prepareCount.incrementAndGet();
            return false;
        }

        @Override
        public void commit(TransactionContext context) {
            // not called in failure scenario
        }

        @Override
        public void rollback(TransactionContext context) {
            rollbackCount.incrementAndGet();
        }
    }

    // Dummy service that fails commit on first attempt then succeeds.
    private static class FlakyCommitService implements Service {
        public final AtomicInteger prepareCount = new AtomicInteger(0);
        public final AtomicInteger commitCount = new AtomicInteger(0);
        public final AtomicInteger rollbackCount = new AtomicInteger(0);
        private final AtomicInteger commitFailures = new AtomicInteger(0);

        @Override
        public boolean prepare(TransactionContext context) {
            prepareCount.incrementAndGet();
            return true;
        }

        @Override
        public void commit(TransactionContext context) {
            // Fail first two attempts before succeeding
            if (commitFailures.getAndIncrement() < 2) {
                throw new RuntimeException("Commit failure simulated.");
            }
            commitCount.incrementAndGet();
        }

        @Override
        public void rollback(TransactionContext context) {
            rollbackCount.incrementAndGet();
        }
    }

    // Dummy service that fails rollback on first attempt then succeeds.
    private static class FlakyRollbackService implements Service {
        public final AtomicInteger prepareCount = new AtomicInteger(0);
        public final AtomicInteger commitCount = new AtomicInteger(0);
        public final AtomicInteger rollbackCount = new AtomicInteger(0);
        private final AtomicInteger rollbackFailures = new AtomicInteger(0);

        @Override
        public boolean prepare(TransactionContext context) {
            prepareCount.incrementAndGet();
            return false; // force rollback
        }

        @Override
        public void commit(TransactionContext context) {
            // Not expected to be called
        }

        @Override
        public void rollback(TransactionContext context) {
            // Fail first two attempts before succeeding
            if (rollbackFailures.getAndIncrement() < 2) {
                throw new RuntimeException("Rollback failure simulated.");
            }
            rollbackCount.incrementAndGet();
        }
    }

    // Dummy service that simulates a hanging prepare to cause timeout.
    private static class TimeoutPrepareService implements Service {
        public final AtomicInteger prepareCount = new AtomicInteger(0);
        public final AtomicInteger rollbackCount = new AtomicInteger(0);

        @Override
        public boolean prepare(TransactionContext context) {
            prepareCount.incrementAndGet();
            try {
                Thread.sleep(6000); // Sleep for 6 seconds to force timeout (assuming timeout is 5 seconds)
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }

        @Override
        public void commit(TransactionContext context) {
            // Not expected to be called
        }

        @Override
        public void rollback(TransactionContext context) {
            rollbackCount.incrementAndGet();
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        SuccessfulService service1 = new SuccessfulService();
        SuccessfulService service2 = new SuccessfulService();
        List<Service> services = Arrays.asList(service1, service2);
        TransactionContext context = new TransactionContext(UUID.randomUUID().toString());

        // Invoke the 2PC commit procedure.
        assertDoesNotThrow(() -> coordinator.commit(services, context));

        // Verify that prepare and commit have been called exactly once per service.
        assertEquals(1, service1.prepareCount.get());
        assertEquals(1, service2.prepareCount.get());
        assertEquals(1, service1.commitCount.get());
        assertEquals(1, service2.commitCount.get());
    }

    @Test
    public void testFailureDuringPrepare() {
        SuccessfulService service1 = new SuccessfulService();
        FailingPrepareService service2 = new FailingPrepareService();
        List<Service> services = Arrays.asList(service1, service2);
        TransactionContext context = new TransactionContext(UUID.randomUUID().toString());

        // When one service fails in prepare, the coordinator should trigger rollback
        Exception exception = assertThrows(RuntimeException.class, () -> coordinator.commit(services, context));
        // Check that rollback is invoked on both services.
        assertEquals(1, service2.prepareCount.get());
        assertTrue(service2.rollbackCount.get() >= 1);
        assertTrue(service1.rollbackCount.get() >= 1);
    }

    @Test
    public void testCommitRetry() {
        FlakyCommitService flakyService = new FlakyCommitService();
        SuccessfulService service = new SuccessfulService();
        List<Service> services = Arrays.asList(flakyService, service);
        TransactionContext context = new TransactionContext(UUID.randomUUID().toString());

        // The coordinator should retry commit for flakyService until it succeeds.
        assertDoesNotThrow(() -> coordinator.commit(services, context));

        // Commit should eventually succeed for flakyService and service.
        // flakyService's commitCount should be 1 even though commitFailures > 0.
        assertTrue(flakyService.commitFailures.get() >= 2);
        assertEquals(1, flakyService.commitCount.get());
        assertEquals(1, service.commitCount.get());
    }

    @Test
    public void testRollbackRetry() {
        FlakyRollbackService flakyRollbackService = new FlakyRollbackService();
        SuccessfulService service = new SuccessfulService();
        List<Service> services = Arrays.asList(flakyRollbackService, service);
        TransactionContext context = new TransactionContext(UUID.randomUUID().toString());

        // Since one service fails prepare, transaction should be rolled back.
        Exception exception = assertThrows(RuntimeException.class, () -> coordinator.commit(services, context));
        // Coordinator should retry rollback until success.
        assertTrue(flakyRollbackService.rollbackFailures.get() >= 2);
        assertEquals(1, flakyRollbackService.rollbackCount.get());
        // Verify that the successful service's rollback has been called.
        assertEquals(1, service.rollbackCount.get());
    }

    @Test
    @Timeout(10)
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int concurrentTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentTransactions);
        List<Future<Void>> futures = new ArrayList<>();
        for (int i = 0; i < concurrentTransactions; i++) {
            futures.add(executor.submit(() -> {
                SuccessfulService service1 = new SuccessfulService();
                SuccessfulService service2 = new SuccessfulService();
                List<Service> services = Arrays.asList(service1, service2);
                TransactionContext context = new TransactionContext(UUID.randomUUID().toString());
                coordinator.commit(services, context);
                // Validate that commit succeeded for each service.
                assertEquals(1, service1.commitCount.get());
                assertEquals(1, service2.commitCount.get());
                return null;
            }));
        }

        for (Future<Void> future : futures) {
            future.get();
        }
        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
    }

    @Test
    public void testTimeoutPrepare() {
        TimeoutPrepareService timeoutService = new TimeoutPrepareService();
        SuccessfulService service = new SuccessfulService();
        List<Service> services = Arrays.asList(timeoutService, service);
        TransactionContext context = new TransactionContext(UUID.randomUUID().toString());

        // The prepare call for timeoutService will exceed the allowed time (assumed 5 seconds)
        Exception exception = assertThrows(RuntimeException.class, () -> coordinator.commit(services, context));

        // Verify that after timeout the coordinator attempted to rollback.
        assertTrue(timeoutService.rollbackCount.get() >= 1);
        // The normal service should have received rollback as well.
        assertTrue(service.rollbackCount.get() >= 1);
    }
}