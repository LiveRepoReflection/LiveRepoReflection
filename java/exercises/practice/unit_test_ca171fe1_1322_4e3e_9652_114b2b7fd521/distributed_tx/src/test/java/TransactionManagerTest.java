import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TransactionManagerTest {

    private TransactionManager transactionManager;

    @BeforeEach
    public void setUp() {
        // Initialize the TransactionManager instance before each test.
        transactionManager = new TransactionManager();
    }

    @Test
    public void testBeginTransaction() {
        String txid = transactionManager.begin();
        assertNotNull(txid);
        String status = transactionManager.getTransactionStatus(txid);
        // Assuming that a newly created transaction has status "preparing"
        assertEquals("preparing", status);
    }

    @Test
    public void testSuccessfulCommit() {
        String txid = transactionManager.begin();
        // Simulate successful prepare responses for all services.
        // The service simulation logic uses the operationDetails: if it contains "fail", it returns abort.
        transactionManager.prepare(txid, "order", "order_ok");
        transactionManager.prepare(txid, "payment", "payment_ok");
        transactionManager.prepare(txid, "inventory", "inventory_ok");
        
        // All services have responded with prepared then commit the transaction.
        transactionManager.commit(txid);
        String status = transactionManager.getTransactionStatus(txid);
        assertEquals("committed", status);
    }

    @Test
    public void testAbortDueToFailureInPrepare() {
        String txid = transactionManager.begin();
        // Simulate two successful prepares and one prepare failure.
        transactionManager.prepare(txid, "order", "order_ok");
        transactionManager.prepare(txid, "payment", "fail"); // This should simulate a failure.
        transactionManager.prepare(txid, "inventory", "inventory_ok");

        // When committing, the transaction manager should detect the failure and abort the transaction.
        transactionManager.commit(txid);
        String status = transactionManager.getTransactionStatus(txid);
        assertEquals("aborted", status);
    }

    @Test
    public void testIdempotencyOnCommit() {
        String txid = transactionManager.begin();
        transactionManager.prepare(txid, "order", "order_ok");
        transactionManager.prepare(txid, "payment", "payment_ok");
        transactionManager.prepare(txid, "inventory", "inventory_ok");

        // Call commit twice.
        transactionManager.commit(txid);
        transactionManager.commit(txid);
        String status = transactionManager.getTransactionStatus(txid);
        // The final status should remain committed.
        assertEquals("committed", status);
    }

    @Test
    public void testIdempotencyOnAbort() {
        String txid = transactionManager.begin();
        transactionManager.prepare(txid, "order", "order_ok");
        transactionManager.prepare(txid, "payment", "fail"); // Causes failure.
        transactionManager.prepare(txid, "inventory", "inventory_ok");

        // Abort multiple times.
        transactionManager.abort(txid);
        transactionManager.abort(txid);
        String status = transactionManager.getTransactionStatus(txid);
        // The final status should remain aborted.
        assertEquals("aborted", status);
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int numberOfTransactions = 50;
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        CountDownLatch latch = new CountDownLatch(numberOfTransactions);

        for (int i = 0; i < numberOfTransactions; i++) {
            tasks.add(() -> {
                try {
                    String txid = transactionManager.begin();
                    // All prepares succeed for this transaction.
                    transactionManager.prepare(txid, "order", "order_ok");
                    transactionManager.prepare(txid, "payment", "payment_ok");
                    transactionManager.prepare(txid, "inventory", "inventory_ok");
                    transactionManager.commit(txid);
                    String status = transactionManager.getTransactionStatus(txid);
                    return "committed".equals(status);
                } finally {
                    latch.countDown();
                }
            });
        }
        List<Future<Boolean>> results = executor.invokeAll(tasks);
        latch.await();
        for (Future<Boolean> future : results) {
            // Each transaction must commit successfully.
            assertEquals(true, future.get());
        }
        executor.shutdown();
    }
}