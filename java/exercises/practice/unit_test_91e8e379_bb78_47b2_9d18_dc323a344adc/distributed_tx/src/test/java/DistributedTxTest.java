package distributed_tx;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {

    @Test
    public void testSuccessfulTransaction() {
        TransactionManager tm = new TransactionManager();
        TestResourceManager rm1 = new TestResourceManager("rm1", true, 0);
        TestResourceManager rm2 = new TestResourceManager("rm2", true, 0);

        tm.registerResourceManager(rm1);
        tm.registerResourceManager(rm2);

        String txid = tm.beginTransaction();

        // Simulate the prepare phase
        String vote1 = rm1.prepare(txid, "operation_data_1");
        tm.receiveVote(txid, rm1.getId(), vote1);
        String vote2 = rm2.prepare(txid, "operation_data_2");
        tm.receiveVote(txid, rm2.getId(), vote2);

        // Run the 2PC protocol
        tm.runTransaction(txid);

        // Validate that commit was called on both resource managers.
        assertTrue(rm1.isCommitted(), "Resource Manager rm1 should have committed the transaction.");
        assertTrue(rm2.isCommitted(), "Resource Manager rm2 should have committed the transaction.");
    }

    @Test
    public void testAbortTransactionDueToAbortVote() {
        TransactionManager tm = new TransactionManager();
        TestResourceManager rm1 = new TestResourceManager("rm1", true, 0);
        TestResourceManager rm2 = new TestResourceManager("rm2", false, 0); // This RM will vote abort.

        tm.registerResourceManager(rm1);
        tm.registerResourceManager(rm2);

        String txid = tm.beginTransaction();

        // Simulate the prepare phase
        String vote1 = rm1.prepare(txid, "operation_data_1");
        tm.receiveVote(txid, rm1.getId(), vote1);
        String vote2 = rm2.prepare(txid, "operation_data_2");
        tm.receiveVote(txid, rm2.getId(), vote2);

        // Run the 2PC protocol
        tm.runTransaction(txid);

        // Validate that abort was called on both resource managers.
        assertTrue(rm1.isAborted(), "Resource Manager rm1 should have aborted the transaction.");
        assertTrue(rm2.isAborted(), "Resource Manager rm2 should have aborted the transaction.");
    }

    @Test
    public void testAbortTransactionDueToTimeout() {
        TransactionManager tm = new TransactionManager();
        TestResourceManager rm1 = new TestResourceManager("rm1", true, 0);
        // This RM simulates delay causing a timeout in the TransactionManager.
        TestResourceManager rm2 = new TestResourceManager("rm2", true, 5000);

        tm.registerResourceManager(rm1);
        tm.registerResourceManager(rm2);

        String txid = tm.beginTransaction();

        // Simulate the prepare phase for rm1 immediately.
        String vote1 = rm1.prepare(txid, "operation_data_1");
        tm.receiveVote(txid, rm1.getId(), vote1);
        // Do not call prepare for rm2 immediately to simulate a timeout.

        // Run the 2PC protocol (the Transaction Manager should handle the missing vote with a timeout).
        tm.runTransaction(txid);

        // Validate that the transaction was aborted due to timeout.
        assertTrue(rm1.isAborted(), "Resource Manager rm1 should have aborted the transaction due to timeout.");
        assertTrue(rm2.isAborted(), "Resource Manager rm2 should have aborted the transaction due to timeout.");
    }

    // Helper class for unit testing that extends the ResourceManager.
    private static class TestResourceManager extends ResourceManager {
        private final String id;
        private final boolean voteCommit;
        private final long delayMillis;
        private boolean committed = false;
        private boolean aborted = false;

        public TestResourceManager(String id, boolean voteCommit, long delayMillis) {
            this.id = id;
            this.voteCommit = voteCommit;
            this.delayMillis = delayMillis;
        }

        public String getId() {
            return id;
        }

        @Override
        public String prepare(String txid, String operationData) {
            if (delayMillis > 0) {
                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            return voteCommit ? "commit" : "abort";
        }

        @Override
        public void commit(String txid) {
            committed = true;
        }

        @Override
        public void abort(String txid) {
            aborted = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isAborted() {
            return aborted;
        }
    }
}