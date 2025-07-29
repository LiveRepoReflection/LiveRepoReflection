import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinatorTest {

    @Test
    public void testCommitTransaction() throws InterruptedException {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        UUID txnId = UUID.randomUUID();
        Set<Integer> nodes = Set.of(0, 1, 2);
        coordinator.startTransaction(txnId, nodes);

        // All nodes vote to commit.
        coordinator.receiveVote(txnId, 0, true);
        coordinator.receiveVote(txnId, 1, true);
        coordinator.receiveVote(txnId, 2, true);

        // Allow a brief pause for internal processing.
        Thread.sleep(100);
        
        TransactionState state = coordinator.getTransactionState(txnId);
        assertEquals(TransactionState.COMMITTED, state, "Expected COMMITTED state when all nodes vote commit");
    }

    @Test
    public void testAbortTransactionByNegativeVote() throws InterruptedException {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        UUID txnId = UUID.randomUUID();
        Set<Integer> nodes = Set.of(0, 1, 2);
        coordinator.startTransaction(txnId, nodes);

        // One node votes abort.
        coordinator.receiveVote(txnId, 0, true);
        coordinator.receiveVote(txnId, 1, false);
        coordinator.receiveVote(txnId, 2, true);

        Thread.sleep(100);

        TransactionState state = coordinator.getTransactionState(txnId);
        assertEquals(TransactionState.ABORTED, state, "Expected ABORTED state when any node votes abort");
    }

    @Test
    public void testAbortTransactionByNodeFailure() throws InterruptedException {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        UUID txnId = UUID.randomUUID();
        Set<Integer> nodes = Set.of(0, 1, 2, 3);
        coordinator.startTransaction(txnId, nodes);

        // Some nodes vote commit.
        coordinator.receiveVote(txnId, 0, true);
        coordinator.receiveVote(txnId, 1, true);
        
        // Simulate a node failure for a node that has not voted.
        coordinator.handleNodeFailure(2);
        
        // Remaining node votes commit.
        coordinator.receiveVote(txnId, 3, true);

        Thread.sleep(100);

        TransactionState state = coordinator.getTransactionState(txnId);
        assertEquals(TransactionState.ABORTED, state, "Expected ABORTED state when a node fails before voting");
    }

    @Test
    public void testDuplicateOperations() throws InterruptedException {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        UUID txnId = UUID.randomUUID();
        Set<Integer> nodes = Set.of(0, 1);
        coordinator.startTransaction(txnId, nodes);

        // Duplicate votes should be idempotent.
        coordinator.receiveVote(txnId, 0, true);
        coordinator.receiveVote(txnId, 0, true);
        coordinator.receiveVote(txnId, 1, true);
        coordinator.receiveVote(txnId, 1, true);

        // Duplicate failure calls for an unrelated node.
        coordinator.handleNodeFailure(5);
        coordinator.handleNodeFailure(5);

        Thread.sleep(100);
        TransactionState state = coordinator.getTransactionState(txnId);
        assertEquals(TransactionState.COMMITTED, state, "Duplicate operations should not affect the outcome");
    }

    @Test
    public void testTimeoutTransaction() throws InterruptedException {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        UUID txnId = UUID.randomUUID();
        // Transaction with two nodes where one never votes.
        Set<Integer> nodes = Set.of(0, 1);
        coordinator.startTransaction(txnId, nodes);

        // Only one node votes commit.
        coordinator.receiveVote(txnId, 0, true);

        // Wait longer than the specified timeout (assumed 10 seconds).
        Thread.sleep(11000);

        TransactionState state = coordinator.getTransactionState(txnId);
        assertEquals(TransactionState.ABORTED, state, "Expected ABORTED state when a transaction times out");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        ExecutorService executor = Executors.newFixedThreadPool(5);
        int transactionCount = 10;
        CountDownLatch latch = new CountDownLatch(transactionCount);
        ConcurrentHashMap<UUID, TransactionState> results = new ConcurrentHashMap<>();

        for (int i = 0; i < transactionCount; i++) {
            executor.submit(() -> {
                UUID txnId = UUID.randomUUID();
                Set<Integer> nodes = Set.of(0, 1, 2);
                coordinator.startTransaction(txnId, nodes);
                
                // Simulate votes from different nodes.
                coordinator.receiveVote(txnId, 0, true);
                coordinator.receiveVote(txnId, 1, true);
                if (ThreadLocalRandom.current().nextBoolean()) {
                    coordinator.receiveVote(txnId, 2, false);
                } else {
                    coordinator.receiveVote(txnId, 2, true);
                }
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                results.put(txnId, coordinator.getTransactionState(txnId));
                latch.countDown();
            });
        }

        latch.await(5, TimeUnit.SECONDS);
        executor.shutdownNow();

        // Verify that each transaction ends in either COMMITTED or ABORTED.
        for (TransactionState state : results.values()) {
            assertTrue(state == TransactionState.COMMITTED || state == TransactionState.ABORTED,
                "Each transaction should be either COMMITTED or ABORTED");
        }
    }
}