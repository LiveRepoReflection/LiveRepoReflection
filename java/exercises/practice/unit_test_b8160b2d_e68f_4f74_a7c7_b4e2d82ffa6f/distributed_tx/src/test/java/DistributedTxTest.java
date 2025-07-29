import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import static org.junit.jupiter.api.Assertions.*;

// Dummy implementation of the ServiceParticipant interface for testing purposes.
// It is assumed that candidates implement the ServiceParticipant interface in their solution.
class DummyParticipant implements ServiceParticipant {
    private final String id;
    private final boolean prepareSuccess;
    private int commitCount = 0;
    private int rollbackCount = 0;
    private boolean prepared = false;

    public DummyParticipant(String id, boolean prepareSuccess) {
        this.id = id;
        this.prepareSuccess = prepareSuccess;
    }

    @Override
    public boolean prepare(String transactionId) {
        // Mark as prepared regardless of outcome to simulate idempotency.
        prepared = true;
        return prepareSuccess;
    }

    @Override
    public void commit(String transactionId) {
        commitCount++;
    }

    @Override
    public void rollback(String transactionId) {
        rollbackCount++;
    }

    public int getCommitCount() {
        return commitCount;
    }

    public int getRollbackCount() {
        return rollbackCount;
    }

    public boolean isPrepared() {
        return prepared;
    }
}

public class DistributedTxTest {

    private DistributedTransactionManager dtm;

    @BeforeEach
    public void setup() {
        dtm = new DistributedTransactionManager();
    }

    @Test
    public void testSuccessfulTransaction() {
        // All participants should successfully prepare and thus commit.
        DummyParticipant s1 = new DummyParticipant("S1", true);
        DummyParticipant s2 = new DummyParticipant("S2", true);
        DummyParticipant s3 = new DummyParticipant("S3", true);

        dtm.registerService("S1", s1);
        dtm.registerService("S2", s2);
        dtm.registerService("S3", s3);

        String txId = "tx-success";
        List<String> serviceIds = Arrays.asList("S1", "S2", "S3");
        boolean result = dtm.executeTransaction(txId, serviceIds);
        assertTrue(result, "Transaction should commit successfully");

        // Verify that commit was called exactly once on each participant.
        assertEquals(1, s1.getCommitCount());
        assertEquals(1, s2.getCommitCount());
        assertEquals(1, s3.getCommitCount());

        // Verify that no rollback was called.
        assertEquals(0, s1.getRollbackCount());
        assertEquals(0, s2.getRollbackCount());
        assertEquals(0, s3.getRollbackCount());
    }

    @Test
    public void testFailedTransaction() {
        // One participant fails during the prepare phase, causing a rollback.
        DummyParticipant s1 = new DummyParticipant("S1", true);
        DummyParticipant s2 = new DummyParticipant("S2", false); // This service will fail in prepare.
        DummyParticipant s3 = new DummyParticipant("S3", true);

        dtm.registerService("S1", s1);
        dtm.registerService("S2", s2);
        dtm.registerService("S3", s3);

        String txId = "tx-fail";
        List<String> serviceIds = Arrays.asList("S1", "S2", "S3");
        boolean result = dtm.executeTransaction(txId, serviceIds);
        assertFalse(result, "Transaction should rollback due to prepare failure");

        // Verify that rollback was called exactly once on each participant.
        assertEquals(1, s1.getRollbackCount());
        assertEquals(1, s2.getRollbackCount());
        assertEquals(1, s3.getRollbackCount());

        // Ensure no commit occurred.
        assertEquals(0, s1.getCommitCount());
        assertEquals(0, s2.getCommitCount());
        assertEquals(0, s3.getCommitCount());
    }

    @Test
    public void testIdempotentOperations() {
        // Verify that duplicate invocations of commit or rollback do not result in extra operations.
        DummyParticipant s1 = new DummyParticipant("S1", true);
        DummyParticipant s2 = new DummyParticipant("S2", true);

        dtm.registerService("S1", s1);
        dtm.registerService("S2", s2);

        String txId = "tx-idempotent";
        List<String> serviceIds = Arrays.asList("S1", "S2");
        boolean result = dtm.executeTransaction(txId, serviceIds);
        assertTrue(result, "Transaction should commit successfully");

        // Manually invoke commit and rollback to test idempotence.
        dtm.commitTransaction(txId, serviceIds);
        dtm.rollbackTransaction(txId, serviceIds);

        // Confirm that commit and rollback counts have not increased beyond the first successful call.
        assertEquals(1, s1.getCommitCount());
        assertEquals(1, s2.getCommitCount());
        assertEquals(0, s1.getRollbackCount());
        assertEquals(0, s2.getRollbackCount());
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        // Test concurrent execution of multiple transactions.
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        // Register a common set of services.
        Map<String, DummyParticipant> participants = new HashMap<>();
        for (int i = 1; i <= 5; i++) {
            DummyParticipant participant = new DummyParticipant("S" + i, true);
            participants.put("S" + i, participant);
            dtm.registerService("S" + i, participant);
        }

        for (int i = 0; i < numTransactions; i++) {
            final String txId = "tx-" + i;
            tasks.add(() -> {
                List<String> serviceIds = Arrays.asList("S1", "S2", "S3", "S4", "S5");
                return dtm.executeTransaction(txId, serviceIds);
            });
        }

        List<Future<Boolean>> futures = executor.invokeAll(tasks);
        int successCount = 0;
        for (Future<Boolean> future : futures) {
            if (future.get()) {
                successCount++;
            }
        }

        // All concurrent transactions should commit successfully.
        assertEquals(numTransactions, successCount, "All transactions should commit successfully");

        // Each participant should have committed for every transaction.
        for (int i = 1; i <= 5; i++) {
            DummyParticipant participant = participants.get("S" + i);
            assertEquals(numTransactions, participant.getCommitCount(),
                    "Participant S" + i + " should have commit count equal to number of transactions");
        }
        executor.shutdown();
    }
}