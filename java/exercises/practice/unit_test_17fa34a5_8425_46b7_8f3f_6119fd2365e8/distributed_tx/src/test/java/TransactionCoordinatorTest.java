package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assertions;

import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

// Dummy implementations for Resource, TransactionContext and TransactionCoordinator
// These dummy classes are for testing purposes only.
// They simulate various behaviors for prepare, commit and rollback based on constructor parameters.

class DummyTransactionContext extends TransactionContext {
    public DummyTransactionContext(UUID transactionId) {
        super(transactionId);
    }
}

interface Resource {
    boolean prepare(TransactionContext context) throws InterruptedException;
    boolean commit(TransactionContext context) throws InterruptedException;
    boolean rollback(TransactionContext context) throws InterruptedException;
}

class TransactionContext {
    private final UUID transactionId;
    public TransactionContext(UUID transactionId) {
        this.transactionId = transactionId;
    }
    public UUID getTransactionId() {
        return transactionId;
    }
}

class TransactionCoordinator {
    private final ConcurrentMap<UUID, List<Resource>> transactionResources = new ConcurrentHashMap<>();

    public TransactionContext beginTransaction() {
        TransactionContext context = new TransactionContext(UUID.randomUUID());
        transactionResources.put(context.getTransactionId(), new CopyOnWriteArrayList<>());
        return context;
    }

    public void enlistResource(TransactionContext context, Resource resource) {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources != null) {
            resources.add(resource);
        }
    }

    public void commitTransaction(TransactionContext context) throws Exception {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources == null) {
            throw new IllegalArgumentException("Transaction context not found");
        }
        // Phase 1: Prepare
        for (Resource resource : resources) {
            boolean prepared = resource.prepare(context);
            if (!prepared) {
                rollbackTransaction(context);
                return;
            }
        }
        // Phase 2: Commit
        List<Resource> committedResources = new ArrayList<>();
        for (Resource resource : resources) {
            boolean committed = resource.commit(context);
            if (!committed) {
                // Try to rollback all committed resources
                for (Resource r : committedResources) {
                    r.rollback(context);
                }
                // Also rollback the failed resource
                if (!resource.rollback(context)) {
                    throw new Exception("Rollback failed during commit phase");
                }
                throw new Exception("Commit failed and rollback completed");
            } else {
                committedResources.add(resource);
            }
        }
    }

    public void rollbackTransaction(TransactionContext context) throws Exception {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources == null) {
            throw new IllegalArgumentException("Transaction context not found");
        }
        Exception rollbackException = null;
        for (Resource resource : resources) {
            boolean rolledBack = resource.rollback(context);
            if (!rolledBack) {
                rollbackException = new Exception("Rollback failed for one or more resources");
            }
        }
        if (rollbackException != null) {
            throw rollbackException;
        }
    }
}

// Dummy resource that always succeeds.
class SuccessfulResource implements Resource {
    public final AtomicInteger prepareCalls = new AtomicInteger(0);
    public final AtomicInteger commitCalls = new AtomicInteger(0);
    public final AtomicInteger rollbackCalls = new AtomicInteger(0);

    @Override
    public boolean prepare(TransactionContext context) throws InterruptedException {
        prepareCalls.incrementAndGet();
        // Simulate work
        Thread.sleep(10);
        return true;
    }

    @Override
    public boolean commit(TransactionContext context) throws InterruptedException {
        commitCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }

    @Override
    public boolean rollback(TransactionContext context) throws InterruptedException {
        rollbackCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }
}

// Dummy resource that fails during prepare.
class PrepareFailureResource implements Resource {
    public final AtomicInteger prepareCalls = new AtomicInteger(0);
    public final AtomicInteger rollbackCalls = new AtomicInteger(0);

    @Override
    public boolean prepare(TransactionContext context) throws InterruptedException {
        prepareCalls.incrementAndGet();
        Thread.sleep(10);
        return false;
    }

    @Override
    public boolean commit(TransactionContext context) throws InterruptedException {
        // Should never be called
        return true;
    }

    @Override
    public boolean rollback(TransactionContext context) throws InterruptedException {
        rollbackCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }
}

// Dummy resource that fails during commit but succeeds in rollback.
class CommitFailureResource implements Resource {
    public final AtomicInteger prepareCalls = new AtomicInteger(0);
    public final AtomicInteger commitCalls = new AtomicInteger(0);
    public final AtomicInteger rollbackCalls = new AtomicInteger(0);

    @Override
    public boolean prepare(TransactionContext context) throws InterruptedException {
        prepareCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }

    @Override
    public boolean commit(TransactionContext context) throws InterruptedException {
        commitCalls.incrementAndGet();
        Thread.sleep(10);
        return false;
    }

    @Override
    public boolean rollback(TransactionContext context) throws InterruptedException {
        rollbackCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }
}

// Dummy resource that fails during commit and also fails during rollback.
class CommitAndRollbackFailureResource implements Resource {
    public final AtomicInteger prepareCalls = new AtomicInteger(0);
    public final AtomicInteger commitCalls = new AtomicInteger(0);
    public final AtomicInteger rollbackCalls = new AtomicInteger(0);

    @Override
    public boolean prepare(TransactionContext context) throws InterruptedException {
        prepareCalls.incrementAndGet();
        Thread.sleep(10);
        return true;
    }

    @Override
    public boolean commit(TransactionContext context) throws InterruptedException {
        commitCalls.incrementAndGet();
        Thread.sleep(10);
        return false;
    }

    @Override
    public boolean rollback(TransactionContext context) throws InterruptedException {
        rollbackCalls.incrementAndGet();
        Thread.sleep(10);
        return false;
    }
}

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new TransactionCoordinator();
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        TransactionContext context = coordinator.beginTransaction();
        SuccessfulResource resource1 = new SuccessfulResource();
        SuccessfulResource resource2 = new SuccessfulResource();

        coordinator.enlistResource(context, resource1);
        coordinator.enlistResource(context, resource2);

        // Expect commit to succeed without exceptions.
        coordinator.commitTransaction(context);
        Assertions.assertEquals(1, resource1.prepareCalls.get());
        Assertions.assertEquals(1, resource2.prepareCalls.get());
        Assertions.assertEquals(1, resource1.commitCalls.get());
        Assertions.assertEquals(1, resource2.commitCalls.get());
        // Rollback should not have been called in a successful transaction.
        Assertions.assertEquals(0, resource1.rollbackCalls.get());
        Assertions.assertEquals(0, resource2.rollbackCalls.get());
    }

    @Test
    public void testPrepareFailureTransaction() throws Exception {
        TransactionContext context = coordinator.beginTransaction();
        SuccessfulResource resource1 = new SuccessfulResource();
        PrepareFailureResource resource2 = new PrepareFailureResource();

        coordinator.enlistResource(context, resource1);
        coordinator.enlistResource(context, resource2);

        // commitTransaction should trigger rollback due to a prepare failure.
        coordinator.commitTransaction(context);
        // Verify prepares were called.
        Assertions.assertEquals(1, resource1.prepareCalls.get());
        Assertions.assertEquals(1, resource2.prepareCalls.get());
        // Since prepare failed for resource2, no commit should occur.
        Assertions.assertEquals(0, resource1.commitCalls.get());
        // Rollback should have been called on both.
        Assertions.assertTrue(resource1.rollbackCalls.get() > 0);
        Assertions.assertEquals(1, resource2.rollbackCalls.get());
    }

    @Test
    public void testCommitFailureWithSuccessfulRollback() {
        TransactionContext context = coordinator.beginTransaction();
        SuccessfulResource resource1 = new SuccessfulResource();
        CommitFailureResource resource2 = new CommitFailureResource();

        coordinator.enlistResource(context, resource1);
        coordinator.enlistResource(context, resource2);

        Exception exception = Assertions.assertThrows(Exception.class, () -> {
            coordinator.commitTransaction(context);
        });
        Assertions.assertEquals(1, resource1.prepareCalls.get());
        Assertions.assertEquals(1, resource2.prepareCalls.get());
        // Commit was attempted for each resource.
        Assertions.assertEquals(1, resource1.commitCalls.get());
        Assertions.assertEquals(1, resource2.commitCalls.get());
        // Rollback should have been called on resource1 and resource2.
        Assertions.assertTrue(resource1.rollbackCalls.get() > 0);
        Assertions.assertEquals(1, resource2.rollbackCalls.get());
        Assertions.assertTrue(exception.getMessage().contains("Commit failed"));
    }

    @Test
    public void testCommitFailureWithRollbackFailure() {
        TransactionContext context = coordinator.beginTransaction();
        // Only resource that will fail commit and rollback.
        CommitAndRollbackFailureResource resource = new CommitAndRollbackFailureResource();
        coordinator.enlistResource(context, resource);

        Exception exception = Assertions.assertThrows(Exception.class, () -> {
            coordinator.commitTransaction(context);
        });
        Assertions.assertEquals(1, resource.prepareCalls.get());
        Assertions.assertEquals(1, resource.commitCalls.get());
        // Rollback is attempted and fails.
        Assertions.assertEquals(1, resource.rollbackCalls.get());
        Assertions.assertTrue(exception.getMessage().contains("Rollback failed"));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (int i = 0; i < numTransactions; i++) {
            tasks.add(() -> {
                TransactionContext context = coordinator.beginTransaction();
                SuccessfulResource resource1 = new SuccessfulResource();
                SuccessfulResource resource2 = new SuccessfulResource();
                coordinator.enlistResource(context, resource1);
                coordinator.enlistResource(context, resource2);
                try {
                    coordinator.commitTransaction(context);
                } catch (Exception e) {
                    return false;
                }
                return (resource1.commitCalls.get() == 1 && resource2.commitCalls.get() == 1);
            });
        }
        List<Future<Boolean>> results = executor.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            Assertions.assertTrue(future.get());
        }
        executor.shutdown();
    }
}