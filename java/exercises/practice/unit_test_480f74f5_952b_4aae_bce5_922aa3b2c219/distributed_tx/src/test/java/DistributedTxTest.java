import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTxTest {
    private TransactionManager tm;
    private Microservice mockService1;
    private Microservice mockService2;
    private Microservice failingService;
    private Microservice slowService;

    @BeforeEach
    public void setUp() {
        tm = new TransactionManager();
        mockService1 = new MockMicroservice();
        mockService2 = new MockMicroservice();
        failingService = new FailingMicroservice();
        slowService = new SlowMicroservice(3000); // 3 seconds delay
    }

    @Test
    public void testSuccessfulTransaction() {
        List<Integer> services = Arrays.asList(1, 2);
        List<List<Operation>> operations = Arrays.asList(
            Arrays.asList(new TestOperation("op1")),
            Arrays.asList(new TestOperation("op2"))
        );
        
        tm.registerMicroservice(1, mockService1);
        tm.registerMicroservice(2, mockService2);
        
        assertTrue(tm.executeTransaction(services, operations));
    }

    @Test
    public void testFailedPreparePhase() {
        List<Integer> services = Arrays.asList(1, 2);
        List<List<Operation>> operations = Arrays.asList(
            Arrays.asList(new TestOperation("op1")),
            Arrays.asList(new TestOperation("op2"))
        );
        
        tm.registerMicroservice(1, mockService1);
        tm.registerMicroservice(2, failingService);
        
        assertFalse(tm.executeTransaction(services, operations));
    }

    @Test
    public void testTimeoutDuringPrepare() {
        List<Integer> services = Arrays.asList(1, 2);
        List<List<Operation>> operations = Arrays.asList(
            Arrays.asList(new TestOperation("op1")),
            Arrays.asList(new TestOperation("op2"))
        );
        
        tm.registerMicroservice(1, mockService1);
        tm.registerMicroservice(2, slowService);
        
        long startTime = System.currentTimeMillis();
        assertFalse(tm.executeTransaction(services, operations));
        long duration = System.currentTimeMillis() - startTime;
        
        assertTrue(duration >= 2000 && duration < 4000); // Should timeout around 2 seconds
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        tm.registerMicroservice(1, mockService1);
        tm.registerMicroservice(2, mockService2);
        
        AtomicInteger successCount = new AtomicInteger(0);
        int threadCount = 10;
        Thread[] threads = new Thread[threadCount];
        
        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            threads[i] = new Thread(() -> {
                List<Integer> services = Arrays.asList(1, 2);
                List<List<Operation>> operations = Arrays.asList(
                    Arrays.asList(new TestOperation("op1-" + threadId)),
                    Arrays.asList(new TestOperation("op2-" + threadId))
                );
                
                if (tm.executeTransaction(services, operations)) {
                    successCount.incrementAndGet();
                }
            });
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        assertEquals(threadCount, successCount.get());
    }

    @Test
    public void testIdempotentCommit() {
        List<Integer> services = Arrays.asList(1);
        List<List<Operation>> operations = Arrays.asList(
            Arrays.asList(new TestOperation("op1"))
        );
        
        tm.registerMicroservice(1, mockService1);
        
        // First execution should succeed
        assertTrue(tm.executeTransaction(services, operations));
        
        // Second execution with same transaction ID should handle idempotency
        assertTrue(tm.executeTransaction(services, operations));
    }

    @Test
    public void testPartialFailureRecovery() {
        List<Integer> services = Arrays.asList(1, 2);
        List<List<Operation>> operations = Arrays.asList(
            Arrays.asList(new TestOperation("op1")),
            Arrays.asList(new TestOperation("op2"))
        );
        
        tm.registerMicroservice(1, mockService1);
        tm.registerMicroservice(2, new IntermittentFailingMicroservice());
        
        // First attempt might fail
        boolean firstAttempt = tm.executeTransaction(services, operations);
        
        // Second attempt should succeed
        boolean secondAttempt = tm.executeTransaction(services, operations);
        
        assertTrue(firstAttempt || secondAttempt);
    }

    private static class MockMicroservice implements Microservice {
        @Override
        public String prepare(int transactionId, List<Operation> operations) {
            return "prepared";
        }

        @Override
        public String commit(int transactionId) {
            return "ack";
        }

        @Override
        public String rollback(int transactionId) {
            return "ack";
        }
    }

    private static class FailingMicroservice implements Microservice {
        @Override
        public String prepare(int transactionId, List<Operation> operations) {
            return "abort";
        }

        @Override
        public String commit(int transactionId) {
            return "ack";
        }

        @Override
        public String rollback(int transactionId) {
            return "ack";
        }
    }

    private static class SlowMicroservice implements Microservice {
        private final long delayMillis;
        
        public SlowMicroservice(long delayMillis) {
            this.delayMillis = delayMillis;
        }

        @Override
        public String prepare(int transactionId, List<Operation> operations) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "prepared";
        }

        @Override
        public String commit(int transactionId) {
            return "ack";
        }

        @Override
        public String rollback(int transactionId) {
            return "ack";
        }
    }

    private static class IntermittentFailingMicroservice implements Microservice {
        private int attemptCount = 0;

        @Override
        public String prepare(int transactionId, List<Operation> operations) {
            attemptCount++;
            return attemptCount % 2 == 1 ? "abort" : "prepared";
        }

        @Override
        public String commit(int transactionId) {
            return "ack";
        }

        @Override
        public String rollback(int transactionId) {
            return "ack";
        }
    }

    private static class TestOperation implements Operation {
        private final String id;

        public TestOperation(String id) {
            this.id = id;
        }

        @Override
        public void execute() {
            // Test operation - no actual side effects
        }
    }
}