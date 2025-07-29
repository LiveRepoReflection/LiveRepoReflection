package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class TransactionManagerTest {

    static class DummyParticipant implements Participant {
        private final String name;
        private final boolean voteYes;
        private final long delayMillis;
        private final AtomicBoolean committed = new AtomicBoolean(false);
        private final AtomicBoolean rolledBack = new AtomicBoolean(false);

        public DummyParticipant(String name, boolean voteYes, long delayMillis) {
            this.name = name;
            this.voteYes = voteYes;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String transactionId) throws InterruptedException {
            if (delayMillis > 0) {
                Thread.sleep(delayMillis);
            }
            return voteYes;
        }

        @Override
        public void commit(String transactionId) {
            committed.set(true);
        }

        @Override
        public void rollback(String transactionId) {
            rolledBack.set(true);
        }

        public boolean isCommitted() {
            return committed.get();
        }

        public boolean isRolledBack() {
            return rolledBack.get();
        }

        public String getName() {
            return name;
        }
    }

    private TransactionManager txManager;

    @BeforeEach
    public void setUp() {
        txManager = new TransactionManager("distributed_tx_log.txt");
    }

    @Test
    public void testSuccessfulCommit() throws Exception {
        List<Participant> participants = new ArrayList<>();
        DummyParticipant p1 = new DummyParticipant("P1", true, 0);
        DummyParticipant p2 = new DummyParticipant("P2", true, 0);
        participants.add(p1);
        participants.add(p2);

        String transactionId = "tx_success_1";

        boolean result = txManager.executeTransaction(transactionId, participants);

        Assertions.assertTrue(result, "Transaction should commit successfully");
        Assertions.assertTrue(p1.isCommitted(), "Participant P1 should have committed");
        Assertions.assertTrue(p2.isCommitted(), "Participant P2 should have committed");
    }

    @Test
    public void testAbortDueToNegativeVote() throws Exception {
        List<Participant> participants = new ArrayList<>();
        DummyParticipant p1 = new DummyParticipant("P1", true, 0);
        DummyParticipant p2 = new DummyParticipant("P2", false, 0);
        participants.add(p1);
        participants.add(p2);

        String transactionId = "tx_abort_1";

        boolean result = txManager.executeTransaction(transactionId, participants);

        Assertions.assertFalse(result, "Transaction should be aborted");
        Assertions.assertTrue(p1.isRolledBack(), "Participant P1 should have rolled back");
        Assertions.assertTrue(p2.isRolledBack(), "Participant P2 should have rolled back");
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testParticipantTimeout() throws Exception {
        List<Participant> participants = new ArrayList<>();
        DummyParticipant p1 = new DummyParticipant("P1", true, 0);
        DummyParticipant p2 = new DummyParticipant("P2", true, 3000);
        participants.add(p1);
        participants.add(p2);

        String transactionId = "tx_timeout_1";

        boolean result = txManager.executeTransaction(transactionId, participants);

        Assertions.assertFalse(result, "Transaction should be aborted due to timeout");
        Assertions.assertTrue(p1.isRolledBack(), "Participant P1 should have rolled back due to timeout");
        Assertions.assertTrue(p2.isRolledBack(), "Participant P2 should have rolled back due to timeout");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int transactionCount = 10;
        List<Thread> threads = new ArrayList<>();
        List<AtomicBoolean> results = new ArrayList<>();

        for (int i = 0; i < transactionCount; i++) {
            final String txId = "tx_concurrent_" + i;
            AtomicBoolean resultFlag = new AtomicBoolean(false);
            results.add(resultFlag);
            Thread t = new Thread(() -> {
                try {
                    List<Participant> participants = new ArrayList<>();
                    DummyParticipant p1 = new DummyParticipant("P1", true, 0);
                    DummyParticipant p2 = new DummyParticipant("P2", true, 0);
                    participants.add(p1);
                    participants.add(p2);
                    boolean res = txManager.executeTransaction(txId, participants);
                    resultFlag.set(res);
                } catch (Exception e) {
                    resultFlag.set(false);
                }
            });
            threads.add(t);
            t.start();
        }

        for (Thread t : threads) {
            t.join();
        }

        for (AtomicBoolean result : results) {
            Assertions.assertTrue(result.get(), "All concurrent transactions should commit successfully");
        }
    }

    @Test
    public void testCoordinatorRecovery() throws Exception {
        List<Participant> participants = new ArrayList<>();
        DummyParticipant p1 = new DummyParticipant("P1", true, 0);
        DummyParticipant p2 = new DummyParticipant("P2", true, 0);
        participants.add(p1);
        participants.add(p2);

        String transactionId = "tx_recovery_1";

        Thread executionThread = new Thread(() -> {
            try {
                txManager.executeTransaction(transactionId, participants);
            } catch (Exception e) {
                // Exception ignored for simulation
            }
        });
        executionThread.start();
        Thread.sleep(500);

        TransactionManager recoveredTxManager = TransactionManager.recoverFromLog("distributed_tx_log.txt");
        recoveredTxManager.recoverPendingTransactions();

        Assertions.assertTrue(p1.isCommitted() || p1.isRolledBack(), "Participant P1 should have finalized its state after recovery");
        Assertions.assertTrue(p2.isCommitted() || p2.isRolledBack(), "Participant P2 should have finalized its state after recovery");
    }
}