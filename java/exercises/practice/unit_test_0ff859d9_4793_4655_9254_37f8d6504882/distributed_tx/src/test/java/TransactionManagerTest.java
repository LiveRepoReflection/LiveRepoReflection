import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

// Assuming that the following classes/interfaces are defined in the main sources:
// TransactionManager, TransactionID, ResourceManager, TransactionState
// For testing purposes, we define a FakeResourceManager that implements ResourceManager

public class TransactionManagerTest {

    public class FakeResourceManager implements ResourceManager {
        private final boolean prepareSuccess;
        private final Map<TransactionID, TransactionState> states = new ConcurrentHashMap<>();

        public FakeResourceManager(boolean prepareSuccess) {
            this.prepareSuccess = prepareSuccess;
        }

        @Override
        public synchronized boolean prepare(TransactionID transactionId) {
            if (prepareSuccess) {
                states.put(transactionId, TransactionState.PREPARED);
                return true;
            } else {
                return false;
            }
        }

        @Override
        public synchronized void commit(TransactionID transactionId) {
            TransactionState current = states.get(transactionId);
            if (current == TransactionState.PREPARED || current == TransactionState.COMMITTED) {
                states.put(transactionId, TransactionState.COMMITTED);
            }
        }

        @Override
        public synchronized void rollback(TransactionID transactionId) {
            TransactionState current = states.get(transactionId);
            if (current == TransactionState.PREPARED || current == TransactionState.ROLLEDBACK) {
                states.put(transactionId, TransactionState.ROLLEDBACK);
            }
        }

        @Override
        public synchronized TransactionState recover(TransactionID transactionId) {
            return states.getOrDefault(transactionId, TransactionState.UNKNOWN);
        }
    }

    private TransactionManager transactionManager;

    @BeforeEach
    public void setup() {
        transactionManager = new TransactionManager();
    }

    @Test
    public void testSuccessfulCommit() {
        TransactionID txId = transactionManager.begin();
        FakeResourceManager rm1 = new FakeResourceManager(true);
        FakeResourceManager rm2 = new FakeResourceManager(true);

        transactionManager.enlist(txId, rm1);
        transactionManager.enlist(txId, rm2);

        boolean commitResult = transactionManager.commit(txId);
        assertTrue(commitResult, "Commit should succeed when all resource managers prepare successfully.");
        assertEquals(TransactionState.COMMITTED, rm1.recover(txId), "Resource manager 1 should be COMMITTED.");
        assertEquals(TransactionState.COMMITTED, rm2.recover(txId), "Resource manager 2 should be COMMITTED.");
    }

    @Test
    public void testFailedPrepareTriggersRollback() {
        TransactionID txId = transactionManager.begin();
        FakeResourceManager rm1 = new FakeResourceManager(true);
        FakeResourceManager rm2 = new FakeResourceManager(false); // This one will fail in prepare

        transactionManager.enlist(txId, rm1);
        transactionManager.enlist(txId, rm2);

        boolean commitResult = transactionManager.commit(txId);
        assertFalse(commitResult, "Commit should fail when a resource manager fails to prepare.");
        // rm1 should be rolled back since it prepared successfully before failure was detected.
        assertEquals(TransactionState.ROLLEDBACK, rm1.recover(txId), "Resource manager 1 should be ROLLEDBACK.");
        // rm2 never prepared successfully so it remains in UNKNOWN state.
        assertEquals(TransactionState.UNKNOWN, rm2.recover(txId), "Resource manager 2 should be UNKNOWN.");
    }

    @Test
    public void testRecoveryCommitsPreparedTransactions() {
        // Simulate a scenario where a transaction was left in PREPARED state due to a crash
        TransactionID txId = transactionManager.begin();
        FakeResourceManager rm1 = new FakeResourceManager(true);
        FakeResourceManager rm2 = new FakeResourceManager(true);

        transactionManager.enlist(txId, rm1);
        transactionManager.enlist(txId, rm2);

        // Manually call prepare to simulate that the resource managers are in PREPARED state
        rm1.prepare(txId);
        rm2.prepare(txId);

        // Invoke recovery; the transaction manager should detect the in-flight transaction and complete it.
        transactionManager.recover();

        // After recovery, both resource managers should be in a COMMITTED state.
        assertEquals(TransactionState.COMMITTED, rm1.recover(txId), "Resource manager 1 should be COMMITTED after recovery.");
        assertEquals(TransactionState.COMMITTED, rm2.recover(txId), "Resource manager 2 should be COMMITTED after recovery.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();
        List<TransactionID> txIds = new ArrayList<>();
        List<FakeResourceManager> resourceManagers = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            TransactionID txId = transactionManager.begin();
            txIds.add(txId);
            FakeResourceManager rm = new FakeResourceManager(true);
            resourceManagers.add(rm);
            transactionManager.enlist(txId, rm);
            futures.add(executor.submit(() -> transactionManager.commit(txId)));
        }

        for (int i = 0; i < numTransactions; i++) {
            boolean result = futures.get(i).get();
            assertTrue(result, "Each concurrent transaction commit should succeed.");
            assertEquals(TransactionState.COMMITTED, resourceManagers.get(i).recover(txIds.get(i)), 
                         "Resource manager should be COMMITTED for transaction " + i);
        }
        executor.shutdown();
    }

    @Test
    public void testIdempotencyOfCommitAndRollback() {
        TransactionID txId = transactionManager.begin();
        FakeResourceManager rm = new FakeResourceManager(true);
        transactionManager.enlist(txId, rm);

        // First commit call
        boolean firstCommit = transactionManager.commit(txId);
        // Second commit call should be idempotent
        boolean secondCommit = transactionManager.commit(txId);

        assertTrue(firstCommit, "First commit should succeed.");
        assertTrue(secondCommit, "Second commit should be idempotent and succeed.");
        assertEquals(TransactionState.COMMITTED, rm.recover(txId), "Resource manager should be COMMITTED.");

        // Now test idempotency of rollback on a committed transaction.
        transactionManager.rollback(txId);
        // Committed state should be retained after a redundant rollback.
        assertEquals(TransactionState.COMMITTED, rm.recover(txId), "Resource manager should remain COMMITTED after rollback on a committed transaction.");
    }
}