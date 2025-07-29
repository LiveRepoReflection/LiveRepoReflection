package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ExecutionException;

// Unit tests for DistributedTransactionManager
public class DistributedTransactionManagerTest {

    private DistributedTransactionManager dtm;
    private TestServiceRegistry serviceRegistry;

    @BeforeEach
    void setUp() {
        serviceRegistry = new TestServiceRegistry();
        dtm = new DistributedTransactionManager(serviceRegistry);
    }

    @Test
    void testBeginTransactionReturnsUniqueID() {
        String tx1 = dtm.begin();
        String tx2 = dtm.begin();
        assertNotNull(tx1, "First transaction ID should not be null");
        assertNotNull(tx2, "Second transaction ID should not be null");
        assertNotEquals(tx1, tx2, "Transaction IDs should be unique");
    }

    @Test
    void testCommitTransactionSuccess() {
        String txId = dtm.begin();
        dtm.enlist(txId, "OrderService", "createOrder", "order data");
        dtm.enlist(txId, "InventoryService", "reserveItems", "item data");
        dtm.enlist(txId, "PaymentService", "processPayment", "payment data");
        dtm.enlist(txId, "ShippingService", "scheduleShipment", "shipping data");

        // Configure TestServiceRegistry for success responses.
        serviceRegistry.setSuccess("OrderService", true);
        serviceRegistry.setSuccess("InventoryService", true);
        serviceRegistry.setSuccess("PaymentService", true);
        serviceRegistry.setSuccess("ShippingService", true);

        boolean commitResult = dtm.commit(txId);
        assertTrue(commitResult, "Commit should succeed when all services succeed");
    }

    @Test
    void testCommitTransactionFailureTriggersRollback() {
        String txId = dtm.begin();
        dtm.enlist(txId, "OrderService", "createOrder", "order data");
        dtm.enlist(txId, "InventoryService", "reserveItems", "item data");
        dtm.enlist(txId, "PaymentService", "processPayment", "payment data");
        dtm.enlist(txId, "ShippingService", "scheduleShipment", "shipping data");

        // Configure TestServiceRegistry to simulate a failure in InventoryService.
        serviceRegistry.setSuccess("OrderService", true);
        serviceRegistry.setSuccess("InventoryService", false);
        serviceRegistry.setSuccess("PaymentService", true);
        serviceRegistry.setSuccess("ShippingService", true);

        boolean commitResult = dtm.commit(txId);
        assertFalse(commitResult, "Commit should fail when a service fails");
        // Verify that rollback process (compensation) has been triggered for all enlisted services
        assertTrue(serviceRegistry.wasCompensated("OrderService"), "OrderService should be compensated");
        assertTrue(serviceRegistry.wasCompensated("InventoryService"), "InventoryService should be compensated");
        assertTrue(serviceRegistry.wasCompensated("PaymentService"), "PaymentService should be compensated");
        assertTrue(serviceRegistry.wasCompensated("ShippingService"), "ShippingService should be compensated");
    }

    @Test
    void testRollbackTransactionManually() {
        String txId = dtm.begin();
        dtm.enlist(txId, "OrderService", "createOrder", "order data");
        dtm.enlist(txId, "InventoryService", "reserveItems", "item data");

        boolean rollbackResult = dtm.rollback(txId);
        assertTrue(rollbackResult, "Rollback should succeed for a valid transaction");
        assertTrue(serviceRegistry.wasCompensated("OrderService"), "OrderService should be compensated on rollback");
        assertTrue(serviceRegistry.wasCompensated("InventoryService"), "InventoryService should be compensated on rollback");
    }

    @Test
    void testCommitIdempotency() {
        String txId = dtm.begin();
        dtm.enlist(txId, "OrderService", "createOrder", "order data");

        serviceRegistry.setSuccess("OrderService", true);

        boolean firstCommit = dtm.commit(txId);
        boolean secondCommit = dtm.commit(txId);
        assertEquals(firstCommit, secondCommit, "Repeated commit should be idempotent");
        assertEquals(1, serviceRegistry.getExecutionCount("OrderService"), "Service execute should be called only once");
    }

    @Test
    void testRollbackIdempotency() {
        String txId = dtm.begin();
        dtm.enlist(txId, "OrderService", "createOrder", "order data");

        boolean firstRollback = dtm.rollback(txId);
        boolean secondRollback = dtm.rollback(txId);
        assertEquals(firstRollback, secondRollback, "Repeated rollback should be idempotent");
        assertEquals(1, serviceRegistry.getCompensationCount("OrderService"), "Service compensate should be called only once");
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int threadCount = 10;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                String txId = dtm.begin();
                dtm.enlist(txId, "OrderService", "createOrder", "order data");
                dtm.enlist(txId, "InventoryService", "reserveItems", "item data");
                serviceRegistry.setSuccess("OrderService", true);
                serviceRegistry.setSuccess("InventoryService", true);
                return dtm.commit(txId);
            });
        }

        List<Future<Boolean>> futures = executorService.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully");
        }
        executorService.shutdown();
    }

    // TestServiceRegistry simulates the behavior of real services.
    private static class TestServiceRegistry implements ServiceRegistry {
        private ConcurrentHashMap<String, Boolean> serviceSuccess = new ConcurrentHashMap<>();
        private ConcurrentHashMap<String, Integer> executionCount = new ConcurrentHashMap<>();
        private ConcurrentHashMap<String, Integer> compensationCount = new ConcurrentHashMap<>();
        private ConcurrentHashMap<String, Boolean> compensated = new ConcurrentHashMap<>();

        public void setSuccess(String service, boolean success) {
            serviceSuccess.put(service, success);
        }

        public boolean wasCompensated(String service) {
            return compensated.getOrDefault(service, false);
        }

        public int getExecutionCount(String service) {
            return executionCount.getOrDefault(service, 0);
        }

        public int getCompensationCount(String service) {
            return compensationCount.getOrDefault(service, 0);
        }

        @Override
        public boolean execute(String service, String operation, String data) {
            executionCount.merge(service, 1, Integer::sum);
            return serviceSuccess.getOrDefault(service, true);
        }

        @Override
        public boolean compensate(String service, String operation, String data) {
            compensationCount.merge(service, 1, Integer::sum);
            compensated.put(service, true);
            return true;
        }
    }
}

interface ServiceRegistry {
    boolean execute(String service, String operation, String data);
    boolean compensate(String service, String operation, String data);
}