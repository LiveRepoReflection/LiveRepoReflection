import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class TxCoordinatorTest {

    private DistributedTransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new DistributedTransactionCoordinator();
    }

    @Test
    public void testReadOnlyTransaction() {
        Transaction transaction = new Transaction("tx1");
        transaction.addOperation(new Operation("res1", OperationType.READ, null));
        TransactionOutcome outcome = coordinator.process(transaction);

        // A read-only transaction should commit and return the current state of resources.
        assertEquals("COMMIT", outcome.getStatus());
        assertNotNull(outcome.getResourceStates());
    }

    @Test
    public void testWriteTransactionCommit() {
        Transaction transaction = new Transaction("tx2");
        transaction.addOperation(new Operation("res1", OperationType.WRITE, "data1"));
        TransactionOutcome outcome = coordinator.process(transaction);

        // The write should commit and update the resource state.
        assertEquals("COMMIT", outcome.getStatus());
        assertEquals("data1", outcome.getResourceStates().get("res1"));
    }

    @Test
    public void testWriteTransactionConflictResolution() {
        // Create two transactions that write to the same resource concurrently.
        Transaction txA = new Transaction("txA");
        txA.addOperation(new Operation("res1", OperationType.WRITE, "dataA"));
        TransactionOutcome outcomeA = coordinator.process(txA);

        Transaction txB = new Transaction("txB");
        txB.addOperation(new Operation("res1", OperationType.WRITE, "dataB"));
        TransactionOutcome outcomeB = coordinator.process(txB);

        // Verify that a conflict resolution occurred and that the coordinator notifies affected transactions.
        List<String> notifications = outcomeB.getConflictNotifications();
        // At least one notification should be issued regarding the conflict.
        assertFalse(notifications.isEmpty());

        // Assuming last-write-wins resolution, final state should reflect txB's write.
        Map<String, String> resourceStates = outcomeB.getResourceStates();
        assertEquals("dataB", resourceStates.get("res1"));
    }

    @Test
    public void testFaultTolerance_NodeFailure() {
        // Simulate a node failure for a specific resource.
        coordinator.simulateNodeFailure("res2");

        Transaction transaction = new Transaction("tx3");
        transaction.addOperation(new Operation("res2", OperationType.WRITE, "data2"));
        TransactionOutcome outcome = coordinator.process(transaction);

        // The coordinator should eventually commit the transaction even if the node was initially unavailable.
        assertEquals("COMMIT", outcome.getStatus());
        assertEquals("data2", outcome.getResourceStates().get("res2"));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int numThreads = 10;
        List<Thread> threads = new ArrayList<>();
        List<TransactionOutcome> outcomes = Collections.synchronizedList(new ArrayList<>());

        for (int i = 0; i < numThreads; i++) {
            final int idx = i;
            Thread t = new Thread(() -> {
                Transaction transaction = new Transaction("tx_concurrent_" + idx);
                transaction.addOperation(new Operation("res_concurrent", OperationType.WRITE, "data_" + idx));
                TransactionOutcome outcome = coordinator.process(transaction);
                outcomes.add(outcome);
            });
            threads.add(t);
        }

        for (Thread t : threads) {
            t.start();
        }
        for (Thread t : threads) {
            t.join();
        }

        // Check that all transactions have eventually committed.
        for (TransactionOutcome outcome : outcomes) {
            assertEquals("COMMIT", outcome.getStatus());
        }

        // Validate that the final state of the shared resource is one of the expected values.
        Map<String, String> resourceStates = outcomes.get(0).getResourceStates();
        String finalData = resourceStates.get("res_concurrent");
        assertNotNull(finalData);
        boolean validFinalData = false;
        for (int i = 0; i < numThreads; i++) {
            if (finalData.equals("data_" + i)) {
                validFinalData = true;
                break;
            }
        }
        assertTrue(validFinalData);
    }
}