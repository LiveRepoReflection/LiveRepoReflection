import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTxTest {
    private TransactionCoordinator coordinator;
    private DummyService serviceA;
    private DummyService serviceB;
    private DummyService serviceC;

    @BeforeEach
    public void setup() {
        coordinator = new TransactionCoordinator();
        serviceA = new DummyService("ServiceA");
        serviceB = new DummyService("ServiceB");
        serviceC = new DummyService("ServiceC");
        coordinator.registerService(serviceA);
        coordinator.registerService(serviceB);
        coordinator.registerService(serviceC);
    }

    @Test
    public void testSuccessfulCommit() throws Exception {
        // All services should prepare successfully.
        serviceA.setPrepareResponse(true);
        serviceB.setPrepareResponse(true);
        serviceC.setPrepareResponse(true);

        Transaction txn = coordinator.beginTransaction();
        coordinator.addOperation(txn, "opA");
        coordinator.addOperation(txn, "opB");
        coordinator.addOperation(txn, "opC");

        boolean result = coordinator.commitTransaction(txn);
        assertTrue(result, "Transaction should commit successfully when all services prepare.");
        assertEquals(TransactionStatus.COMMITTED, txn.getStatus());
    }

    @Test
    public void testFailedCommitDueToServiceAbort() throws Exception {
        // One service will abort during prepare.
        serviceA.setPrepareResponse(true);
        serviceB.setPrepareResponse(false); // This service will abort.
        serviceC.setPrepareResponse(true);

        Transaction txn = coordinator.beginTransaction();
        coordinator.addOperation(txn, "opA");
        coordinator.addOperation(txn, "opB");
        coordinator.addOperation(txn, "opC");

        boolean result = coordinator.commitTransaction(txn);
        assertFalse(result, "Transaction should abort due to one service failing its prepare phase.");
        assertEquals(TransactionStatus.ABORTED, txn.getStatus());
    }

    @Test
    public void testRollback() throws Exception {
        // Initiate a transaction and then explicitly rollback.
        serviceA.setPrepareResponse(true);
        serviceB.setPrepareResponse(true);
        serviceC.setPrepareResponse(true);

        Transaction txn = coordinator.beginTransaction();
        coordinator.addOperation(txn, "opA");
        coordinator.addOperation(txn, "opB");
        coordinator.addOperation(txn, "opC");

        coordinator.rollbackTransaction(txn);
        assertEquals(TransactionStatus.ABORTED, txn.getStatus());
    }

    @Test
    public void testServiceTimeoutLeadsToAbort() throws Exception {
        // Simulate a timeout by having one service not respond.
        serviceA.setPrepareResponse(true);
        serviceB.setPrepareResponse(true);
        serviceC.setNoResponse(true); // Simulate no response scenario.

        Transaction txn = coordinator.beginTransaction();
        coordinator.addOperation(txn, "opA");
        coordinator.addOperation(txn, "opB");
        coordinator.addOperation(txn, "opC");

        boolean result = coordinator.commitTransaction(txn);
        assertFalse(result, "Transaction should abort if a service times out during prepare.");
        assertEquals(TransactionStatus.ABORTED, txn.getStatus());
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Test that multiple transactions can be handled concurrently.
        serviceA.setPrepareResponse(true);
        serviceB.setPrepareResponse(true);
        serviceC.setPrepareResponse(true);

        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            futures.add(executor.submit(() -> {
                Transaction txn = coordinator.beginTransaction();
                coordinator.addOperation(txn, "opA");
                coordinator.addOperation(txn, "opB");
                coordinator.addOperation(txn, "opC");
                return coordinator.commitTransaction(txn);
            }));
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        for (Future<Boolean> future : futures) {
            try {
                assertTrue(future.get(), "Each concurrent transaction should commit successfully.");
            } catch (Exception e) {
                fail("Concurrent transaction execution failed: " + e.getMessage());
            }
        }
    }
}

// Below are dummy implementations to simulate the DTC logic. In a production environment,
// these would be replaced by the actual implementations.

enum TransactionStatus {
    INIT, PREPARED, COMMITTED, ABORTED;
}

class Transaction {
    private final UUID id;
    private TransactionStatus status;
    private final List<String> operations;

    public Transaction() {
        this.id = UUID.randomUUID();
        this.status = TransactionStatus.INIT;
        this.operations = new ArrayList<>();
    }

    public UUID getId() {
        return id;
    }

    public TransactionStatus getStatus() {
        return status;
    }

    public void setStatus(TransactionStatus status) {
        this.status = status;
    }

    public List<String> getOperations() {
        return operations;
    }

    public void addOperation(String op) {
        operations.add(op);
    }
}

interface Service {
    String getName();
    boolean prepare(Transaction txn);
    void commit(Transaction txn);
    void rollback(Transaction txn);
}

class DummyService implements Service {
    private final String name;
    private boolean prepareResponse = true;
    private boolean noResponse = false;

    public DummyService(String name) {
        this.name = name;
    }

    public void setPrepareResponse(boolean response) {
        this.prepareResponse = response;
        this.noResponse = false;
    }

    public void setNoResponse(boolean noResponse) {
        this.noResponse = noResponse;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(Transaction txn) {
        if (noResponse) {
            try {
                // Simulate no response by sleeping beyond the coordinator's timeout.
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return false;
        }
        return prepareResponse;
    }

    @Override
    public void commit(Transaction txn) {
        // Simulated commit logic.
    }

    @Override
    public void rollback(Transaction txn) {
        // Simulated rollback logic.
    }
}

class TransactionCoordinator {
    private final List<Service> services = new ArrayList<>();
    private final Map<UUID, Transaction> transactions = new ConcurrentHashMap<>();
    private final int timeoutMillis = 1000;
    private final int retryLimit = 3;

    public void registerService(Service service) {
        services.add(service);
    }

    public Transaction beginTransaction() {
        Transaction txn = new Transaction();
        transactions.put(txn.getId(), txn);
        return txn;
    }

    public void addOperation(Transaction txn, String op) {
        txn.addOperation(op);
    }

    public boolean commitTransaction(Transaction txn) {
        txn.setStatus(TransactionStatus.PREPARED);
        List<Future<Boolean>> futures = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(services.size());

        for (Service service : services) {
            futures.add(executor.submit(() -> {
                int attempt = 0;
                while (attempt < retryLimit) {
                    boolean result = service.prepare(txn);
                    return result;
                }
                return false;
            }));
        }
        executor.shutdown();
        try {
            if (!executor.awaitTermination(timeoutMillis, TimeUnit.MILLISECONDS)) {
                executor.shutdownNow();
                txn.setStatus(TransactionStatus.ABORTED);
                return false;
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            txn.setStatus(TransactionStatus.ABORTED);
            return false;
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                if (!future.get(timeoutMillis, TimeUnit.MILLISECONDS)) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (!allPrepared) {
            txn.setStatus(TransactionStatus.ABORTED);
            for (Service service : services) {
                service.rollback(txn);
            }
            return false;
        }

        // Commit phase
        for (Service service : services) {
            service.commit(txn);
        }
        txn.setStatus(TransactionStatus.COMMITTED);
        return true;
    }

    public void rollbackTransaction(Transaction txn) {
        txn.setStatus(TransactionStatus.ABORTED);
        for (Service service : services) {
            service.rollback(txn);
        }
    }
}