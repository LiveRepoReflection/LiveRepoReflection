import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;

/**
 * This unit test suite tests the functionality of the TransactionCoordinator
 * implementing a 2PC protocol in a distributed banking system.
 */
public class TransactionCoordinatorTest {

    /**
     * A dummy implementation of the BankService interface for testing purposes.
     */
    class TestBankService implements BankService {
        private String name;
        private boolean prepareDebitSuccess;
        private boolean prepareCreditSuccess;
        private boolean commitDebitSuccess;
        private boolean commitCreditSuccess;
        private long delayMs;

        // For commit retry simulation: number of initial failures to simulate.
        private int commitDebitFailThreshold;
        private int commitCreditFailThreshold;
        private int commitDebitCallCount = 0;
        private int commitCreditCallCount = 0;

        // Counters to record rollback invocations.
        public int rollbackDebitCount = 0;
        public int rollbackCreditCount = 0;

        public TestBankService(String name,
                               boolean prepareDebitSuccess,
                               boolean prepareCreditSuccess,
                               boolean commitDebitSuccess,
                               boolean commitCreditSuccess,
                               long delayMs,
                               int commitDebitFailThreshold,
                               int commitCreditFailThreshold) {
            this.name = name;
            this.prepareDebitSuccess = prepareDebitSuccess;
            this.prepareCreditSuccess = prepareCreditSuccess;
            this.commitDebitSuccess = commitDebitSuccess;
            this.commitCreditSuccess = commitCreditSuccess;
            this.delayMs = delayMs;
            this.commitDebitFailThreshold = commitDebitFailThreshold;
            this.commitCreditFailThreshold = commitCreditFailThreshold;
        }

        @Override
        public boolean debit(String accountId, double amount) {
            // Not used by the coordinator.
            return true;
        }

        @Override
        public boolean credit(String accountId, double amount) {
            // Not used by the coordinator.
            return true;
        }

        @Override
        public boolean prepareDebit(String accountId, double amount) {
            if (delayMs > 0) {
                try {
                    Thread.sleep(delayMs);
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
            return prepareDebitSuccess;
        }

        @Override
        public boolean prepareCredit(String accountId, double amount) {
            if (delayMs > 0) {
                try {
                    Thread.sleep(delayMs);
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
            return prepareCreditSuccess;
        }

        @Override
        public boolean commitDebit(String accountId, double amount) {
            commitDebitCallCount++;
            if (commitDebitCallCount <= commitDebitFailThreshold) {
                return false;
            }
            return commitDebitSuccess;
        }

        @Override
        public boolean commitCredit(String accountId, double amount) {
            commitCreditCallCount++;
            if (commitCreditCallCount <= commitCreditFailThreshold) {
                return false;
            }
            return commitCreditSuccess;
        }

        @Override
        public boolean rollbackDebit(String accountId, double amount) {
            rollbackDebitCount++;
            return true;
        }

        @Override
        public boolean rollbackCredit(String accountId, double amount) {
            rollbackCreditCount++;
            return true;
        }

        @Override
        public boolean isAlive() {
            return true;
        }
    }

    /**
     * Tests that a transaction succeeds when all bank services succeed in all phases.
     */
    @Test
    public void testSuccessfulTransaction() {
        TestBankService debitService = new TestBankService(
            "DebitService", true, true, true, true, 0, 0, 0);
        TestBankService creditService = new TestBankService(
            "CreditService", true, true, true, true, 0, 0, 0);

        TransactionCoordinator coordinator = new TransactionCoordinator();
        List<BankService> services = Arrays.asList(debitService, creditService);
        boolean result = coordinator.transfer("A1", "B1", 100.0, services);
        assertTrue(result, "Transaction should succeed when all prepare and commit steps succeed.");
    }

    /**
     * Tests that the transaction fails if one service fails during the prepare phase.
     */
    @Test
    public void testPrepareFailure() {
        // Simulate the credit service failing in the prepareCredit phase.
        TestBankService debitService = new TestBankService(
            "DebitService", true, true, true, true, 0, 0, 0);
        TestBankService creditService = new TestBankService(
            "CreditService", true, false, true, true, 0, 0, 0);

        TransactionCoordinator coordinator = new TransactionCoordinator();
        List<BankService> services = Arrays.asList(debitService, creditService);
        boolean result = coordinator.transfer("A1", "B1", 200.0, services);
        assertFalse(result, "Transaction should fail because credit service prepare fails.");
        // Verify that rollback was invoked for debit service.
        assertTrue(debitService.rollbackDebitCount > 0, "Debit service should be rolled back.");
    }

    /**
     * Tests that the transaction fails when a service takes too long to respond in the prepare phase.
     */
    @Test
    public void testTimeoutDuringPrepare() {
        // Simulate a delay causing a timeout (delay greater than 5000ms).
        TestBankService debitService = new TestBankService(
            "DebitService", true, true, true, true, 6000, 0, 0);
        TestBankService creditService = new TestBankService(
            "CreditService", true, true, true, true, 0, 0, 0);

        TransactionCoordinator coordinator = new TransactionCoordinator();
        List<BankService> services = Arrays.asList(debitService, creditService);
        boolean result = coordinator.transfer("A1", "B1", 150.0, services);
        assertFalse(result, "Transaction should fail due to timeout during prepare phase.");
        // At least one rollback should have been invoked due to the timeout.
        boolean rollbackOccurred = debitService.rollbackDebitCount > 0 || creditService.rollbackCreditCount > 0;
        assertTrue(rollbackOccurred, "Rollback should occur when a service times out.");
    }

    /**
     * Tests the commit retry mechanism by having the debit service fail its commit phase
     * a few times before succeeding.
     */
    @Test
    public void testCommitRetryMechanism() {
        // Simulate the debit service failing commitDebit twice before succeeding.
        TestBankService debitService = new TestBankService(
            "DebitService", true, true, true, true, 0, 2, 0);
        TestBankService creditService = new TestBankService(
            "CreditService", true, true, true, true, 0, 0, 0);

        TransactionCoordinator coordinator = new TransactionCoordinator();
        List<BankService> services = Arrays.asList(debitService, creditService);
        boolean result = coordinator.transfer("A1", "B1", 50.0, services);
        assertTrue(result, "Transaction should succeed after commit retries.");
        assertTrue(debitService.commitDebitCallCount > 2, "Debit service commit should have been retried.");
    }

    /**
     * Tests that the transaction fails if a service consistently fails during the commit phase,
     * triggering rollback procedures.
     */
    @Test
    public void testServiceFailureDuringCommit() {
        // Simulate the credit service always failing in commitCredit (3 retries simulated).
        TestBankService debitService = new TestBankService(
            "DebitService", true, true, true, true, 0, 0, 0);
        TestBankService creditService = new TestBankService(
            "CreditService", true, true, true, false, 0, 0, 3);

        TransactionCoordinator coordinator = new TransactionCoordinator();
        List<BankService> services = Arrays.asList(debitService, creditService);
        boolean result = coordinator.transfer("A1", "B1", 75.0, services);
        assertFalse(result, "Transaction should fail if commit on credit service fails even after retries.");
        // Verify that rollback has been initiated on both services.
        assertTrue(debitService.rollbackDebitCount > 0, "Debit service should be rolled back upon commit failure.");
        assertTrue(creditService.rollbackCreditCount > 0, "Credit service should be rolled back upon commit failure.");
    }
}