import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.*;
import java.util.concurrent.*;
import org.junit.jupiter.api.Test;

class TransactionCoordinatorTest {

    private static class TestOperationData implements OperationData {
        private final String info;

        TestOperationData(String info) {
            this.info = info;
        }

        public String getInfo() {
            return info;
        }
    }

    private static class TestService implements Service {
        private final String name;
        private final boolean prepareResult;
        private final boolean throwOnCommit;
        private final boolean throwOnRollback;
        private boolean commitCalled = false;
        private boolean rollbackCalled = false;
        private int prepareCallCount = 0;
        private int commitCallCount = 0;
        private int rollbackCallCount = 0;

        TestService(String name, boolean prepareResult, boolean throwOnCommit, boolean throwOnRollback) {
            this.name = name;
            this.prepareResult = prepareResult;
            this.throwOnCommit = throwOnCommit;
            this.throwOnRollback = throwOnRollback;
        }
        
        @Override
        public boolean prepare(UUID transactionId, OperationData operationData) {
            prepareCallCount++;
            // Simulate some processing delay.
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return prepareResult;
        }

        @Override
        public void commit(UUID transactionId) {
            commitCallCount++;
            commitCalled = true;
            // Simulate delay.
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            if (throwOnCommit) {
                throw new RuntimeException("Commit failed on service " + name);
            }
        }

        @Override
        public void rollback(UUID transactionId) {
            rollbackCallCount++;
            rollbackCalled = true;
            // Simulate delay.
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            if (throwOnRollback) {
                throw new RuntimeException("Rollback failed on service " + name);
            }
        }

        public String getName() {
            return name;
        }
    }

    @Test
    void testSuccessfulTransaction() {
        // Both services prepare successfully.
        TestService service1 = new TestService("Service1", true, false, false);
        TestService service2 = new TestService("Service2", true, false, false);

        Set<Service> services = new HashSet<>();
        services.add(service1);
        services.add(service2);

        Map<Service, OperationData> operations = new HashMap<>();
        operations.put(service1, new TestOperationData("Debit"));
        operations.put(service2, new TestOperationData("Credit"));

        TransactionCoordinator coordinator = new TransactionCoordinator(services);
        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, operations);

        assertTrue(result, "Transaction should succeed when all services prepare successfully.");
        // Allow for asynchronous tasks to complete.
        assertTrue(service1.commitCalled, "Service1 should have received commit call.");
        assertTrue(service2.commitCalled, "Service2 should have received commit call.");
    }

    @Test
    void testFailedPrepareTransaction() {
        // One service fails during prepare.
        TestService service1 = new TestService("Service1", true, false, false);
        TestService service2 = new TestService("Service2", false, false, false);

        Set<Service> services = new HashSet<>();
        services.add(service1);
        services.add(service2);

        Map<Service, OperationData> operations = new HashMap<>();
        operations.put(service1, new TestOperationData("Debit"));
        operations.put(service2, new TestOperationData("Credit"));

        TransactionCoordinator coordinator = new TransactionCoordinator(services);
        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, operations);

        assertFalse(result, "Transaction should fail if any service fails to prepare.");
        // Even if prepare failed, rollback should be called.
        assertTrue(service1.rollbackCalled, "Service1 should have received rollback call.");
        assertTrue(service2.rollbackCalled, "Service2 should have received rollback call.");
    }

    @Test
    void testCommitExceptionHandling() {
        // Services prepare successfully, but one throws exception during commit.
        TestService service1 = new TestService("Service1", true, true, false); // Will throw on commit.
        TestService service2 = new TestService("Service2", true, false, false);

        Set<Service> services = new HashSet<>();
        services.add(service1);
        services.add(service2);

        Map<Service, OperationData> operations = new HashMap<>();
        operations.put(service1, new TestOperationData("Debit"));
        operations.put(service2, new TestOperationData("Credit"));

        TransactionCoordinator coordinator = new TransactionCoordinator(services);
        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, operations);

        assertTrue(result, "Transaction should return true as prepare phase succeeded.");
        // Even if one commit throws, commit should be attempted on both.
        assertTrue(service1.commitCallCount > 0, "Service1 commit should be attempted.");
        assertTrue(service2.commitCallCount > 0, "Service2 commit should be attempted.");
    }

    @Test
    void testRollbackExceptionHandling() {
        // At least one service fails prepare, and one throws exception during rollback.
        TestService service1 = new TestService("Service1", false, false, true); // Will throw on rollback.
        TestService service2 = new TestService("Service2", true, false, false);

        Set<Service> services = new HashSet<>();
        services.add(service1);
        services.add(service2);

        Map<Service, OperationData> operations = new HashMap<>();
        operations.put(service1, new TestOperationData("Debit"));
        operations.put(service2, new TestOperationData("Credit"));

        TransactionCoordinator coordinator = new TransactionCoordinator(services);
        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, operations);

        assertFalse(result, "Transaction should fail due to one service failing in prepare.");
        // Even if rollback of one service throws exception, both rollbacks should be attempted.
        assertTrue(service1.rollbackCallCount > 0, "Service1 rollback should be attempted.");
        assertTrue(service2.rollbackCallCount > 0, "Service2 rollback should be attempted.");
    }

    @Test
    void testConcurrencyWithMultipleServices() throws InterruptedException {
        // Create many services to test concurrency aspects.
        int serviceCount = 10;
        Set<Service> services = new HashSet<>();
        Map<Service, OperationData> operations = new HashMap<>();
        
        for (int i = 0; i < serviceCount; i++) {
            TestService service = new TestService("Service" + i, true, false, false);
            services.add(service);
            operations.put(service, new TestOperationData("Operation" + i));
        }

        TransactionCoordinator coordinator = new TransactionCoordinator(services);
        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, operations);

        assertTrue(result, "Transaction should succeed when all services prepare successfully.");
        for (Service s : services) {
            TestService ts = (TestService) s;
            assertTrue(ts.commitCalled, ts.getName() + " should have received commit call.");
        }
    }
}