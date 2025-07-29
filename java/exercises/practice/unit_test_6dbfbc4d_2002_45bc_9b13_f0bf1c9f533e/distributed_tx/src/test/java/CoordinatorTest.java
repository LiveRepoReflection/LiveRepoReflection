import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class CoordinatorTest {

    // Mock service implementation for testing
    class MockService implements Service {
        private final String name;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;
        private final long delay; // delay in milliseconds
        private final boolean failOnPrepare;
        private boolean busy = false; // simulate one transaction at a time

        public MockService(String name) {
            this(name, 0, false);
        }

        public MockService(String name, long delay, boolean failOnPrepare) {
            this.name = name;
            this.delay = delay;
            this.failOnPrepare = failOnPrepare;
        }

        @Override
        public synchronized boolean prepare(String transactionId) {
            // if already busy with another transaction, return false
            if (busy) {
                return false;
            }
            busy = true;
            try {
                if (delay > 0) {
                    Thread.sleep(delay);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                busy = false;
                return false;
            }
            if (failOnPrepare) {
                busy = false;
                return false;
            }
            prepared = true;
            return true;
        }

        @Override
        public synchronized void commit(String transactionId) {
            if (!prepared) {
                return;
            }
            committed = true;
            busy = false;
        }

        @Override
        public synchronized void rollback(String transactionId) {
            rolledBack = true;
            busy = false;
        }

        @Override
        public String getServiceName() {
            return name;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Create a coordinator with a 1 second timeout for prepare phase.
        Coordinator coordinator = new Coordinator(1000);
        String txId = coordinator.beginTransaction();

        // Create services that succeed in preparing.
        MockService inventory = new MockService("Inventory");
        MockService payment = new MockService("Payment");
        MockService order = new MockService("Order");

        coordinator.registerService(inventory, txId);
        coordinator.registerService(payment, txId);
        coordinator.registerService(order, txId);

        boolean prepared = coordinator.prepareTransaction(txId);
        assertTrue(prepared, "All services should prepare successfully.");
        coordinator.commitTransaction(txId);

        assertTrue(inventory.isCommitted(), "Inventory service should be committed.");
        assertTrue(payment.isCommitted(), "Payment service should be committed.");
        assertTrue(order.isCommitted(), "Order service should be committed.");
    }

    @Test
    public void testPrepareFailure() throws Exception {
        Coordinator coordinator = new Coordinator(1000);
        String txId = coordinator.beginTransaction();

        // Simulate Payment service failure by returning false on prepare.
        MockService inventory = new MockService("Inventory");
        MockService payment = new MockService("Payment", 0, true);
        MockService order = new MockService("Order");

        coordinator.registerService(inventory, txId);
        coordinator.registerService(payment, txId);
        coordinator.registerService(order, txId);

        boolean prepared = coordinator.prepareTransaction(txId);
        assertFalse(prepared, "Prepare should fail due to one service failing to prepare.");
        coordinator.rollbackTransaction(txId);

        assertTrue(inventory.isRolledBack(), "Inventory should be rolled back.");
        assertTrue(payment.isRolledBack(), "Payment should be rolled back.");
        assertTrue(order.isRolledBack(), "Order should be rolled back.");
    }

    @Test
    public void testTimeoutDuringPrepare() throws Exception {
        // Set coordinator timeout to 500ms while one service delays for 1000ms.
        Coordinator coordinator = new Coordinator(500);
        String txId = coordinator.beginTransaction();

        MockService inventory = new MockService("Inventory");
        // This service will delay, causing timeout.
        MockService payment = new MockService("Payment", 1000, false);
        MockService order = new MockService("Order");

        coordinator.registerService(inventory, txId);
        coordinator.registerService(payment, txId);
        coordinator.registerService(order, txId);

        boolean prepared = coordinator.prepareTransaction(txId);
        assertFalse(prepared, "Prepare should fail due to timeout in one service.");
        coordinator.rollbackTransaction(txId);

        assertTrue(inventory.isRolledBack(), "Inventory should be rolled back after timeout.");
        assertTrue(payment.isRolledBack(), "Payment should be rolled back after timeout.");
        assertTrue(order.isRolledBack(), "Order should be rolled back after timeout.");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        final Coordinator coordinator = new Coordinator(1000);
        int numTransactions = 5;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> results = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            results.add(executor.submit(() -> {
                String txId = coordinator.beginTransaction();
                MockService service1 = new MockService("Service1");
                MockService service2 = new MockService("Service2");

                coordinator.registerService(service1, txId);
                coordinator.registerService(service2, txId);

                boolean prepared = coordinator.prepareTransaction(txId);
                if (prepared) {
                    coordinator.commitTransaction(txId);
                    return service1.isCommitted() && service2.isCommitted();
                } else {
                    coordinator.rollbackTransaction(txId);
                    return service1.isRolledBack() && service2.isRolledBack();
                }
            }));
        }

        for (Future<Boolean> future : results) {
            try {
                assertTrue(future.get(2, TimeUnit.SECONDS), "Concurrent transaction failed.");
            } catch (Exception e) {
                fail("Concurrent transaction encountered an exception: " + e.getMessage());
            }
        }
        executor.shutdown();
    }
}