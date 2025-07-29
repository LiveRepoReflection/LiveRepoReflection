package tx_coordinator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

// Dummy implementations of Service interface for testing
class AlwaysSuccessService implements Service {
    private final String name;
    private final List<String> log;

    AlwaysSuccessService(String name, List<String> log) {
        this.name = name;
        this.log = log;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(String transactionId, String data) {
        log.add("prepare:" + name + ":" + transactionId);
        return true;
    }

    @Override
    public void commit(String transactionId) {
        log.add("commit:" + name + ":" + transactionId);
    }

    @Override
    public void rollback(String transactionId) {
        log.add("rollback:" + name + ":" + transactionId);
    }
}

class FailingPrepareService implements Service {
    private final String name;
    private final List<String> log;

    FailingPrepareService(String name, List<String> log) {
        this.name = name;
        this.log = log;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(String transactionId, String data) {
        log.add("prepare:" + name + ":" + transactionId);
        return false;
    }

    @Override
    public void commit(String transactionId) {
        log.add("commit:" + name + ":" + transactionId);
    }

    @Override
    public void rollback(String transactionId) {
        log.add("rollback:" + name + ":" + transactionId);
    }
}

class ExceptionPrepareService implements Service {
    private final String name;
    private final List<String> log;

    ExceptionPrepareService(String name, List<String> log) {
        this.name = name;
        this.log = log;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(String transactionId, String data) {
        log.add("prepare:" + name + ":" + transactionId);
        throw new RuntimeException("Prepare exception in " + name);
    }

    @Override
    public void commit(String transactionId) {
        log.add("commit:" + name + ":" + transactionId);
    }

    @Override
    public void rollback(String transactionId) {
        log.add("rollback:" + name + ":" + transactionId);
    }
}

class DelayService implements Service {
    private final String name;
    private final List<String> log;
    private final long delayMillis;

    DelayService(String name, List<String> log, long delayMillis) {
        this.name = name;
        this.log = log;
        this.delayMillis = delayMillis;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(String transactionId, String data) {
        log.add("prepare:start:" + name + ":" + transactionId);
        try {
            Thread.sleep(delayMillis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
        log.add("prepare:end:" + name + ":" + transactionId);
        return true;
    }

    @Override
    public void commit(String transactionId) {
        log.add("commit:" + name + ":" + transactionId);
    }

    @Override
    public void rollback(String transactionId) {
        log.add("rollback:" + name + ":" + transactionId);
    }
}

public class DistributedTransactionCoordinatorTest {

    private DistributedTransactionCoordinator coordinator;
    private List<String> logList;

    @BeforeEach
    public void setup() {
        // Assuming a parameterless constructor for DistributedTransactionCoordinator
        coordinator = new DistributedTransactionCoordinator();
        logList = new ArrayList<>();
    }

    @Test
    public void testSuccessfulCommit() {
        String txId = coordinator.begin();
        Service service1 = new AlwaysSuccessService("Service1", logList);
        Service service2 = new AlwaysSuccessService("Service2", logList);

        coordinator.enlist(txId, service1, "data1");
        coordinator.enlist(txId, service2, "data2");

        coordinator.commit(txId);
        String status = coordinator.getTransactionStatus(txId);
        assertEquals("COMMITTED", status);

        // Check that commit logs exist for both services
        assertTrue(logList.stream().anyMatch(s -> s.equals("prepare:Service1:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("prepare:Service2:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("commit:Service1:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("commit:Service2:" + txId)));
    }

    @Test
    public void testPrepareFailureTriggersRollback() {
        String txId = coordinator.begin();
        Service service1 = new AlwaysSuccessService("Service1", logList);
        Service failingService = new FailingPrepareService("ServiceFail", logList);
        Service service2 = new AlwaysSuccessService("Service2", logList);

        coordinator.enlist(txId, service1, "data1");
        coordinator.enlist(txId, failingService, "dataFail");
        coordinator.enlist(txId, service2, "data2");

        coordinator.commit(txId);
        String status = coordinator.getTransactionStatus(txId);
        assertEquals("ROLLED_BACK", status);

        // Check that rollback was invoked for all services
        assertTrue(logList.stream().anyMatch(s -> s.equals("rollback:Service1:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("rollback:ServiceFail:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("rollback:Service2:" + txId)));
    }

    @Test
    public void testExceptionDuringPrepareTriggersRollback() {
        String txId = coordinator.begin();
        Service service1 = new AlwaysSuccessService("Service1", logList);
        Service exceptionService = new ExceptionPrepareService("ServiceEx", logList);

        coordinator.enlist(txId, service1, "data1");
        coordinator.enlist(txId, exceptionService, "dataEx");

        // Expect commit to handle the exception and perform rollback
        coordinator.commit(txId);
        String status = coordinator.getTransactionStatus(txId);
        assertEquals("ROLLED_BACK", status);

        // Check logs for rollback calls
        assertTrue(logList.stream().anyMatch(s -> s.equals("rollback:Service1:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.equals("rollback:ServiceEx:" + txId)));
    }

    @Test
    public void testTimeoutDuringPrepareTriggersRollback() {
        String txId = coordinator.begin();
        // Delay service with delay longer than the coordinator timeout
        Service delayService = new DelayService("SlowService", logList, 3000); // Delay 3000ms
        Service serviceNormal = new AlwaysSuccessService("ServiceNormal", logList);

        coordinator.enlist(txId, delayService, "dataSlow");
        coordinator.enlist(txId, serviceNormal, "dataNormal");

        // Assuming the coordinator has a timeout mechanism with duration < 3000ms
        coordinator.commit(txId);
        String status = coordinator.getTransactionStatus(txId);
        assertEquals("ROLLED_BACK", status);

        // Check that rollback was invoked due to timeout
        assertTrue(logList.stream().anyMatch(s -> s.startsWith("rollback:SlowService:" + txId)));
        assertTrue(logList.stream().anyMatch(s -> s.startsWith("rollback:ServiceNormal:" + txId)));
    }

    @Test
    public void testIdempotentCommitAndRollback() {
        String txId = coordinator.begin();
        Service service = new AlwaysSuccessService("Service1", logList);

        coordinator.enlist(txId, service, "data1");

        // Call commit multiple times
        coordinator.commit(txId);
        coordinator.commit(txId);

        String statusAfterCommit = coordinator.getTransactionStatus(txId);
        assertEquals("COMMITTED", statusAfterCommit);

        // Now, calling rollback after commit should not change outcome (idempotency)
        coordinator.rollback(txId);
        String statusAfterRollback = coordinator.getTransactionStatus(txId);
        assertEquals("COMMITTED", statusAfterRollback);
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(5);
        int transactionCount = 10;
        List<Future<String>> futures = new ArrayList<>();

        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger rolledBackCount = new AtomicInteger(0);

        for (int i = 0; i < transactionCount; i++) {
            futures.add(executor.submit(() -> {
                String txId = coordinator.begin();
                // Each transaction uses its own log to avoid concurrent modifications; using synchronized list for simplicity.
                Service service1 = new AlwaysSuccessService("Service1", logList);
                Service service2 = new AlwaysSuccessService("Service2", logList);
                coordinator.enlist(txId, service1, "data1");
                coordinator.enlist(txId, service2, "data2");
                // Randomly decide to force a rollback by enlisting a failing service
                if (ThreadLocalRandom.current().nextBoolean()) {
                    Service failingService = new FailingPrepareService("ServiceFail", logList);
                    coordinator.enlist(txId, failingService, "dataFail");
                }
                coordinator.commit(txId);
                String status = coordinator.getTransactionStatus(txId);
                if ("COMMITTED".equals(status)) {
                    successCount.incrementAndGet();
                } else if ("ROLLED_BACK".equals(status)) {
                    rolledBackCount.incrementAndGet();
                }
                return status;
            }));
        }

        for (Future<String> future : futures) {
            future.get();
        }
        executor.shutdownNow();

        // Ensure that all transactions ended in either COMMITTED or ROLLED_BACK
        int total = successCount.get() + rolledBackCount.get();
        assertEquals(transactionCount, total);
    }
}