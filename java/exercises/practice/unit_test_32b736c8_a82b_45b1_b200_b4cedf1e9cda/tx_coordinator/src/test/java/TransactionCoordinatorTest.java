import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.*;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new TransactionCoordinator();
    }

    // A dummy implementation of BankService to simulate various behaviors.
    class DummyBankService implements BankService {
        public boolean prepareCalled = false;
        public boolean commitCalled = false;
        public boolean rollbackCalled = false;
        private final boolean prepareResult;
        private final long delayMillis; // Used to simulate response delays

        public DummyBankService(boolean prepareResult, long delayMillis) {
            this.prepareResult = prepareResult;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String transactionId) {
            try {
                if (delayMillis > 0) {
                    Thread.sleep(delayMillis);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            prepareCalled = true;
            return prepareResult;
        }

        @Override
        public void commit(String transactionId) {
            commitCalled = true;
        }

        @Override
        public void rollback(String transactionId) {
            rollbackCalled = true;
        }
    }

    @Test
    public void testSuccessfulTransfer() throws Exception {
        // Begin a new transaction
        String txnId = coordinator.beginTransaction();

        // Create two bank services that always succeed in the prepare phase.
        DummyBankService bankService1 = new DummyBankService(true, 0);
        DummyBankService bankService2 = new DummyBankService(true, 0);

        // Enlist services for the transaction.
        coordinator.enlistBankService(txnId, bankService1);
        coordinator.enlistBankService(txnId, bankService2);

        // Execute the transfer operation.
        coordinator.transfer(txnId, bankService1, "acct1", bankService2, "acct2", 100);

        // Verify that prepare was called on both services.
        assertTrue(bankService1.prepareCalled);
        assertTrue(bankService2.prepareCalled);
        // Verify that commit was called because both prepared successfully.
        assertTrue(bankService1.commitCalled);
        assertTrue(bankService2.commitCalled);
        // Ensure rollback was not triggered.
        assertFalse(bankService1.rollbackCalled);
        assertFalse(bankService2.rollbackCalled);
    }

    @Test
    public void testFailedTransferByPrepareFailure() throws Exception {
        // Begin a new transaction.
        String txnId = coordinator.beginTransaction();

        // First bank service succeeds; second fails in the prepare phase.
        DummyBankService bankService1 = new DummyBankService(true, 0);
        DummyBankService bankService2 = new DummyBankService(false, 0);

        coordinator.enlistBankService(txnId, bankService1);
        coordinator.enlistBankService(txnId, bankService2);

        // Execute the transfer operation; expecting a rollback due to failure.
        coordinator.transfer(txnId, bankService1, "acct1", bankService2, "acct2", 50);

        // Both services should have been told to rollback.
        assertTrue(bankService1.prepareCalled);
        assertTrue(bankService2.prepareCalled);
        assertTrue(bankService1.rollbackCalled);
        assertTrue(bankService2.rollbackCalled);
        // Commit should not be called.
        assertFalse(bankService1.commitCalled);
        assertFalse(bankService2.commitCalled);
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Boolean>> futures = new ArrayList<>();
        int transactionCount = 20;

        for (int i = 0; i < transactionCount; i++) {
            futures.add(executor.submit(() -> {
                String txnId = coordinator.beginTransaction();
                DummyBankService bankService1 = new DummyBankService(true, 0);
                DummyBankService bankService2 = new DummyBankService(true, 0);
                coordinator.enlistBankService(txnId, bankService1);
                coordinator.enlistBankService(txnId, bankService2);
                coordinator.transfer(txnId, bankService1, "acct1", bankService2, "acct2", 10);
                return bankService1.commitCalled && bankService2.commitCalled;
            }));
        }
        for (Future<Boolean> future : futures) {
            try {
                // Each transaction should complete within 5 seconds.
                assertTrue(future.get(5, TimeUnit.SECONDS));
            } catch (TimeoutException e) {
                fail("Concurrent transaction timed out");
            }
        }
        executor.shutdownNow();
    }

    @Test
    public void testTimeoutDuringPrepare() throws Exception {
        // Begin a new transaction.
        String txnId = coordinator.beginTransaction();

        // Create a bank service that responds normally.
        DummyBankService bankService1 = new DummyBankService(true, 0);
        // Simulate a delayed bank service that exceeds the timeout threshold.
        DummyBankService bankService2 = new DummyBankService(true, 3000);

        coordinator.enlistBankService(txnId, bankService1);
        coordinator.enlistBankService(txnId, bankService2);

        // Execute the transfer operation; expecting a rollback due to timeout.
        coordinator.transfer(txnId, bankService1, "acct1", bankService2, "acct2", 75);

        // Verify that both services have been rolled back.
        assertTrue(bankService1.rollbackCalled);
        assertTrue(bankService2.rollbackCalled);
        // Commit should not have been executed.
        assertFalse(bankService1.commitCalled);
        assertFalse(bankService2.commitCalled);
    }

    @Test
    public void testIdempotentCommitAndRollback() throws Exception {
        // Begin a new transaction.
        String txnId = coordinator.beginTransaction();

        // Create a single bank service.
        DummyBankService bankService = new DummyBankService(true, 0);
        coordinator.enlistBankService(txnId, bankService);

        // Execute the transfer operation.
        coordinator.transfer(txnId, bankService, "acct1", bankService, "acct1", 100);

        // Manually invoke commit and rollback to simulate duplicate calls.
        bankService.commit(txnId);
        bankService.commit(txnId);
        bankService.rollback(txnId);
        bankService.rollback(txnId);

        // The service should reflect that commit and rollback have been processed (idempotently).
        assertTrue(bankService.commitCalled);
        assertTrue(bankService.rollbackCalled);
    }
}