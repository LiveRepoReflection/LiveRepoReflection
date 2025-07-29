package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTxTest {

    // The DistributedTransactionManager and Participant interface are assumed to be implemented as follows:
    //
    // public class DistributedTransactionManager {
    //     public DistributedTransactionManager(long prepareTimeoutMillis, int maxRetries) { ... }
    //     public String beginTransaction() { ... }
    //     public void registerParticipant(String txId, Participant participant) { ... }
    //     public void executeTransaction(String txId) throws Exception { ... }
    //     public String getTransactionStatus(String txId) { ... }
    // }
    //
    // public interface Participant {
    //     boolean prepare() throws Exception;
    //     void commit() throws Exception;
    //     void rollback() throws Exception;
    // }
    //
    // The possible transaction statuses returned by getTransactionStatus(txId) are "COMMITTED" and "ROLLED_BACK".

    private DistributedTransactionManager dtm;

    @BeforeEach
    public void setup() {
        // For testing, we initialize the DTM with a prepare timeout of 500ms and maximum 3 commit retries.
        dtm = new DistributedTransactionManager(500, 3);
    }

    @Test
    public void testSuccessfulCommit() throws Exception {
        String txId = dtm.beginTransaction();
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() {
                // Successful commit; no-op.
            }

            @Override
            public void rollback() {
                fail("Rollback should not be called for a successful commit.");
            }
        });
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() {
                // Successful commit; no-op.
            }

            @Override
            public void rollback() {
                fail("Rollback should not be called for a successful commit.");
            }
        });
        dtm.executeTransaction(txId);
        assertEquals("COMMITTED", dtm.getTransactionStatus(txId));
    }

    @Test
    public void testRollbackDueToPrepareFailure() throws Exception {
        String txId = dtm.beginTransaction();
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() {
                fail("Commit should not be called when a prepare failure occurs.");
            }

            @Override
            public void rollback() {
                // Expected rollback.
            }
        });
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return false; // Simulate a prepare failure.
            }

            @Override
            public void commit() {
                fail("Commit should not be called when a prepare failure occurs.");
            }

            @Override
            public void rollback() {
                // Expected rollback.
            }
        });
        dtm.executeTransaction(txId);
        assertEquals("ROLLED_BACK", dtm.getTransactionStatus(txId));
    }

    @Test
    public void testTimeoutBehaviour() throws Exception {
        String txId = dtm.beginTransaction();
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() throws Exception {
                Thread.sleep(600); // Sleep longer than the configured timeout.
                return true;
            }

            @Override
            public void commit() {
                fail("Commit should not be invoked when a participant times out during prepare.");
            }

            @Override
            public void rollback() {
                // Expected rollback due to timeout.
            }
        });
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() {
                fail("Commit should not be invoked when a participant times out during prepare.");
            }

            @Override
            public void rollback() {
                // Expected rollback.
            }
        });
        dtm.executeTransaction(txId);
        assertEquals("ROLLED_BACK", dtm.getTransactionStatus(txId));
    }

    @Test
    public void testIdempotentCommit() throws Exception {
        AtomicInteger commitCounter = new AtomicInteger(0);
        String txId = dtm.beginTransaction();
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() {
                commitCounter.incrementAndGet();
            }

            @Override
            public void rollback() {
                fail("Rollback should not be called during a successful commit.");
            }
        });
        dtm.executeTransaction(txId);
        // Even if the DTM sends duplicate commit calls, the participant's commit should execute only once.
        assertEquals(1, commitCounter.get());
        assertEquals("COMMITTED", dtm.getTransactionStatus(txId));
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        CountDownLatch latch = new CountDownLatch(numTransactions);
        ConcurrentLinkedQueue<String> txIds = new ConcurrentLinkedQueue<>();

        for (int i = 0; i < numTransactions; i++) {
            executor.submit(() -> {
                try {
                    String txId = dtm.beginTransaction();
                    txIds.add(txId);
                    dtm.registerParticipant(txId, new Participant() {
                        @Override
                        public boolean prepare() {
                            return true;
                        }

                        @Override
                        public void commit() {
                            // No-op commit.
                        }

                        @Override
                        public void rollback() {
                            fail("Rollback should not occur in concurrent successful transactions.");
                        }
                    });
                    dtm.executeTransaction(txId);
                } catch (Exception e) {
                    fail("Exception in concurrent transaction: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        assertTrue(latch.await(5, TimeUnit.SECONDS), "Timeout waiting for concurrent transactions.");
        executor.shutdownNow();
        for (String txId : txIds) {
            assertEquals("COMMITTED", dtm.getTransactionStatus(txId));
        }
    }

    @Test
    public void testRetryCommitMechanism() throws Exception {
        String txId = dtm.beginTransaction();
        AtomicInteger commitAttempts = new AtomicInteger(0);
        dtm.registerParticipant(txId, new Participant() {
            @Override
            public boolean prepare() {
                return true;
            }

            @Override
            public void commit() throws Exception {
                int attempt = commitAttempts.incrementAndGet();
                if (attempt < 2) {
                    throw new Exception("Simulated commit failure on attempt " + attempt);
                }
            }

            @Override
            public void rollback() {
                fail("Rollback should not be invoked if commit eventually succeeds.");
            }
        });
        dtm.executeTransaction(txId);
        assertEquals("COMMITTED", dtm.getTransactionStatus(txId));
        assertTrue(commitAttempts.get() >= 2, "Commit method should have been retried at least once.");
    }
}