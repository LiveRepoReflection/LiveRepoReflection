package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {

    private TransactionManager transactionManager;

    @BeforeEach
    public void setup() {
        // Create a new TransactionManager for each test
        transactionManager = new TransactionManager();
        // Set default configuration values: timeout = 1000ms, retries = 3, retryInterval = 500ms
        transactionManager.setTimeout(1000);
        transactionManager.setMaxRetries(3);
        transactionManager.setRetryInterval(500);
    }

    @Test
    public void testSuccessfulTransaction() {
        Transaction tx = transactionManager.createTransaction();
        tx.registerParticipant(new DummyParticipant(true, true));
        tx.registerParticipant(new DummyParticipant(true, true));
        boolean result = tx.execute();
        assertTrue(result, "Transaction should commit successfully when all participants succeed in prepare and commit phases.");
    }

    @Test
    public void testPrepareFailure() {
        Transaction tx = transactionManager.createTransaction();
        tx.registerParticipant(new DummyParticipant(true, true));
        // This participant will fail during prepare phase.
        tx.registerParticipant(new DummyParticipant(false, true));
        boolean result = tx.execute();
        assertFalse(result, "Transaction should roll back when any participant fails in the prepare phase.");
    }

    @Test
    public void testCommitFailureWithRetry() {
        Transaction tx = transactionManager.createTransaction();
        // This participant will fail commit a number of times before succeeding.
        tx.registerParticipant(new CommitRetryParticipant(2));
        tx.registerParticipant(new DummyParticipant(true, true));
        boolean result = tx.execute();
        assertTrue(result, "Transaction should commit successfully after retrying failed commit attempts within retry limit.");
    }

    @Test
    public void testTimeoutHandling() {
        Transaction tx = transactionManager.createTransaction();
        // Set a shorter timeout to force a timeout condition.
        tx.setTimeout(500);
        // This participant delays longer than the timeout during prepare phase.
        tx.registerParticipant(new SlowParticipant(600, true));
        boolean result = tx.execute();
        assertFalse(result, "Transaction should roll back when a participant exceeds the configured timeout in the prepare phase.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        Callable<Boolean> task = () -> {
            Transaction tx = transactionManager.createTransaction();
            tx.registerParticipant(new DummyParticipant(true, true));
            tx.registerParticipant(new DummyParticipant(true, true));
            return tx.execute();
        };
        Future<Boolean>[] results = new Future[numTransactions];
        for (int i = 0; i < numTransactions; i++) {
            results[i] = executor.submit(task);
        }
        for (int i = 0; i < numTransactions; i++) {
            assertTrue(results[i].get(), "Each concurrent transaction should commit successfully.");
        }
        executor.shutdown();
    }

    // DummyParticipant simulates a participant that returns fixed outcomes for prepare and commit.
    static class DummyParticipant implements Participant {
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private boolean prepared = false;

        public DummyParticipant(boolean prepareSuccess, boolean commitSuccess) {
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
        }

        @Override
        public boolean prepare() {
            prepared = true;
            return prepareSuccess;
        }

        @Override
        public boolean commit() {
            if (!prepared) {
                return false;
            }
            return commitSuccess;
        }

        @Override
        public boolean rollback() {
            // Always succeed in rollback
            return true;
        }
    }

    // CommitRetryParticipant simulates a participant that fails commit a specified number of times before succeeding.
    static class CommitRetryParticipant implements Participant {
        private int remainingFailures;
        private boolean prepared = false;

        public CommitRetryParticipant(int failures) {
            this.remainingFailures = failures;
        }

        @Override
        public boolean prepare() {
            prepared = true;
            return true;
        }

        @Override
        public boolean commit() {
            if (!prepared) {
                return false;
            }
            if (remainingFailures > 0) {
                remainingFailures--;
                return false;
            }
            return true;
        }

        @Override
        public boolean rollback() {
            // Always succeed in rollback
            return true;
        }
    }

    // SlowParticipant simulates a participant that delays its response during the prepare phase.
    static class SlowParticipant implements Participant {
        private final long delayMillis;
        private final boolean prepareResult;

        public SlowParticipant(long delayMillis, boolean prepareResult) {
            this.delayMillis = delayMillis;
            this.prepareResult = prepareResult;
        }

        @Override
        public boolean prepare() {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return prepareResult;
        }

        @Override
        public boolean commit() {
            return true;
        }

        @Override
        public boolean rollback() {
            return true;
        }
    }
}