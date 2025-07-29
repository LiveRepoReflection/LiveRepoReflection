package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.*;

// This test suite assumes the existence of the following classes/interfaces in your main source:
// - DistributedTransactionCoordinator with methods:
//       TransactionStatus executeTransaction(String transactionId, List<BranchService> branches)
//       void simulateCrashDuringCommit(String transactionId, List<BranchService> branches)
//       TransactionStatus recoverPendingTransactions(String transactionId)
// - BranchService interface with methods:
//       boolean prepare(String transactionId)
//       void commit(String transactionId)
//       void rollback(String transactionId)
// - TransactionStatus enum with values: COMMITTED and ABORTED

public class DistributedTxTest {

    private DistributedTransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new DistributedTransactionCoordinator();
    }

    // Dummy implementation of BranchService for testing purposes.
    public static class DummyBranchService implements BranchService {
        private final boolean failOnPrepare;
        private final long prepareDelayMillis;

        public DummyBranchService(boolean failOnPrepare, long prepareDelayMillis) {
            this.failOnPrepare = failOnPrepare;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        @Override
        public boolean prepare(String transactionId) {
            if (prepareDelayMillis > 0) {
                try {
                    Thread.sleep(prepareDelayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            return !failOnPrepare;
        }

        @Override
        public void commit(String transactionId) {
            // Simulated commit logic.
        }

        @Override
        public void rollback(String transactionId) {
            // Simulated rollback logic.
        }
    }

    // Test a successful transaction where all branches prepare and commit.
    @Test
    public void testSuccessfulTransaction() {
        String transactionId = "tx_success";
        List<BranchService> branches = new ArrayList<>();
        branches.add(new DummyBranchService(false, 0));
        branches.add(new DummyBranchService(false, 0));

        TransactionStatus status = coordinator.executeTransaction(transactionId, branches);
        assertEquals(TransactionStatus.COMMITTED, status, "Expected transaction to be committed");
    }

    // Test a transaction that should abort when one branch fails during the prepare phase.
    @Test
    public void testAbortTransaction() {
        String transactionId = "tx_abort";
        List<BranchService> branches = new ArrayList<>();
        branches.add(new DummyBranchService(false, 0));
        // This branch will simulate a preparation failure.
        branches.add(new DummyBranchService(true, 0));

        TransactionStatus status = coordinator.executeTransaction(transactionId, branches);
        assertEquals(TransactionStatus.ABORTED, status, "Expected transaction to be aborted due to a branch failure");
    }

    // Test a transaction that times out due to one branch's delayed response.
    @Test
    public void testTimeoutTransaction() {
        String transactionId = "tx_timeout";
        List<BranchService> branches = new ArrayList<>();
        // Assuming the coordinator's timeout is less than 1500ms.
        branches.add(new DummyBranchService(false, 1500));
        branches.add(new DummyBranchService(false, 0));

        TransactionStatus status = coordinator.executeTransaction(transactionId, branches);
        // Expect the coordinator to abort if a branch does not respond in time.
        assertEquals(TransactionStatus.ABORTED, status, "Expected transaction to be aborted due to timeout");
    }

    // Test multiple concurrent transactions to ensure proper isolation and synchronization.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<TransactionStatus>> tasks = new ArrayList<>();

        for (int i = 0; i < 10; i++) {
            final String txId = "tx_concurrent_" + i;
            tasks.add(() -> {
                List<BranchService> branches = new ArrayList<>();
                branches.add(new DummyBranchService(false, 0));
                branches.add(new DummyBranchService(false, 0));
                return coordinator.executeTransaction(txId, branches);
            });
        }

        List<Future<TransactionStatus>> futures = executor.invokeAll(tasks);
        for (Future<TransactionStatus> future : futures) {
            TransactionStatus status = future.get();
            assertEquals(TransactionStatus.COMMITTED, status, "Expected concurrent transaction to be committed");
        }
        executor.shutdown();
    }

    // Test the recovery mechanism to handle unfinished transactions after a simulated coordinator crash.
    @Test
    public void testRecovery() {
        String transactionId = "tx_recovery";
        List<BranchService> branches = new ArrayList<>();
        // Use branches with moderate delay to simulate ongoing transaction state.
        branches.add(new DummyBranchService(false, 500));
        branches.add(new DummyBranchService(false, 500));

        // Simulate a crash during the commit phase.
        coordinator.simulateCrashDuringCommit(transactionId, branches);

        // Invoke the recovery mechanism to complete the pending transaction.
        TransactionStatus status = coordinator.recoverPendingTransactions(transactionId);
        assertEquals(TransactionStatus.COMMITTED, status, "Expected recovered transaction to be committed");
    }
}