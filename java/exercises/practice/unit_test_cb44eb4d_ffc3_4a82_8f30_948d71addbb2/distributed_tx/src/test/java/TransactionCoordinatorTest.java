package distributed_tx;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class TransactionCoordinatorTest {

    // Stub interface as defined in problem description
    interface BankServer {
        boolean prepare(Transaction transaction) throws Exception;
        void commit(Transaction transaction) throws Exception;
        void rollback(Transaction transaction) throws Exception;
    }

    // Stub Transaction class as defined in problem description
    interface Transaction {
        String transactionId();
        List<Operation> operations();
        Set<BankServer> participatingServers();
    }

    // Dummy Operation class
    static class Operation {
        // contents are not used in the test, just a placeholder
    }

    // A Test Implementation of BankServer for unit tests
    static class TestBankServer implements BankServer {
        private final String name;
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private final boolean rollbackSuccess;
        private final long prepareDelay;   // in milliseconds
        private final long commitDelay;    // in milliseconds
        private final long rollbackDelay;  // in milliseconds
        private final AtomicBoolean prepareCalled = new AtomicBoolean(false);
        private final AtomicBoolean commitCalled = new AtomicBoolean(false);
        private final AtomicBoolean rollbackCalled = new AtomicBoolean(false);
        private final boolean throwOnCommit;
        private final boolean throwOnRollback;

        public TestBankServer(String name,
                              boolean prepareSuccess,
                              boolean commitSuccess,
                              boolean rollbackSuccess,
                              long prepareDelay,
                              long commitDelay,
                              long rollbackDelay,
                              boolean throwOnCommit,
                              boolean throwOnRollback) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
            this.rollbackSuccess = rollbackSuccess;
            this.prepareDelay = prepareDelay;
            this.commitDelay = commitDelay;
            this.rollbackDelay = rollbackDelay;
            this.throwOnCommit = throwOnCommit;
            this.throwOnRollback = throwOnRollback;
        }

        public boolean wasPrepareCalled() {
            return prepareCalled.get();
        }

        public boolean wasCommitCalled() {
            return commitCalled.get();
        }

        public boolean wasRollbackCalled() {
            return rollbackCalled.get();
        }

        @Override
        public boolean prepare(Transaction transaction) throws Exception {
            prepareCalled.set(true);
            if (prepareDelay > 0) {
                Thread.sleep(prepareDelay);
            }
            return prepareSuccess;
        }

        @Override
        public void commit(Transaction transaction) throws Exception {
            commitCalled.set(true);
            if (commitDelay > 0) {
                Thread.sleep(commitDelay);
            }
            if (throwOnCommit) {
                throw new Exception("Commit failure on server " + name);
            }
            if (!commitSuccess) {
                throw new Exception("Commit reported as failure on server " + name);
            }
        }

        @Override
        public void rollback(Transaction transaction) throws Exception {
            rollbackCalled.set(true);
            if (rollbackDelay > 0) {
                Thread.sleep(rollbackDelay);
            }
            if (throwOnRollback) {
                throw new Exception("Rollback failure on server " + name);
            }
            if (!rollbackSuccess) {
                throw new Exception("Rollback reported as failure on server " + name);
            }
        }
    }

    // A Test Implementation of Transaction for unit tests
    static class TestTransaction implements Transaction {
        private final String id;
        private final List<Operation> ops;
        private final Set<BankServer> servers;

        public TestTransaction(String id, List<Operation> ops, Set<BankServer> servers) {
            this.id = id;
            this.ops = ops;
            this.servers = servers;
        }

        @Override
        public String transactionId() {
            return id;
        }

        @Override
        public List<Operation> operations() {
            return ops;
        }

        @Override
        public Set<BankServer> participatingServers() {
            return servers;
        }
    }

    // A simple TransactionCoordinator implementation stub for testing purposes.
    // In real scenario, this would be implemented in production code.
    static class TransactionCoordinator {
        private final ExecutorService executor = Executors.newCachedThreadPool();

        public boolean executeTransaction(Transaction transaction, int timeoutMillis) {
            Set<BankServer> servers = transaction.participatingServers();
            List<Future<Boolean>> prepareFutures = new ArrayList<>();
            // Phase 1: Prepare concurrently.
            for (BankServer server : servers) {
                Future<Boolean> future = executor.submit(() -> {
                    try {
                        return server.prepare(transaction);
                    } catch (Exception e) {
                        return false;
                    }
                });
                prepareFutures.add(future);
            }

            boolean allPrepared = true;
            long deadline = System.currentTimeMillis() + timeoutMillis;
            for (Future<Boolean> future : prepareFutures) {
                long timeLeft = deadline - System.currentTimeMillis();
                if (timeLeft <= 0) {
                    allPrepared = false;
                    break;
                }
                try {
                    Boolean result = future.get(timeLeft, TimeUnit.MILLISECONDS);
                    if (!result) {
                        allPrepared = false;
                        break;
                    }
                } catch (Exception e) {
                    allPrepared = false;
                    break;
                }
            }

            if (allPrepared) {
                // Phase 2: Commit concurrently.
                List<Future<Boolean>> commitFutures = new ArrayList<>();
                for (BankServer server : servers) {
                    Future<Boolean> future = executor.submit(() -> {
                        try {
                            server.commit(transaction);
                            return true;
                        } catch (Exception e) {
                            return false;
                        }
                    });
                    commitFutures.add(future);
                }
                boolean allCommitted = true;
                for (Future<Boolean> future : commitFutures) {
                    try {
                        Boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                        if (!result) {
                            allCommitted = false;
                            break;
                        }
                    } catch (Exception e) {
                        allCommitted = false;
                        break;
                    }
                }
                if (allCommitted) {
                    return true;
                }
            }
            // Rollback if prepare not all succeeded or commit failed.
            List<Future<Boolean>> rollbackFutures = new ArrayList<>();
            for (BankServer server : servers) {
                Future<Boolean> future = executor.submit(() -> {
                    try {
                        server.rollback(transaction);
                        return true;
                    } catch (Exception e) {
                        return false;
                    }
                });
                rollbackFutures.add(future);
            }
            boolean allRolledBack = true;
            for (Future<Boolean> future : rollbackFutures) {
                try {
                    Boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!result) {
                        allRolledBack = false;
                        break;
                    }
                } catch (Exception e) {
                    allRolledBack = false;
                    break;
                }
            }
            return allRolledBack ? false : false;
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        TestBankServer server1 = new TestBankServer("Server1", true, true, true, 0, 0, 0, false, false);
        TestBankServer server2 = new TestBankServer("Server2", true, true, true, 0, 0, 0, false, false);
        Set<BankServer> servers = new HashSet<>();
        servers.add(server1);
        servers.add(server2);
        TestTransaction transaction = new TestTransaction("tx1", new ArrayList<>(), servers);
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction(transaction, 2000);
        Assertions.assertTrue(result);
        Assertions.assertTrue(server1.wasPrepareCalled());
        Assertions.assertTrue(server2.wasPrepareCalled());
        Assertions.assertTrue(server1.wasCommitCalled());
        Assertions.assertTrue(server2.wasCommitCalled());
    }

    @Test
    public void testPrepareFailureTransaction() {
        TestBankServer server1 = new TestBankServer("Server1", false, true, true, 0, 0, 0, false, false);
        TestBankServer server2 = new TestBankServer("Server2", true, true, true, 0, 0, 0, false, false);
        Set<BankServer> servers = new HashSet<>();
        servers.add(server1);
        servers.add(server2);
        TestTransaction transaction = new TestTransaction("tx2", new ArrayList<>(), servers);
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction(transaction, 2000);
        Assertions.assertFalse(result);
        // Both servers should have been rolled back
        Assertions.assertTrue(server1.wasRollbackCalled());
        Assertions.assertTrue(server2.wasRollbackCalled());
    }

    @Test
    public void testPrepareTimeout() {
        // Simulate a delay in prepare that exceeds timeout for one server
        TestBankServer server1 = new TestBankServer("Server1", true, true, true, 3000, 0, 0, false, false);
        TestBankServer server2 = new TestBankServer("Server2", true, true, true, 0, 0, 0, false, false);
        Set<BankServer> servers = new HashSet<>();
        servers.add(server1);
        servers.add(server2);
        TestTransaction transaction = new TestTransaction("tx3", new ArrayList<>(), servers);
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction(transaction, 1000);
        Assertions.assertFalse(result);
        // Should trigger rollback on both servers
        Assertions.assertTrue(server1.wasRollbackCalled());
        Assertions.assertTrue(server2.wasRollbackCalled());
    }

    @Test
    public void testCommitFailureTransaction() {
        // Simulate a commit failure for one server
        TestBankServer server1 = new TestBankServer("Server1", true, false, true, 0, 0, 0, true, false);
        TestBankServer server2 = new TestBankServer("Server2", true, true, true, 0, 0, 0, false, false);
        Set<BankServer> servers = new HashSet<>();
        servers.add(server1);
        servers.add(server2);
        TestTransaction transaction = new TestTransaction("tx4", new ArrayList<>(), servers);
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction(transaction, 2000);
        Assertions.assertFalse(result);
        // Even though prepare succeeded, commit failure should cause rollback on both servers
        Assertions.assertTrue(server1.wasRollbackCalled());
        Assertions.assertTrue(server2.wasRollbackCalled());
    }

    @Test
    public void testRollbackFailureTransaction() {
        // Simulate a rollback failure for one server during rollback
        TestBankServer server1 = new TestBankServer("Server1", false, true, false, 0, 0, 0, false, true);
        TestBankServer server2 = new TestBankServer("Server2", true, true, true, 0, 0, 0, false, false);
        Set<BankServer> servers = new HashSet<>();
        servers.add(server1);
        servers.add(server2);
        TestTransaction transaction = new TestTransaction("tx5", new ArrayList<>(), servers);
        TransactionCoordinator coordinator = new TransactionCoordinator();
        boolean result = coordinator.executeTransaction(transaction, 2000);
        // Even if rollback is attempted, the rollback failure will yield a false outcome.
        Assertions.assertFalse(result);
        Assertions.assertTrue(server1.wasRollbackCalled());
        Assertions.assertTrue(server2.wasRollbackCalled());
    }
}