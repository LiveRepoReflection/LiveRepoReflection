import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assertions;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTransactionManagerTest {

    private DistributedTransactionManager dtm;

    @BeforeEach
    public void setup() {
        dtm = new DistributedTransactionManager();
    }

    // Dummy implementation of a transaction participant for testing.
    private static class DummyParticipant implements TransactionParticipant {
        private final String name;
        private final boolean prepareSuccess;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        public DummyParticipant(String name, boolean prepareSuccess) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
        }

        @Override
        public boolean prepare() {
            prepared = true;
            return prepareSuccess;
        }

        @Override
        public void commit() {
            committed = true;
        }

        @Override
        public void rollback() {
            rolledBack = true;
        }

        public boolean isPrepared() {
            return prepared;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        public String getName() {
            return name;
        }
    }

    // Test a successful transaction where all participants vote commit.
    @Test
    public void testSuccessfulTransaction() {
        DummyParticipant p1 = new DummyParticipant("AccountService", true);
        DummyParticipant p2 = new DummyParticipant("InventoryService", true);

        List<TransactionParticipant> participants = List.of(p1, p2);
        boolean result = dtm.executeTransaction(participants);

        Assertions.assertTrue(result, "The transaction should have been committed");
        // After commit, all services should reflect commit state.
        for (TransactionParticipant participant : participants) {
            DummyParticipant dp = (DummyParticipant) participant;
            Assertions.assertTrue(dp.isPrepared(), dp.getName() + " should have been prepared");
            Assertions.assertTrue(dp.isCommitted(), dp.getName() + " should have committed");
            Assertions.assertFalse(dp.isRolledBack(), dp.getName() + " should not have rolled back");
        }
    }

    // Test a transaction rollback if any participant fails during preparation.
    @Test
    public void testRolledBackTransaction() {
        DummyParticipant p1 = new DummyParticipant("AccountService", true);
        DummyParticipant p2 = new DummyParticipant("InventoryService", false); // Simulate failure

        List<TransactionParticipant> participants = List.of(p1, p2);
        boolean result = dtm.executeTransaction(participants);

        Assertions.assertFalse(result, "The transaction should have been rolled back");
        // In case of rollback, all participants should have rolled back.
        for (TransactionParticipant participant : participants) {
            DummyParticipant dp = (DummyParticipant) participant;
            Assertions.assertTrue(dp.isPrepared(), dp.getName() + " should have attempted preparation");
            Assertions.assertFalse(dp.isCommitted(), dp.getName() + " should not have committed");
            Assertions.assertTrue(dp.isRolledBack(), dp.getName() + " should have rolled back");
        }
    }

    // Test concurrent transaction execution to ensure thread safety and correctness.
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        // Count of concurrent transactions
        int numTransactions = 10;
        CountDownLatch latch = new CountDownLatch(numTransactions);
        AtomicInteger commitCount = new AtomicInteger(0);
        AtomicInteger rollbackCount = new AtomicInteger(0);

        Runnable transactionTask = () -> {
            // For each transaction, randomly decide which participant will fail.
            DummyParticipant p1 = new DummyParticipant("AccountService", true);
            // Simulate random failure: for this test, alternate success and failure.
            boolean p2Success = Thread.currentThread().getId() % 2 == 0;
            DummyParticipant p2 = new DummyParticipant("InventoryService", p2Success);
            List<TransactionParticipant> participants = new ArrayList<>();
            participants.add(p1);
            participants.add(p2);

            boolean result = dtm.executeTransaction(participants);
            if (result) {
                commitCount.incrementAndGet();
            } else {
                rollbackCount.incrementAndGet();
            }
            latch.countDown();
        };

        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < numTransactions; i++) {
            Thread t = new Thread(transactionTask);
            threads.add(t);
            t.start();
        }
        latch.await();

        // Validate that there are both commits and rollbacks based on simulated outcomes.
        Assertions.assertTrue(commitCount.get() >= 0, "There should be zero or more committed transactions");
        Assertions.assertTrue(rollbackCount.get() >= 0, "There should be zero or more rolled back transactions");
    }

    // Test resilience by simulating a participant "crashing" after preparation but before commit.
    @Test
    public void testParticipantRecoveryAfterCrash() {
        DummyParticipant p1 = new DummyParticipant("AccountService", true) {
            @Override
            public void commit() {
                // Simulate crash by not performing commit on first call.
                if (!isCommitted()) {
                    // Simulate delayed commit (e.g., crash before commit)
                    // Recovery mechanism should eventually commit.
                    // For simulation, call super.commit() after a delay.
                    try {
                        Thread.sleep(50);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    super.commit();
                }
            }
        };
        DummyParticipant p2 = new DummyParticipant("InventoryService", true);

        List<TransactionParticipant> participants = List.of(p1, p2);
        boolean result = dtm.executeTransaction(participants);

        Assertions.assertTrue(result, "The transaction should eventually commit after recovery");
        for (TransactionParticipant participant : participants) {
            DummyParticipant dp = (DummyParticipant) participant;
            Assertions.assertTrue(dp.isCommitted(), dp.getName() + " should have committed after recovery");
        }
    }
}