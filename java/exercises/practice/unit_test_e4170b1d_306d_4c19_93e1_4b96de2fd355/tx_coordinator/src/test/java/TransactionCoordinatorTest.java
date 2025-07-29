import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.ArrayList;
import java.util.List;

class TransactionCoordinatorTest {

    // A dummy microservice used for testing purposes.
    static class TestService {
        private final String name;
        private final boolean prepareResult;
        private final long prepareDelayMillis; // Delay to simulate timeout in prepare phase.
        volatile boolean prepareCalled = false;
        volatile boolean commitCalled = false;
        volatile boolean rollbackCalled = false;

        TestService(String name, boolean prepareResult, long prepareDelayMillis) {
            this.name = name;
            this.prepareResult = prepareResult;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        public boolean prepare(String transactionId) {
            prepareCalled = true;
            try {
                if (prepareDelayMillis > 0) {
                    Thread.sleep(prepareDelayMillis);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return prepareResult;
        }

        public void commit(String transactionId) {
            commitCalled = true;
        }

        public void rollback(String transactionId) {
            rollbackCalled = true;
        }
    }

    TransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        // Create a new TransactionCoordinator instance with a default timeout (in milliseconds) for prepare phase.
        coordinator = new TransactionCoordinator(1000);
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        String txId = coordinator.begin();

        TestService service1 = new TestService("Service1", true, 0);
        TestService service2 = new TestService("Service2", true, 0);

        coordinator.enlist(service1, () -> service1.prepare(txId));
        coordinator.enlist(service2, () -> service2.prepare(txId));

        boolean committed = coordinator.commit();
        assertTrue(committed, "Transaction should commit successfully.");
        assertEquals(TransactionStatus.COMMITTED, coordinator.getStatus());

        // Verify that commit was invoked on all enlisted services.
        assertTrue(service1.commitCalled, "Service1 should have received commit.");
        assertTrue(service2.commitCalled, "Service2 should have received commit.");
    }

    @Test
    public void testTransactionRollbackDueToPrepareFailure() throws Exception {
        String txId = coordinator.begin();

        TestService service1 = new TestService("Service1", true, 0);
        TestService service2 = new TestService("Service2", false, 0); // This service fails during prepare

        coordinator.enlist(service1, () -> service1.prepare(txId));
        coordinator.enlist(service2, () -> service2.prepare(txId));

        boolean committed = coordinator.commit();
        assertFalse(committed, "Transaction should fail to commit due to a prepare failure.");
        assertEquals(TransactionStatus.ABORTED, coordinator.getStatus());

        // Both services should have been triggered for rollback.
        assertTrue(service1.rollbackCalled, "Service1 should have received rollback.");
        assertTrue(service2.rollbackCalled, "Service2 should have received rollback.");
    }

    @Test
    public void testExplicitRollback() throws Exception {
        String txId = coordinator.begin();

        TestService service1 = new TestService("Service1", true, 0);
        TestService service2 = new TestService("Service2", true, 0);

        coordinator.enlist(service1, () -> service1.prepare(txId));
        coordinator.enlist(service2, () -> service2.prepare(txId));

        coordinator.rollback();
        assertEquals(TransactionStatus.ABORTED, coordinator.getStatus());

        // Verify rollback was called on both services.
        assertTrue(service1.rollbackCalled, "Service1 should have received rollback on explicit abort.");
        assertTrue(service2.rollbackCalled, "Service2 should have received rollback on explicit abort.");
    }

    @Test
    public void testPrepareTimeout() throws Exception {
        // Set a very short timeout to simulate a prepare timeout.
        coordinator = new TransactionCoordinator(100);
        String txId = coordinator.begin();

        // This service's prepare method will delay longer than the timeout.
        TestService slowService = new TestService("SlowService", true, 500);
        coordinator.enlist(slowService, () -> slowService.prepare(txId));

        boolean committed = coordinator.commit();
        assertFalse(committed, "Transaction should fail due to timeout during prepare phase.");
        assertEquals(TransactionStatus.ABORTED, coordinator.getStatus());

        // Verify that rollback was called as a result of the timeout.
        assertTrue(slowService.rollbackCalled, "SlowService should have received rollback due to timeout.");
    }

    @Test
    public void testMultipleConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            tasks.add(() -> {
                TransactionCoordinator localCoordinator = new TransactionCoordinator(1000);
                String localTxId = localCoordinator.begin();
                TestService service = new TestService("ConcurrentService", true, 0);
                localCoordinator.enlist(service, () -> service.prepare(localTxId));
                return localCoordinator.commit();
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully.");
        }
        executor.shutdown();
    }
}