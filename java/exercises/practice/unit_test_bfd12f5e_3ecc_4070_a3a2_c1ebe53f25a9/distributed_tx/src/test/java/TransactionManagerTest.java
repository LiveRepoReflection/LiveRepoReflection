package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionManagerTest {

    private TransactionManager txManager;

    @BeforeEach
    public void setup() {
        txManager = new TransactionManager();
    }

    // A simple DummyResourceManager to simulate ResourceManager behavior.
    private static class DummyResourceManager implements ResourceManager {
        private final String name;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;
        private final boolean failPrepare;
        private final boolean failCommit;

        public DummyResourceManager(String name, boolean failPrepare, boolean failCommit) {
            this.name = name;
            this.failPrepare = failPrepare;
            this.failCommit = failCommit;
        }

        @Override
        public synchronized boolean prepare(UUID transactionId) {
            if (prepared) {
                return true;
            }
            if (failPrepare) {
                return false;
            }
            prepared = true;
            return true;
        }

        @Override
        public synchronized void commit(UUID transactionId) {
            if (!prepared || committed) {
                return;
            }
            if (failCommit) {
                throw new RuntimeException("Commit failed for resource: " + name);
            }
            committed = true;
        }

        @Override
        public synchronized void rollback(UUID transactionId) {
            if (rolledBack) {
                return;
            }
            rolledBack = true;
        }
        
        // Getters for testing internal state (used within tests)
        public boolean isPrepared() {
            return prepared;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        UUID txId = txManager.begin();
        DummyResourceManager rm1 = new DummyResourceManager("rm1", false, false);
        DummyResourceManager rm2 = new DummyResourceManager("rm2", false, false);
        txManager.enlist(txId, rm1);
        txManager.enlist(txId, rm2);

        boolean prepareResult = txManager.prepare(txId);
        assertTrue(prepareResult, "Prepare phase should succeed when all resources are ready");

        // Commit should execute without throwing an exception.
        assertDoesNotThrow(() -> txManager.commit(txId));

        // Verify that the resource managers are in committed state.
        assertTrue(rm1.isCommitted(), "Resource manager rm1 should be committed");
        assertTrue(rm2.isCommitted(), "Resource manager rm2 should be committed");
    }

    @Test
    public void testPrepareFailureLeadsToRollback() {
        UUID txId = txManager.begin();
        DummyResourceManager rm1 = new DummyResourceManager("rm1", false, false);
        // This resource manager is set to fail in the prepare phase.
        DummyResourceManager rm2 = new DummyResourceManager("rm2", true, false);
        txManager.enlist(txId, rm1);
        txManager.enlist(txId, rm2);

        boolean prepareResult = txManager.prepare(txId);
        assertFalse(prepareResult, "Prepare phase should fail if any resource manager fails");

        // Attempting to commit should throw an exception since prepare did not succeed.
        assertThrows(RuntimeException.class, () -> txManager.commit(txId), "Commit should throw exception when prepare fails");

        // Rollback should be idempotent and not throw an exception.
        assertDoesNotThrow(() -> txManager.rollback(txId));
        assertTrue(rm1.isRolledBack(), "Resource manager rm1 should be rolled back");
        assertTrue(rm2.isRolledBack(), "Resource manager rm2 should be rolled back");
    }

    @Test
    public void testCommitFailureTriggersRollback() {
        UUID txId = txManager.begin();
        DummyResourceManager rm1 = new DummyResourceManager("rm1", false, false);
        // This resource manager is set to fail during commit.
        DummyResourceManager rm2 = new DummyResourceManager("rm2", false, true);
        txManager.enlist(txId, rm1);
        txManager.enlist(txId, rm2);

        boolean prepareResult = txManager.prepare(txId);
        assertTrue(prepareResult, "Prepare phase should succeed when all resources are ready");

        // Commit should throw an exception due to the failure in rm2.
        Exception commitException = assertThrows(RuntimeException.class, () -> txManager.commit(txId));
        assertNotNull(commitException, "Commit failure should throw an exception");

        // Rollback should execute without throwing an exception and be idempotent.
        assertDoesNotThrow(() -> txManager.rollback(txId));
        assertTrue(rm1.isRolledBack(), "Resource manager rm1 should be rolled back after commit failure");
        assertTrue(rm2.isRolledBack(), "Resource manager rm2 should be rolled back after commit failure");
    }

    @Test
    public void testIdempotency() {
        UUID txId = txManager.begin();
        DummyResourceManager rm = new DummyResourceManager("rm", false, false);
        txManager.enlist(txId, rm);

        boolean firstPrepare = txManager.prepare(txId);
        boolean secondPrepare = txManager.prepare(txId);
        assertEquals(firstPrepare, secondPrepare, "Prepare phase should be idempotent when called multiple times");

        // Commit twice; second call should not change state or throw an error.
        assertDoesNotThrow(() -> txManager.commit(txId));
        assertDoesNotThrow(() -> txManager.commit(txId));

        // Calling rollback after commit should do nothing and be idempotent.
        assertDoesNotThrow(() -> txManager.rollback(txId));
        assertDoesNotThrow(() -> txManager.rollback(txId));
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int numTransactions = 50;
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        AtomicInteger successCount = new AtomicInteger(0);

        for (int i = 0; i < numTransactions; i++) {
            tasks.add(() -> {
                UUID txId = txManager.begin();
                DummyResourceManager rm1 = new DummyResourceManager("rm1", false, false);
                DummyResourceManager rm2 = new DummyResourceManager("rm2", false, false);
                txManager.enlist(txId, rm1);
                txManager.enlist(txId, rm2);
                boolean prepareResult = txManager.prepare(txId);
                if (!prepareResult) {
                    txManager.rollback(txId);
                    return false;
                }
                try {
                    txManager.commit(txId);
                    successCount.incrementAndGet();
                    return true;
                } catch (RuntimeException ex) {
                    txManager.rollback(txId);
                    return false;
                }
            });
        }

        List<Future<Boolean>> futures = executor.invokeAll(tasks);
        for (Future<Boolean> f : futures) {
            f.get();
        }
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
        assertEquals(numTransactions, successCount.get(), "All concurrent transactions should commit successfully");
    }
}