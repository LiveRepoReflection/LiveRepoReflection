import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Timeout;

import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

// Dummy exceptions for simulation
class ServiceUnavailableException extends Exception {
    public ServiceUnavailableException(String message) {
        super(message);
    }
}

// The Service interface as defined in the problem statement
interface Service {
    boolean prepare(UUID transactionId) throws Exception;
    void commit(UUID transactionId) throws Exception;
    void rollback(UUID transactionId) throws Exception;
}

// Dummy implementation for success case
class AlwaysSuccessService implements Service {
    public boolean prepareCalled = false;
    public boolean commitCalled = false;
    public boolean rollbackCalled = false;

    @Override
    public boolean prepare(UUID transactionId) throws Exception {
        prepareCalled = true;
        return true;
    }

    @Override
    public void commit(UUID transactionId) throws Exception {
        commitCalled = true;
    }

    @Override
    public void rollback(UUID transactionId) throws Exception {
        rollbackCalled = true;
    }
}

// Dummy implementation for a service that fails during prepare by returning false
class AlwaysFailPrepareService implements Service {
    public boolean prepareCalled = false;
    public boolean rollbackCalled = false;

    @Override
    public boolean prepare(UUID transactionId) throws Exception {
        prepareCalled = true;
        return false;
    }

    @Override
    public void commit(UUID transactionId) throws Exception {
        // Should not be called if prepare fails
    }

    @Override
    public void rollback(UUID transactionId) throws Exception {
        rollbackCalled = true;
    }
}

// Dummy implementation for a service that throws exception during prepare
class ExceptionPrepareService implements Service {
    public boolean prepareCalled = false;
    public boolean rollbackCalled = false;

    @Override
    public boolean prepare(UUID transactionId) throws Exception {
        prepareCalled = true;
        throw new Exception("Prepare exception");
    }

    @Override
    public void commit(UUID transactionId) throws Exception {
        // Not expected
    }

    @Override
    public void rollback(UUID transactionId) throws Exception {
        rollbackCalled = true;
    }
}

// Dummy implementation for a service that simulates commit retries.
// It will throw exceptions a given number of times before succeeding.
class CommitRetryService implements Service {
    private final int failuresBeforeSuccess;
    private final AtomicInteger commitAttempts = new AtomicInteger(0);
    public boolean prepareCalled = false;
    public boolean commitCalled = false;
    public boolean rollbackCalled = false;

    public CommitRetryService(int failuresBeforeSuccess) {
        this.failuresBeforeSuccess = failuresBeforeSuccess;
    }

    @Override
    public boolean prepare(UUID transactionId) throws Exception {
        prepareCalled = true;
        return true;
    }

    @Override
    public void commit(UUID transactionId) throws Exception {
        int attempt = commitAttempts.incrementAndGet();
        if (attempt <= failuresBeforeSuccess) {
            throw new TimeoutException("Simulated timeout on commit attempt " + attempt);
        }
        commitCalled = true;
    }

    @Override
    public void rollback(UUID transactionId) throws Exception {
        rollbackCalled = true;
    }
}

// Dummy implementation for a service that always throws exception on rollback.
class RollbackExceptionService implements Service {
    public boolean prepareCalled = false;
    public boolean commitCalled = false;
    public boolean rollbackCalled = false;

    @Override
    public boolean prepare(UUID transactionId) throws Exception {
        prepareCalled = true;
        return false; // Force rollback scenario
    }

    @Override
    public void commit(UUID transactionId) throws Exception {
        commitCalled = true;
    }

    @Override
    public void rollback(UUID transactionId) throws Exception {
        rollbackCalled = true;
        throw new ServiceUnavailableException("Simulated failure in rollback");
    }
}

// Assume TxCoordinator implements the Distributed Transaction Coordinator functionality 
// according to the problem statement and is available in src/main/java.
// Its API includes: begin(), enlist(UUID transactionId, Service service),
// commit(UUID transactionId) which returns boolean, and rollback(UUID transactionId).
// For the purpose of testing, we assume its existence.

class TxCoordinator {
    // Internal storage for transactions: mapping transaction id to list of services
    private final ConcurrentMap<UUID, List<Service>> transactions = new ConcurrentHashMap<>();

    // Executor for retrying commit/rollback operations
    private final ScheduledExecutorService executor = Executors.newScheduledThreadPool(4);

    // Maximum number of retry attempts for commit/rollback operations
    private final int maxRetries = 3;
    // Delay between retries in milliseconds
    private final int retryDelayMs = 100;

    public UUID begin() {
        UUID txId = UUID.randomUUID();
        transactions.put(txId, new CopyOnWriteArrayList<>());
        return txId;
    }

    public void enlist(UUID transactionId, Service service) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList != null) {
            serviceList.add(service);
        } else {
            throw new IllegalArgumentException("Transaction does not exist");
        }
    }

    public boolean commit(UUID transactionId) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }

        // Phase 1: Prepare phase
        for (Service service : serviceList) {
            try {
                boolean prepared = service.prepare(transactionId);
                if (!prepared) {
                    rollback(transactionId);
                    transactions.remove(transactionId);
                    return false;
                }
            } catch (Exception e) {
                rollback(transactionId);
                transactions.remove(transactionId);
                return false;
            }
        }

        // Phase 2: Commit phase with retries
        for (Service service : serviceList) {
            boolean committed = executeWithRetry(() -> {
                service.commit(transactionId);
                return true;
            });
            if (!committed) {
                rollback(transactionId);
                transactions.remove(transactionId);
                return false;
            }
        }
        transactions.remove(transactionId);
        return true;
    }

    public void rollback(UUID transactionId) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }
        // Attempt to rollback all services with retries, logging error in case of failure.
        for (Service service : serviceList) {
            executeWithRetry(() -> {
                service.rollback(transactionId);
                return true;
            });
        }
        transactions.remove(transactionId);
    }

    // Helper method to execute an operation with retries on TimeoutException or ServiceUnavailableException
    private boolean executeWithRetry(Callable<Boolean> operation) {
        int attempts = 0;
        while (attempts < maxRetries) {
            try {
                return operation.call();
            } catch (TimeoutException | ServiceUnavailableException e) {
                attempts++;
                try {
                    Thread.sleep(retryDelayMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            } catch (Exception ex) {
                return false;
            }
        }
        return false;
    }
}

public class TxCoordinatorTest {

    private TxCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new TxCoordinator();
    }

    @Test
    public void testSuccessfulCommit() {
        UUID txId = coordinator.begin();
        AlwaysSuccessService service = new AlwaysSuccessService();
        coordinator.enlist(txId, service);

        boolean result = coordinator.commit(txId);
        assertTrue(result, "Transaction should commit successfully");
        assertTrue(service.prepareCalled, "Prepare should be called");
        assertTrue(service.commitCalled, "Commit should be called");
        assertFalse(service.rollbackCalled, "Rollback should not be called");
    }

    @Test
    public void testPrepareFailureTriggersRollback() {
        UUID txId = coordinator.begin();
        AlwaysFailPrepareService service = new AlwaysFailPrepareService();
        coordinator.enlist(txId, service);

        boolean result = coordinator.commit(txId);
        assertFalse(result, "Transaction should fail to commit due to prepare failure");
        assertTrue(service.prepareCalled, "Prepare should be called");
        assertTrue(service.rollbackCalled, "Rollback should be called after prepare failure");
    }

    @Test
    public void testExceptionDuringPrepareTriggersRollback() {
        UUID txId = coordinator.begin();
        ExceptionPrepareService service = new ExceptionPrepareService();
        coordinator.enlist(txId, service);

        boolean result = coordinator.commit(txId);
        assertFalse(result, "Transaction should fail to commit due to exception in prepare");
        assertTrue(service.prepareCalled, "Prepare should be called");
        assertTrue(service.rollbackCalled, "Rollback should be called after exception");
    }

    @Test
    public void testCommitWithRetrySuccess() {
        UUID txId = coordinator.begin();
        // Service will fail commit twice before succeeding on the third attempt.
        CommitRetryService service = new CommitRetryService(2);
        coordinator.enlist(txId, service);

        boolean result = coordinator.commit(txId);
        assertTrue(result, "Transaction should eventually commit successfully after retries");
        assertTrue(service.prepareCalled, "Prepare should be called");
        assertTrue(service.commitCalled, "Commit should ultimately succeed");
    }

    @Test
    public void testRollbackWithException() {
        UUID txId = coordinator.begin();
        RollbackExceptionService service = new RollbackExceptionService();
        coordinator.enlist(txId, service);

        // Commit should fail because prepare returns false, triggering rollback.
        boolean result = coordinator.commit(txId);
        assertFalse(result, "Transaction should fail commit due to prepare failure");
        assertTrue(service.prepareCalled, "Prepare should be called");
        // Even though rollback throws exception, our coordinator retries and eventually gives up.
        assertTrue(service.rollbackCalled, "Rollback should have been attempted");
    }

    @Test
    @Timeout(10)
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numThreads = 10;
        int transactionsPerThread = 20;
        ExecutorService exec = Executors.newFixedThreadPool(numThreads);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numThreads; i++) {
            tasks.add(() -> {
                boolean allSuccess = true;
                for (int j = 0; j < transactionsPerThread; j++) {
                    UUID txId = coordinator.begin();
                    AlwaysSuccessService service1 = new AlwaysSuccessService();
                    CommitRetryService service2 = new CommitRetryService(1);
                    coordinator.enlist(txId, service1);
                    coordinator.enlist(txId, service2);
                    boolean result = coordinator.commit(txId);
                    if (!result) {
                        allSuccess = false;
                    }
                }
                return allSuccess;
            });
        }

        List<Future<Boolean>> futures = exec.invokeAll(tasks);
        exec.shutdown();
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully");
        }
    }
}