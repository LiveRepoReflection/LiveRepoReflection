import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }

    // A mock implementation of BankService that always succeeds.
    private static class SuccessfulBankService implements BankService {
        private final String name;

        SuccessfulBankService(String name) {
            this.name = name;
        }

        @Override
        public boolean debit(String accountId, double amount) throws InsufficientFundsException {
            return true;
        }

        @Override
        public boolean credit(String accountId, double amount) {
            return true;
        }

        @Override
        public boolean prepare(String transactionId, List<Operation> operations) {
            return true;
        }

        @Override
        public boolean commit(String transactionId) {
            return true;
        }

        @Override
        public boolean rollback(String transactionId) {
            return true;
        }
    }

    // A mock implementation of BankService that fails during prepare.
    private static class FailingPrepareBankService implements BankService {
        @Override
        public boolean debit(String accountId, double amount) throws InsufficientFundsException {
            return true;
        }

        @Override
        public boolean credit(String accountId, double amount) {
            return true;
        }

        @Override
        public boolean prepare(String transactionId, List<Operation> operations) {
            return false;
        }

        @Override
        public boolean commit(String transactionId) {
            return true;
        }

        @Override
        public boolean rollback(String transactionId) {
            return true;
        }
    }

    // A mock implementation of BankService that fails transiently before eventually succeeding.
    private static class TransientFailureBankService implements BankService {
        private final AtomicInteger prepareAttempts = new AtomicInteger(0);
        private final AtomicInteger commitAttempts = new AtomicInteger(0);
        private final AtomicInteger rollbackAttempts = new AtomicInteger(0);
        private final int failTimes;

        TransientFailureBankService(int failTimes) {
            this.failTimes = failTimes;
        }

        @Override
        public boolean debit(String accountId, double amount) throws InsufficientFundsException {
            return true;
        }

        @Override
        public boolean credit(String accountId, double amount) {
            return true;
        }

        @Override
        public boolean prepare(String transactionId, List<Operation> operations) {
            if (prepareAttempts.getAndIncrement() < failTimes) {
                return false;
            }
            return true;
        }

        @Override
        public boolean commit(String transactionId) {
            if (commitAttempts.getAndIncrement() < failTimes) {
                return false;
            }
            return true;
        }

        @Override
        public boolean rollback(String transactionId) {
            if (rollbackAttempts.getAndIncrement() < failTimes) {
                return false;
            }
            return true;
        }
    }

    // Helper method to create a sample list of operations.
    private List<Operation> createOperations() {
        List<Operation> ops = new ArrayList<>();
        Operation op1 = new Operation("acct-1", 100.0, OperationType.DEBIT);
        Operation op2 = new Operation("acct-2", 100.0, OperationType.CREDIT);
        ops.add(op1);
        ops.add(op2);
        return ops;
    }

    // Test committing a transaction with no enlisted bank services (empty transaction).
    @Test
    public void testEmptyTransactionCommit() {
        String txnId = coordinator.begin();
        coordinator.commit(txnId);
        TransactionStatus status = coordinator.getTransactionStatus(txnId);
        Assertions.assertEquals(TransactionStatus.COMMITTED, status);
    }

    // Test committing a transaction where all enlisted services succeed.
    @Test
    public void testSuccessfulTransactionCommit() {
        String txnId = coordinator.begin();
        BankService service1 = new SuccessfulBankService("Bank1");
        coordinator.enlist(txnId, service1, createOperations());
        coordinator.commit(txnId);
        TransactionStatus status = coordinator.getTransactionStatus(txnId);
        Assertions.assertEquals(TransactionStatus.COMMITTED, status);
    }

    // Test that a service failing during the prepare phase causes the transaction to be aborted.
    @Test
    public void testTransactionPrepareFailureCausesRollback() {
        String txnId = coordinator.begin();
        BankService service1 = new SuccessfulBankService("Bank1");
        BankService service2 = new FailingPrepareBankService();
        coordinator.enlist(txnId, service1, createOperations());
        coordinator.enlist(txnId, service2, createOperations());
        coordinator.commit(txnId);
        TransactionStatus status = coordinator.getTransactionStatus(txnId);
        Assertions.assertEquals(TransactionStatus.ABORTED, status);
    }

    // Test committing a transaction where a service experiences transient failures before eventually succeeding.
    @Test
    public void testTransactionCommitWithTransientFailures() {
        String txnId = coordinator.begin();
        BankService service1 = new TransientFailureBankService(2);
        coordinator.enlist(txnId, service1, createOperations());
        coordinator.commit(txnId);
        TransactionStatus status = coordinator.getTransactionStatus(txnId);
        Assertions.assertEquals(TransactionStatus.COMMITTED, status);
    }

    // Test explicitly rolling back a transaction.
    @Test
    public void testExplicitRollback() {
        String txnId = coordinator.begin();
        BankService service1 = new SuccessfulBankService("Bank1");
        coordinator.enlist(txnId, service1, createOperations());
        coordinator.rollback(txnId);
        TransactionStatus status = coordinator.getTransactionStatus(txnId);
        Assertions.assertEquals(TransactionStatus.ABORTED, status);
    }

    // Test managing multiple concurrent transactions.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<TransactionStatus>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            futures.add(executor.submit(() -> {
                TransactionCoordinator localCoordinator = new TransactionCoordinator();
                String txnId = localCoordinator.begin();
                BankService service = new SuccessfulBankService("ConcurrentBank");
                localCoordinator.enlist(txnId, service, createOperations());
                localCoordinator.commit(txnId);
                return localCoordinator.getTransactionStatus(txnId);
            }));
        }

        for (Future<TransactionStatus> future : futures) {
            TransactionStatus status = future.get();
            Assertions.assertEquals(TransactionStatus.COMMITTED, status);
        }
        executor.shutdown();
    }
}