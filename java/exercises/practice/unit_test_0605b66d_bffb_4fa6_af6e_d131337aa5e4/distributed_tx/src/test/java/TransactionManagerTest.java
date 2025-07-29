package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;

class TransactionManagerTest {

    static class DummyService implements Service {
        private final boolean prepareSuccess;
        private final long prepareDelayMillis;
        private final boolean throwOnPrepare;
        private final boolean throwOnCommit;
        private final boolean throwOnRollback;
        private final List<String> log = Collections.synchronizedList(new ArrayList<>());
        private final String name;

        DummyService(String name, boolean prepareSuccess, long prepareDelayMillis, boolean throwOnPrepare, boolean throwOnCommit, boolean throwOnRollback) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.prepareDelayMillis = prepareDelayMillis;
            this.throwOnPrepare = throwOnPrepare;
            this.throwOnCommit = throwOnCommit;
            this.throwOnRollback = throwOnRollback;
        }

        @Override
        public boolean prepare(TransactionContext tx) {
            log.add(name + " prepare start");
            if (prepareDelayMillis > 0) {
                try {
                    Thread.sleep(prepareDelayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            if (throwOnPrepare) {
                log.add(name + " prepare throw");
                throw new RuntimeException(name + " prepare exception");
            }
            log.add(name + " prepare done");
            return prepareSuccess;
        }

        @Override
        public void commit(TransactionContext tx) {
            log.add(name + " commit start");
            if (throwOnCommit) {
                log.add(name + " commit throw");
                throw new RuntimeException(name + " commit exception");
            }
            log.add(name + " commit done");
        }

        @Override
        public void rollback(TransactionContext tx) {
            log.add(name + " rollback start");
            if (throwOnRollback) {
                log.add(name + " rollback throw");
                throw new RuntimeException(name + " rollback exception");
            }
            log.add(name + " rollback done");
        }

        public List<String> getLog() {
            return log;
        }
    }

    private TransactionManager transactionManager;

    @BeforeEach
    public void setUp() {
        transactionManager = new TransactionManager();
    }

    @Test
    public void testSuccessfulTransaction() {
        DummyService service1 = new DummyService("S1", true, 0, false, false, false);
        DummyService service2 = new DummyService("S2", true, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        boolean result = transactionManager.executeTransaction(services);
        assertTrue(result, "Transaction should succeed");

        // Verify that prepare and commit phases were executed
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " prepare done"), "Prepare phase should complete for " + ds.name);
            assertTrue(serviceLog.contains(ds.name + " commit done"), "Commit phase should complete for " + ds.name);
        }
    }

    @Test
    public void testFailureInPrepare() {
        DummyService service1 = new DummyService("S1", true, 0, false, false, false);
        DummyService service2 = new DummyService("S2", false, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        boolean result = transactionManager.executeTransaction(services);
        assertFalse(result, "Transaction should fail due to prepare failure");

        // Verify that rollback was executed on both services
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " rollback done") || serviceLog.contains(ds.name + " rollback start"),
                    "Rollback should be initiated for " + ds.name);
        }
    }

    @Test
    public void testTimeoutOnPrepare() {
        // Assume the TransactionManager has a 5000 ms timeout for the prepare phase.
        DummyService service1 = new DummyService("S1", true, 6000, false, false, false);
        DummyService service2 = new DummyService("S2", true, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        boolean result = transactionManager.executeTransaction(services);
        assertFalse(result, "Transaction should fail due to prepare timeout");

        // Verify that rollback was executed on both services
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " rollback done") || serviceLog.contains(ds.name + " rollback start"),
                    "Rollback should be initiated for " + ds.name);
        }
    }

    @Test
    public void testExceptionDuringPrepare() {
        DummyService service1 = new DummyService("S1", true, 0, true, false, false);
        DummyService service2 = new DummyService("S2", true, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        boolean result = transactionManager.executeTransaction(services);
        assertFalse(result, "Transaction should fail due to exception during prepare");

        // Verify that rollback was executed on both services
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " rollback done") || serviceLog.contains(ds.name + " rollback start"),
                    "Rollback should be initiated for " + ds.name);
        }
    }

    @Test
    public void testExceptionDuringCommit() {
        DummyService service1 = new DummyService("S1", true, 0, false, true, false);
        DummyService service2 = new DummyService("S2", true, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        // Even if a commit exception is thrown, the transaction manager should treat the transaction as successful.
        boolean result = transactionManager.executeTransaction(services);
        assertTrue(result, "Transaction should succeed despite commit exception");

        // Verify that commit was attempted on both services
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " commit start"), "Commit phase should be initiated for " + ds.name);
        }
    }

    @Test
    public void testExceptionDuringRollback() {
        DummyService service1 = new DummyService("S1", false, 0, false, false, true);
        DummyService service2 = new DummyService("S2", true, 0, false, false, false);
        List<Service> services = Arrays.asList(service1, service2);

        boolean result = transactionManager.executeTransaction(services);
        assertFalse(result, "Transaction should fail when rollback is triggered even if exceptions occur during rollback");

        // Verify that rollback was attempted on both services
        for (DummyService ds : Arrays.asList(service1, service2)) {
            List<String> serviceLog = ds.getLog();
            assertTrue(serviceLog.contains(ds.name + " rollback start"),
                       "Rollback should be initiated for " + ds.name);
        }
    }
}