import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class TransactionCoordinatorTest {
    private TransactionCoordinator coordinator;
    private List<Microservice> microservices;
    private static final int RETRY_ATTEMPTS = 3;

    @BeforeEach
    void setUp() {
        coordinator = new TransactionCoordinator(RETRY_ATTEMPTS);
        microservices = new ArrayList<>();
    }

    @Test
    void testSuccessfulTransaction() {
        Microservice successfulService = new TestMicroservice(true, false);
        microservices.add(successfulService);
        
        TransactionContext context = coordinator.begin();
        microservices.forEach(ms -> coordinator.enlist(ms));
        
        assertTrue(coordinator.prepareTransaction(context));
        assertTrue(coordinator.commitTransaction(context));
    }

    @Test
    void testFailedPreparePhase() {
        Microservice failingService = new TestMicroservice(false, false);
        microservices.add(failingService);
        
        TransactionContext context = coordinator.begin();
        microservices.forEach(ms -> coordinator.enlist(ms));
        
        assertFalse(coordinator.prepareTransaction(context));
        assertTrue(coordinator.rollbackTransaction(context));
    }

    @Test
    void testPartialFailureWithRetries() {
        AtomicBoolean shouldFail = new AtomicBoolean(true);
        Microservice flakyService = new TestMicroservice(true, false) {
            @Override
            public boolean prepare(TransactionContext context) {
                if (shouldFail.getAndSet(false)) {
                    throw new RuntimeException("Temporary failure");
                }
                return true;
            }
        };
        microservices.add(flakyService);
        
        TransactionContext context = coordinator.begin();
        microservices.forEach(ms -> coordinator.enlist(ms));
        
        assertTrue(coordinator.prepareTransaction(context));
        assertTrue(coordinator.commitTransaction(context));
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException {
        Microservice service = new TestMicroservice(true, false);
        microservices.add(service);
        
        Thread t1 = new Thread(() -> {
            TransactionContext context = coordinator.begin();
            microservices.forEach(ms -> coordinator.enlist(ms));
            assertTrue(coordinator.prepareTransaction(context));
            assertTrue(coordinator.commitTransaction(context));
        });
        
        Thread t2 = new Thread(() -> {
            TransactionContext context = coordinator.begin();
            microservices.forEach(ms -> coordinator.enlist(ms));
            assertTrue(coordinator.prepareTransaction(context));
            assertTrue(coordinator.commitTransaction(context));
        });
        
        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }

    @Test
    void testIdempotentCommit() {
        Microservice service = new TestMicroservice(true, false);
        microservices.add(service);
        
        TransactionContext context = coordinator.begin();
        microservices.forEach(ms -> coordinator.enlist(ms));
        
        assertTrue(coordinator.prepareTransaction(context));
        assertTrue(coordinator.commitTransaction(context));
        assertTrue(coordinator.commitTransaction(context)); // Second commit should be harmless
    }

    private static class TestMicroservice implements Microservice {
        private final boolean shouldPrepare;
        private final boolean shouldFailCommit;
        
        public TestMicroservice(boolean shouldPrepare, boolean shouldFailCommit) {
            this.shouldPrepare = shouldPrepare;
            this.shouldFailCommit = shouldFailCommit;
        }
        
        @Override
        public boolean prepare(TransactionContext context) {
            return shouldPrepare;
        }
        
        @Override
        public void commit(TransactionContext context) {
            if (shouldFailCommit) {
                throw new RuntimeException("Commit failed");
            }
        }
        
        @Override
        public void rollback(TransactionContext context) {
            // No-op for testing
        }
    }
}