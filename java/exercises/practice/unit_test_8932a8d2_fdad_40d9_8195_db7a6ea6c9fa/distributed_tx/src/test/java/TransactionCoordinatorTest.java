package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;
    private BankServer bank1;
    private BankServer bank2;

    @BeforeEach
    public void setup() {
        // Initialize two bank servers with unique identifiers.
        bank1 = new BankServer("Bank1");
        bank2 = new BankServer("Bank2");

        // Create accounts on each bank server.
        bank1.createAccount("A1", 1000);
        bank2.createAccount("B1", 500);

        // Initialize the distributed transaction coordinator.
        coordinator = new TransactionCoordinator();
        coordinator.registerBankServer(bank1);
        coordinator.registerBankServer(bank2);
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Transfer 200 from source A1 (bank1) to destination B1 (bank2).
        Transaction tx = new Transaction("A1", "B1", 200);
        boolean result = coordinator.initiateTransaction(tx);
        assertTrue(result, "Transaction should commit successfully");
        assertEquals(800, bank1.getBalance("A1"), "Source account balance should be reduced by 200");
        assertEquals(700, bank2.getBalance("B1"), "Destination account balance should be increased by 200");
    }

    @Test
    public void testInsufficientFunds() throws Exception {
        // Attempt a transfer that exceeds the available funds in account A1.
        Transaction tx = new Transaction("A1", "B1", 1200);
        boolean result = coordinator.initiateTransaction(tx);
        assertFalse(result, "Transaction should fail due to insufficient funds");
        assertEquals(1000, bank1.getBalance("A1"), "Source account balance should remain unchanged");
        assertEquals(500, bank2.getBalance("B1"), "Destination account balance should remain unchanged");
    }

    @Test
    public void testServerFailureDuringTransaction() throws Exception {
        // Simulate failure in bank2 during a transaction.
        bank2.setAvailable(false);
        Transaction tx = new Transaction("A1", "B1", 100);
        boolean result = coordinator.initiateTransaction(tx);
        assertFalse(result, "Transaction should abort due to server failure");
        assertEquals(1000, bank1.getBalance("A1"), "Source account balance should remain unchanged due to abort");
        assertEquals(500, bank2.getBalance("B1"), "Destination account balance should remain unchanged due to abort");
        bank2.setAvailable(true); // Restore bank2 for further tests.
    }

    @Test
    public void testIdempotentTransactionApplication() throws Exception {
        // Test that duplicate transaction requests do not result in multiple applications.
        Transaction tx = new Transaction("A1", "B1", 150);
        boolean firstResult = coordinator.initiateTransaction(tx);
        boolean duplicateResult = coordinator.initiateTransaction(tx);
        assertTrue(firstResult, "First transaction should commit");
        assertFalse(duplicateResult, "Duplicate transaction should be ignored");
        assertEquals(850, bank1.getBalance("A1"), "Source account balance should be decreased only once");
        assertEquals(650, bank2.getBalance("B1"), "Destination account balance should be increased only once");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Test multiple concurrent transactions on the same accounts.
        // Reset the accounts to their original balances.
        bank1.updateBalance("A1", 1000);
        bank2.updateBalance("B1", 500);

        Transaction tx1 = new Transaction("A1", "B1", 100);
        Transaction tx2 = new Transaction("A1", "B1", 200);
        Transaction tx3 = new Transaction("A1", "B1", 300);

        ExecutorService executor = Executors.newFixedThreadPool(4);

        Callable<Boolean> task1 = () -> coordinator.initiateTransaction(tx1);
        Callable<Boolean> task2 = () -> coordinator.initiateTransaction(tx2);
        Callable<Boolean> task3 = () -> coordinator.initiateTransaction(tx3);

        Future<Boolean> f1 = executor.submit(task1);
        Future<Boolean> f2 = executor.submit(task2);
        Future<Boolean> f3 = executor.submit(task3);

        boolean res1 = f1.get();
        boolean res2 = f2.get();
        boolean res3 = f3.get();

        int totalDeducted = 0;
        totalDeducted += res1 ? 100 : 0;
        totalDeducted += res2 ? 200 : 0;
        totalDeducted += res3 ? 300 : 0;

        int finalBalanceA1 = bank1.getBalance("A1");
        int finalBalanceB1 = bank2.getBalance("B1");

        assertEquals(1000 - totalDeducted, finalBalanceA1, "Source account balance should reflect all successful transactions");
        assertEquals(500 + totalDeducted, finalBalanceB1, "Destination account balance should reflect all successful transactions");

        executor.shutdown();
    }

    @Test
    public void testLostUpdatePrevention() throws Exception {
        // Setup additional accounts on bank1 and bank2.
        bank1.createAccount("A2", 500);
        bank2.createAccount("B2", 300);

        // Simulate two concurrent transactions withdrawing funds from the same account A2.
        Transaction tx1 = new Transaction("A2", "B2", 200);
        Transaction tx2 = new Transaction("A2", "B2", 200);

        boolean result1 = coordinator.initiateTransaction(tx1);
        boolean result2 = coordinator.initiateTransaction(tx2);

        int finalBalanceA2 = bank1.getBalance("A2");
        int finalBalanceB2 = bank2.getBalance("B2");

        if (result1 && !result2) {
            assertEquals(300, finalBalanceA2, "Only one transaction should apply, reducing A2 by 200");
            assertEquals(500, finalBalanceB2, "B2 should be credited by 200");
        } else if (!result1 && result2) {
            assertEquals(300, finalBalanceA2, "Only one transaction should apply, reducing A2 by 200");
            assertEquals(500, finalBalanceB2, "B2 should be credited by 200");
        } else if (!result1 && !result2) {
            assertEquals(500, finalBalanceA2, "Neither transaction applied due to conflict");
            assertEquals(300, finalBalanceB2, "Neither transaction applied due to conflict");
        } else {
            fail("Both transactions should not commit when insufficient funds are available for both concurrent operations");
        }
    }
}