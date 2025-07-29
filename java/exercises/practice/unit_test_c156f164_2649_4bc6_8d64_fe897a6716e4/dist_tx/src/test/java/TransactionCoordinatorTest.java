import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

import java.util.*;
import java.util.concurrent.*;

class TransactionCoordinatorTest {

    static class MockResourceManager implements ResourceManager {
        private final String name;
        private final boolean shouldAbort;
        private boolean committed = false;
        private boolean rolledBack = false;
        private int commitCount = 0;
        private int rollbackCount = 0;

        public MockResourceManager(String name, boolean shouldAbort) {
            this.name = name;
            this.shouldAbort = shouldAbort;
        }

        @Override
        public boolean prepare(String transactionId) {
            // Simulate preparation delay for realism if needed.
            return !shouldAbort;
        }

        @Override
        public void commit(String transactionId) {
            if (!committed) {
                committed = true;
                commitCount++;
            } else {
                // Idempotent commit; record additional calls.
                commitCount++;
            }
        }

        @Override
        public void rollback(String transactionId) {
            if (!rolledBack) {
                rolledBack = true;
                rollbackCount++;
            } else {
                // Idempotent rollback; record additional calls.
                rollbackCount++;
            }
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        public int getCommitCount() {
            return commitCount;
        }

        public int getRollbackCount() {
            return rollbackCount;
        }
    }

    TransactionCoordinator coordinator;

    @BeforeEach
    void setup() {
        coordinator = new TransactionCoordinator();
    }

    @Test
    void testSuccessfulTransaction() {
        String txId = "tx_success";
        List<ResourceManager> resourceManagers = new ArrayList<>();
        MockResourceManager rm1 = new MockResourceManager("RM1", false);
        MockResourceManager rm2 = new MockResourceManager("RM2", false);
        MockResourceManager rm3 = new MockResourceManager("RM3", false);
        resourceManagers.add(rm1);
        resourceManagers.add(rm2);
        resourceManagers.add(rm3);

        coordinator.registerTransaction(txId, resourceManagers);
        coordinator.executeTransaction(txId);

        Assertions.assertTrue(rm1.isCommitted());
        Assertions.assertTrue(rm2.isCommitted());
        Assertions.assertTrue(rm3.isCommitted());
        Assertions.assertFalse(rm1.isRolledBack());
        Assertions.assertFalse(rm2.isRolledBack());
        Assertions.assertFalse(rm3.isRolledBack());
    }

    @Test
    void testAbortedTransaction() {
        String txId = "tx_abort";
        List<ResourceManager> resourceManagers = new ArrayList<>();
        MockResourceManager rm1 = new MockResourceManager("RM1", false);
        // This RM will vote abort.
        MockResourceManager rm2 = new MockResourceManager("RM2", true);
        MockResourceManager rm3 = new MockResourceManager("RM3", false);
        resourceManagers.add(rm1);
        resourceManagers.add(rm2);
        resourceManagers.add(rm3);

        coordinator.registerTransaction(txId, resourceManagers);
        coordinator.executeTransaction(txId);

        Assertions.assertFalse(rm1.isCommitted());
        Assertions.assertFalse(rm2.isCommitted());
        Assertions.assertFalse(rm3.isCommitted());
        Assertions.assertTrue(rm1.isRolledBack());
        Assertions.assertTrue(rm2.isRolledBack());
        Assertions.assertTrue(rm3.isRolledBack());
    }

    @Test
    void testIdempotencyOfCommitAndRollback() {
        String txId = "tx_idempotency";
        List<ResourceManager> resourceManagers = new ArrayList<>();
        MockResourceManager rm1 = new MockResourceManager("RM1", false);
        resourceManagers.add(rm1);

        coordinator.registerTransaction(txId, resourceManagers);
        coordinator.executeTransaction(txId);

        // Manually invoke commit multiple times to simulate duplicate messages.
        rm1.commit(txId);
        rm1.commit(txId);
        // Expect that the first commit from executeTransaction plus additional calls recorded.
        Assertions.assertEquals(3, rm1.getCommitCount());

        // Similarly, manually invoke rollback multiple times.
        rm1.rollback(txId);
        rm1.rollback(txId);
        Assertions.assertEquals(2, rm1.getRollbackCount());
    }

    @Test
    void testConcurrentTransactions() throws Exception {
        int transactionCount = 10;
        List<String> txIds = new ArrayList<>();
        Map<String, List<MockResourceManager>> transactionMap = new HashMap<>();

        for (int i = 0; i < transactionCount; i++) {
            String txId = "tx_concurrent_" + i;
            txIds.add(txId);
            List<ResourceManager> resourceManagers = new ArrayList<>();
            MockResourceManager rmA = new MockResourceManager("RM_A_" + i, false);
            MockResourceManager rmB = new MockResourceManager("RM_B_" + i, false);
            resourceManagers.add(rmA);
            resourceManagers.add(rmB);
            coordinator.registerTransaction(txId, resourceManagers);
            transactionMap.put(txId, Arrays.asList(rmA, rmB));
        }
        
        ExecutorService executor = Executors.newFixedThreadPool(transactionCount);
        List<Callable<String>> tasks = new ArrayList<>();
        for (String txId : txIds) {
            tasks.add(() -> {
                coordinator.executeTransaction(txId);
                return txId;
            });
        }
        List<Future<String>> futures = executor.invokeAll(tasks);
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // Verify each concurrent transaction committed successfully.
        for (String txId : txIds) {
            List<MockResourceManager> rms = transactionMap.get(txId);
            for (MockResourceManager rm : rms) {
                Assertions.assertTrue(rm.isCommitted());
                Assertions.assertFalse(rm.isRolledBack());
            }
        }
    }

    @Test
    void testCrashRecoverySimulation() {
        String txId = "tx_recovery";
        List<ResourceManager> resourceManagers = new ArrayList<>();
        MockResourceManager rm1 = new MockResourceManager("RM1", false);
        MockResourceManager rm2 = new MockResourceManager("RM2", false);
        resourceManagers.add(rm1);
        resourceManagers.add(rm2);

        coordinator.registerTransaction(txId, resourceManagers);
        // Simulate crash after prepare phase and before final decision.
        coordinator.simulateCrashAfterPrepare(txId);

        // Simulate recovery.
        coordinator.recover();

        // After recovery, the transaction should have been committed.
        Assertions.assertTrue(rm1.isCommitted());
        Assertions.assertTrue(rm2.isCommitted());
        Assertions.assertFalse(rm1.isRolledBack());
        Assertions.assertFalse(rm2.isRolledBack());
    }
}

interface ResourceManager {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}

class TransactionCoordinator {
    private final Map<String, List<ResourceManager>> transactions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> transactionPrepared = new ConcurrentHashMap<>();

    public void registerTransaction(String transactionId, List<ResourceManager> resourceManagers) {
        transactions.put(transactionId, resourceManagers);
    }

    public void executeTransaction(String transactionId) {
        List<ResourceManager> resourceManagers = transactions.get(transactionId);
        if (resourceManagers == null) {
            throw new IllegalArgumentException("Transaction not registered: " + transactionId);
        }
        boolean allPrepared = true;
        for (ResourceManager rm : resourceManagers) {
            if (!rm.prepare(transactionId)) {
                allPrepared = false;
                break;
            }
        }
        transactionPrepared.put(transactionId, allPrepared);
        if (allPrepared) {
            for (ResourceManager rm : resourceManagers) {
                rm.commit(transactionId);
            }
        } else {
            for (ResourceManager rm : resourceManagers) {
                rm.rollback(transactionId);
            }
        }
    }

    public void simulateCrashAfterPrepare(String transactionId) {
        List<ResourceManager> resourceManagers = transactions.get(transactionId);
        if (resourceManagers == null) {
            return;
        }
        boolean allPrepared = true;
        for (ResourceManager rm : resourceManagers) {
            if (!rm.prepare(transactionId)) {
                allPrepared = false;
                break;
            }
        }
        transactionPrepared.put(transactionId, allPrepared);
        // Simulated crash: do not proceed to commit/rollback.
    }

    public void recover() {
        for (Map.Entry<String, Boolean> entry : transactionPrepared.entrySet()) {
            String txId = entry.getKey();
            List<ResourceManager> resourceManagers = transactions.get(txId);
            if (resourceManagers == null) {
                continue;
            }
            if (entry.getValue()) {
                for (ResourceManager rm : resourceManagers) {
                    rm.commit(txId);
                }
            } else {
                for (ResourceManager rm : resourceManagers) {
                    rm.rollback(txId);
                }
            }
        }
    }
}