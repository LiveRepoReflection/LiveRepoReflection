package distributed_tx;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class DistributedTxTest {

    private TransactionCoordinator coordinator;
    private List<Participant> participants;

    @BeforeEach
    public void setup() {
        participants = new ArrayList<>();
    }

    private TransactionCoordinator createCoordinatorWithParticipants(boolean allSucceed) {
        participants.clear();
        for (int i = 0; i < 3; i++) {
            participants.add(new MockParticipant("P" + i, allSucceed));
        }
        return new TransactionCoordinator(participants);
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        coordinator = createCoordinatorWithParticipants(true);
        Transaction tx = new Transaction("TX1");
        coordinator.beginTransaction(tx);
        boolean prepared = coordinator.prepareTransaction(tx);
        assertTrue(prepared, "All participants should prepare successfully");

        boolean committed = coordinator.commitTransaction(tx);
        assertTrue(committed, "Transaction commit should succeed");

        for (Participant p : participants) {
            assertTrue(((MockParticipant) p).isCommitted(), "Participant " + p.getId() + " should have committed");
        }
    }

    @Test
    public void testTransactionRollbackOnPrepareFailure() throws Exception {
        coordinator = createCoordinatorWithParticipants(false);
        Transaction tx = new Transaction("TX2");
        coordinator.beginTransaction(tx);
        boolean prepared = coordinator.prepareTransaction(tx);
        assertFalse(prepared, "At least one participant should fail to prepare");

        boolean rolledBack = coordinator.rollbackTransaction(tx);
        assertTrue(rolledBack, "Transaction rollback should succeed");

        for (Participant p : participants) {
            assertTrue(((MockParticipant) p).isRolledBack(), "Participant " + p.getId() + " should have rolled back");
        }
    }

    @Test
    public void testCoordinatorRecoveryDuringCommit() throws Exception {
        coordinator = createCoordinatorWithParticipants(true);
        Transaction tx = new Transaction("TX3");
        coordinator.beginTransaction(tx);
        boolean prepared = coordinator.prepareTransaction(tx);
        assertTrue(prepared, "All participants should prepare successfully");

        // Simulate failure in one participant during commit
        MockParticipant failingParticipant = (MockParticipant) participants.get(0);
        failingParticipant.simulateFailureOnCommit();

        boolean committed = coordinator.commitTransaction(tx);
        assertFalse(committed, "Transaction commit should fail due to a participant failure");

        boolean rolledBack = coordinator.rollbackTransaction(tx);
        assertTrue(rolledBack, "Transaction rollback should succeed after commit failure");

        for (Participant p : participants) {
            assertTrue(((MockParticipant) p).isRolledBack(), "Participant " + p.getId() + " should have rolled back");
        }
    }

    @Test
    public void testIdempotentMessageHandling() throws Exception {
        coordinator = createCoordinatorWithParticipants(true);
        Transaction tx = new Transaction("TX4");
        coordinator.beginTransaction(tx);
        boolean preparedFirst = coordinator.prepareTransaction(tx);
        assertTrue(preparedFirst, "First prepare should succeed");

        // Repeating the prepare should be idempotent
        boolean preparedSecond = coordinator.prepareTransaction(tx);
        assertTrue(preparedSecond, "Second prepare should also succeed idempotently");

        boolean committedFirst = coordinator.commitTransaction(tx);
        assertTrue(committedFirst, "First commit should succeed");

        // Repeating the commit call should have no additional effect
        boolean committedSecond = coordinator.commitTransaction(tx);
        assertTrue(committedSecond, "Second commit should remain idempotent");

        for (Participant p : participants) {
            assertTrue(((MockParticipant) p).isCommitted(), "Participant " + p.getId() + " should have committed");
        }
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        Transaction tx1 = new Transaction("CTX1");
        Transaction tx2 = new Transaction("CTX2");

        TransactionCoordinator coordinator1 = createCoordinatorWithParticipants(true);
        TransactionCoordinator coordinator2 = createCoordinatorWithParticipants(true);

        ExecutorService executor = Executors.newFixedThreadPool(2);

        Future<Boolean> future1 = executor.submit(() -> {
            coordinator1.beginTransaction(tx1);
            boolean prep = coordinator1.prepareTransaction(tx1);
            if (!prep) return false;
            return coordinator1.commitTransaction(tx1);
        });

        Future<Boolean> future2 = executor.submit(() -> {
            coordinator2.beginTransaction(tx2);
            boolean prep = coordinator2.prepareTransaction(tx2);
            if (!prep) return false;
            return coordinator2.commitTransaction(tx2);
        });

        try {
            boolean result1 = future1.get(5, TimeUnit.SECONDS);
            boolean result2 = future2.get(5, TimeUnit.SECONDS);
            assertTrue(result1, "Concurrent transaction 1 should commit successfully");
            assertTrue(result2, "Concurrent transaction 2 should commit successfully");
        } catch (TimeoutException te) {
            fail("Concurrent transactions timed out");
        } finally {
            executor.shutdownNow();
        }
    }

    // --- Mock Classes for Testing ---

    static class Transaction {
        private final String id;

        public Transaction(String id) {
            this.id = id;
        }

        public String getId() {
            return id;
        }
    }

    interface Participant {
        String getId();
        boolean prepare(Transaction tx);
        boolean commit(Transaction tx);
        boolean rollback(Transaction tx);
    }

    static class TransactionCoordinator {
        private final List<Participant> participants;
        private final Map<String, Transaction> activeTransactions = new ConcurrentHashMap<>();
        private final Map<String, Boolean> preparedStatus = new ConcurrentHashMap<>();
        private final Map<String, Boolean> commitStatus = new ConcurrentHashMap<>();

        public TransactionCoordinator(List<Participant> participants) {
            this.participants = participants;
        }

        public void beginTransaction(Transaction tx) {
            activeTransactions.put(tx.getId(), tx);
        }

        public boolean prepareTransaction(Transaction tx) {
            boolean overallPrepared = true;
            for (Participant participant : participants) {
                boolean prepared = participant.prepare(tx);
                if (!prepared) {
                    overallPrepared = false;
                }
            }
            preparedStatus.put(tx.getId(), overallPrepared);
            return overallPrepared;
        }

        public boolean commitTransaction(Transaction tx) {
            if (!Boolean.TRUE.equals(preparedStatus.get(tx.getId()))) {
                return false;
            }
            boolean overallCommit = true;
            for (Participant participant : participants) {
                boolean committed = participant.commit(tx);
                if (!committed) {
                    overallCommit = false;
                }
            }
            commitStatus.put(tx.getId(), overallCommit);
            return overallCommit;
        }

        public boolean rollbackTransaction(Transaction tx) {
            boolean overallRollback = true;
            for (Participant participant : participants) {
                if (!participant.rollback(tx)) {
                    overallRollback = false;
                }
            }
            return overallRollback;
        }
    }

    static class MockParticipant implements Participant {
        private final String id;
        private final boolean alwaysSucceed;
        private final AtomicBoolean prepared = new AtomicBoolean(false);
        private final AtomicBoolean committed = new AtomicBoolean(false);
        private final AtomicBoolean rolledBack = new AtomicBoolean(false);
        private final AtomicBoolean failOnCommit = new AtomicBoolean(false);

        public MockParticipant(String id, boolean alwaysSucceed) {
            this.id = id;
            this.alwaysSucceed = alwaysSucceed;
        }

        public void simulateFailureOnCommit() {
            failOnCommit.set(true);
        }

        public boolean isCommitted() {
            return committed.get();
        }

        public boolean isRolledBack() {
            return rolledBack.get();
        }

        @Override
        public String getId() {
            return id;
        }

        @Override
        public boolean prepare(Transaction tx) {
            if (alwaysSucceed) {
                prepared.set(true);
                return true;
            } else {
                prepared.set(false);
                return false;
            }
        }

        @Override
        public boolean commit(Transaction tx) {
            if (failOnCommit.get()) {
                return false;
            }
            if (prepared.get()) {
                committed.set(true);
                return true;
            }
            return false;
        }

        @Override
        public boolean rollback(Transaction tx) {
            if (prepared.get() || committed.get()) {
                rolledBack.set(true);
                return true;
            }
            rolledBack.set(true);
            return true;
        }
    }
}