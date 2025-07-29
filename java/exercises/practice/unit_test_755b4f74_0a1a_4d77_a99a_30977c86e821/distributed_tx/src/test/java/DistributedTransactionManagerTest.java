import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedTransactionManagerTest {

    // Dummy TransactionContext for testing purposes.
    public static class TransactionContext {
        private final UUID transactionId = UUID.randomUUID();
        public UUID getTransactionId() { return transactionId; }
    }

    // Dummy Operation class for testing purposes.
    public static class Operation {
        private final String serviceName;
        private final String operationDetails;
        public Operation(String serviceName, String operationDetails) {
            this.serviceName = serviceName;
            this.operationDetails = operationDetails;
        }
        public String getServiceName() { return serviceName; }
        public String getOperationDetails() { return operationDetails; }
    }

    // Service interface as described in the problem statement.
    public interface Service {
        String getName();
        boolean prepare(TransactionContext transactionContext, String operation);
        boolean commit(TransactionContext transactionContext, String operation);
        boolean rollback(TransactionContext transactionContext, String operation);
    }

    // A mock implementation of the Service interface for testing.
    public class MockService implements Service {
        private final String name;
        private boolean failPrepare;
        private boolean failCommit;
        private boolean failRollback;
        private long prepareDelay;
        private long commitDelay;
        private long rollbackDelay;
        public int commitAttempts = 0;
        public int rollbackAttempts = 0;

        public MockService(String name) {
            this.name = name;
            this.failPrepare = false;
            this.failCommit = false;
            this.failRollback = false;
            this.prepareDelay = 0;
            this.commitDelay = 0;
            this.rollbackDelay = 0;
        }

        public void setFailPrepare(boolean failPrepare) {
            this.failPrepare = failPrepare;
        }

        public void setFailCommit(boolean failCommit) {
            this.failCommit = failCommit;
        }

        public void setFailRollback(boolean failRollback) {
            this.failRollback = failRollback;
        }

        public void setPrepareDelay(long delayMillis) {
            this.prepareDelay = delayMillis;
        }

        public void setCommitDelay(long delayMillis) {
            this.commitDelay = delayMillis;
        }

        public void setRollbackDelay(long delayMillis) {
            this.rollbackDelay = delayMillis;
        }

        @Override
        public String getName() {
            return name;
        }

        @Override
        public boolean prepare(TransactionContext transactionContext, String operation) {
            try {
                if (prepareDelay > 0) {
                    Thread.sleep(prepareDelay);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return !failPrepare;
        }

        @Override
        public boolean commit(TransactionContext transactionContext, String operation) {
            commitAttempts++;
            try {
                if (commitDelay > 0) {
                    Thread.sleep(commitDelay);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return !failCommit;
        }

        @Override
        public boolean rollback(TransactionContext transactionContext, String operation) {
            rollbackAttempts++;
            try {
                if (rollbackDelay > 0) {
                    Thread.sleep(rollbackDelay);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return !failRollback;
        }
    }

    // A dummy implementation of the DistributedTransactionManager.
    // In the actual project, this class would reside in the main source.
    public class DistributedTransactionManager {
        private final Map<String, Service> serviceMap;
        private final long timeoutMillis = 500;
        private final int commitRetryLimit = 3;
        private final int rollbackRetryLimit = 3;
        private final ExecutorService executor = Executors.newCachedThreadPool();

        public DistributedTransactionManager(List<Service> services) {
            serviceMap = new HashMap<>();
            for (Service s : services) {
                serviceMap.put(s.getName(), s);
            }
        }

        public boolean executeTransaction(List<Operation> operations) {
            TransactionContext txContext = new TransactionContext();
            // Phase 1: Prepare
            for (Operation op : operations) {
                Service service = serviceMap.get(op.getServiceName());
                if (service == null) {
                    return false;
                }
                Future<Boolean> future = executor.submit(() -> service.prepare(txContext, op.getOperationDetails()));
                try {
                    if (!future.get(timeoutMillis, TimeUnit.MILLISECONDS)) {
                        rollbackAll(txContext, operations);
                        return false;
                    }
                } catch (Exception e) {
                    rollbackAll(txContext, operations);
                    return false;
                }
            }
            // Phase 2: Commit
            boolean commitSuccess = true;
            for (Operation op : operations) {
                Service service = serviceMap.get(op.getServiceName());
                if (service == null) {
                    continue;
                }
                boolean committed = false;
                int attempts = 0;
                while (attempts < commitRetryLimit && !committed) {
                    Future<Boolean> future = executor.submit(() -> service.commit(txContext, op.getOperationDetails()));
                    try {
                        committed = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    } catch (Exception e) {
                        committed = false;
                    }
                    attempts++;
                }
                if (!committed) {
                    commitSuccess = false;
                }
            }
            if (!commitSuccess) {
                rollbackAll(txContext, operations);
                return false;
            }
            return true;
        }

        private void rollbackAll(TransactionContext txContext, List<Operation> operations) {
            for (Operation op : operations) {
                Service service = serviceMap.get(op.getServiceName());
                if (service == null) {
                    continue;
                }
                int attempts = 0;
                boolean rolledBack = false;
                while (attempts < rollbackRetryLimit && !rolledBack) {
                    Future<Boolean> future = executor.submit(() -> service.rollback(txContext, op.getOperationDetails()));
                    try {
                        rolledBack = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    } catch (Exception e) {
                        rolledBack = false;
                    }
                    attempts++;
                }
            }
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        MockService service1 = new MockService("Service1");
        MockService service2 = new MockService("Service2");

        List<Service> services = Arrays.asList(service1, service2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);

        List<Operation> operations = Arrays.asList(
            new Operation("Service1", "Operation1"),
            new Operation("Service2", "Operation2")
        );
        boolean result = dtm.executeTransaction(operations);
        assertTrue(result, "Transaction should be successful when all services succeed.");
    }

    @Test
    public void testPrepareFailure() {
        MockService service1 = new MockService("Service1");
        MockService service2 = new MockService("Service2");
        service2.setFailPrepare(true);

        List<Service> services = Arrays.asList(service1, service2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);

        List<Operation> operations = Arrays.asList(
            new Operation("Service1", "Operation1"),
            new Operation("Service2", "Operation2")
        );
        boolean result = dtm.executeTransaction(operations);
        assertFalse(result, "Transaction should fail due to prepare phase failure.");
    }

    @Test
    public void testCommitFailureWithRetries() {
        MockService service1 = new MockService("Service1");
        MockService service2 = new MockService("Service2");
        service2.setFailCommit(true);

        List<Service> services = Arrays.asList(service1, service2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);

        List<Operation> operations = Arrays.asList(
            new Operation("Service1", "Operation1"),
            new Operation("Service2", "Operation2")
        );
        boolean result = dtm.executeTransaction(operations);
        assertFalse(result, "Transaction should fail due to commit phase failure even after retries.");
        assertTrue(service2.commitAttempts >= 3, "Service2 commit should be retried at least 3 times.");
    }

    @Test
    public void testTimeoutDuringPrepare() {
        MockService service1 = new MockService("Service1");
        service1.setPrepareDelay(600);
        MockService service2 = new MockService("Service2");

        List<Service> services = Arrays.asList(service1, service2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);

        List<Operation> operations = Arrays.asList(
            new Operation("Service1", "Operation1"),
            new Operation("Service2", "Operation2")
        );
        boolean result = dtm.executeTransaction(operations);
        assertFalse(result, "Transaction should fail due to timeout in the prepare phase.");
    }

    @Test
    public void testRollbackOnCommitFailure() {
        MockService service1 = new MockService("Service1");
        MockService service2 = new MockService("Service2");
        service2.setFailCommit(true);

        List<Service> services = Arrays.asList(service1, service2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);

        List<Operation> operations = Arrays.asList(
            new Operation("Service1", "Operation1"),
            new Operation("Service2", "Operation2")
        );
        boolean result = dtm.executeTransaction(operations);
        assertFalse(result, "Transaction should rollback if commit phase fails for any service.");
        assertTrue(service1.rollbackAttempts >= 1, "Service1 should have attempted rollback.");
        assertTrue(service2.rollbackAttempts >= 1, "Service2 should have attempted rollback.");
    }

    @Test
    @Timeout(5)
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        final int numTransactions = 10;
        List<MockService> mockServices = new ArrayList<>();
        for (int i = 1; i <= 3; i++) {
            mockServices.add(new MockService("Service" + i));
        }
        List<Service> services = new ArrayList<>(mockServices);
        DistributedTransactionManager dtm = new DistributedTransactionManager(services);
        ExecutorService executorService = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            tasks.add(() -> {
                List<Operation> ops = Arrays.asList(
                    new Operation("Service1", "Op" + ThreadLocalRandom.current().nextInt(100)),
                    new Operation("Service2", "Op" + ThreadLocalRandom.current().nextInt(100)),
                    new Operation("Service3", "Op" + ThreadLocalRandom.current().nextInt(100))
                );
                return dtm.executeTransaction(ops);
            });
        }

        List<Future<Boolean>> futures = executorService.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Concurrent transaction should succeed when all services operate normally.");
        }
        executorService.shutdown();
        executorService.awaitTermination(3, TimeUnit.SECONDS);
    }
}