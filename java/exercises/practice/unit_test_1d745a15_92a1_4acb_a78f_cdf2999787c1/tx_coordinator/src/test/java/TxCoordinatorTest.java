import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class TxCoordinatorTest {

    // Dummy Bank Server to simulate network calls and operations
    static class DummyBankServer {
        String serverID;
        Map<String, Integer> accounts;
        Map<String, List<Operation>> pendingTransactions = new HashMap<>();

        public DummyBankServer(String serverID, Map<String, Integer> initialAccounts) {
            this.serverID = serverID;
            this.accounts = new HashMap<>(initialAccounts);
        }

        public boolean prepare(String transactionID, List<Operation> ops) {
            // Validate all withdraw operations have sufficient funds
            for (Operation op : ops) {
                if (op.operationType.equals("Withdraw")) {
                    int current = accounts.getOrDefault(op.accountID, 0);
                    if (current < op.amount) {
                        return false;
                    }
                }
            }
            pendingTransactions.put(transactionID, ops);
            return true;
        }

        public void commit(String transactionID) {
            List<Operation> ops = pendingTransactions.get(transactionID);
            if (ops != null) {
                for (Operation op : ops) {
                    if (op.operationType.equals("Deposit")) {
                        accounts.put(op.accountID, accounts.getOrDefault(op.accountID, 0) + op.amount);
                    } else if (op.operationType.equals("Withdraw")) {
                        accounts.put(op.accountID, accounts.getOrDefault(op.accountID, 0) - op.amount);
                    }
                }
                pendingTransactions.remove(transactionID);
            }
        }

        public void rollback(String transactionID) {
            pendingTransactions.remove(transactionID);
        }
        
        public int getBalance(String accountID) {
            return accounts.getOrDefault(accountID, 0);
        }
    }

    // Operation class to represent single bank operation
    static class Operation {
        String serverID;
        String accountID;
        String operationType; // "Deposit" or "Withdraw"
        int amount;

        public Operation(String serverID, String accountID, String operationType, int amount) {
            this.serverID = serverID;
            this.accountID = accountID;
            this.operationType = operationType;
            this.amount = amount;
        }
    }

    // Transaction class that contains a list of operations
    static class Transaction {
        String transactionID;
        List<Operation> operations;

        public Transaction(String transactionID, List<Operation> operations) {
            this.transactionID = transactionID;
            this.operations = operations;
        }
    }

    // TransactionCoordinator coordinating the two-phase commit protocol
    static class TransactionCoordinator {
        Map<String, DummyBankServer> servers;
        List<String> log = new ArrayList<>();

        public TransactionCoordinator(Map<String, DummyBankServer> servers) {
            this.servers = servers;
        }

        public boolean processTransaction(Transaction transaction) {
            // Group operations by serverID
            Map<String, List<Operation>> opsByServer = new HashMap<>();
            for (Operation op : transaction.operations) {
                opsByServer.computeIfAbsent(op.serverID, k -> new ArrayList<>()).add(op);
            }

            Map<String, Boolean> prepareResults = new HashMap<>();

            // Phase 1: Prepare
            for (Map.Entry<String, List<Operation>> entry : opsByServer.entrySet()) {
                String serverID = entry.getKey();
                DummyBankServer server = servers.get(serverID);
                boolean result = server.prepare(transaction.transactionID, entry.getValue());
                prepareResults.put(serverID, result);
                log.add("Prepared " + serverID + " " + result);
                if (!result) {
                    break;
                }
            }

            boolean allPrepared = prepareResults.values().stream().allMatch(b -> b);

            if (allPrepared) {
                // Phase 2: Commit on each server
                for (String serverID : opsByServer.keySet()) {
                    DummyBankServer server = servers.get(serverID);
                    server.commit(transaction.transactionID);
                    log.add("Committed " + serverID);
                }
                return true;
            } else {
                // Roll back for servers that successfully prepared
                for (Map.Entry<String, Boolean> entry : prepareResults.entrySet()) {
                    if (entry.getValue()) {
                        DummyBankServer server = servers.get(entry.getKey());
                        server.rollback(transaction.transactionID);
                        log.add("Rolled back " + entry.getKey());
                    }
                }
                return false;
            }
        }
    }

    TransactionCoordinator coordinator;
    DummyBankServer serverA;
    DummyBankServer serverB;

    @BeforeEach
    public void setup() {
        // Initialize two bank servers with initial account balances.
        Map<String, Integer> accountsA = new HashMap<>();
        accountsA.put("A1", 1000);
        accountsA.put("A2", 500);
        serverA = new DummyBankServer("A", accountsA);

        Map<String, Integer> accountsB = new HashMap<>();
        accountsB.put("B1", 2000);
        accountsB.put("B2", 1500);
        serverB = new DummyBankServer("B", accountsB);

        Map<String, DummyBankServer> servers = new HashMap<>();
        servers.put("A", serverA);
        servers.put("B", serverB);

        coordinator = new TransactionCoordinator(servers);
    }

    @Test
    public void testSingleServerCommitTransaction() {
        List<Operation> ops = new ArrayList<>();
        ops.add(new Operation("A", "A1", "Withdraw", 200));
        ops.add(new Operation("A", "A2", "Deposit", 200));

        Transaction transaction = new Transaction("tx1", ops);
        boolean result = coordinator.processTransaction(transaction);
        assertTrue(result);
        assertEquals(800, serverA.getBalance("A1"));
        assertEquals(700, serverA.getBalance("A2"));
    }

    @Test
    public void testMultiServerCommitTransaction() {
        List<Operation> ops = new ArrayList<>();
        ops.add(new Operation("A", "A1", "Withdraw", 300));
        ops.add(new Operation("B", "B1", "Deposit", 300));

        Transaction transaction = new Transaction("tx2", ops);
        boolean result = coordinator.processTransaction(transaction);
        assertTrue(result);
        assertEquals(700, serverA.getBalance("A1"));
        assertEquals(2300, serverB.getBalance("B1"));
    }

    @Test
    public void testTransactionRollbackDueToInsufficientFunds() {
        List<Operation> ops = new ArrayList<>();
        ops.add(new Operation("A", "A2", "Withdraw", 600)); // insufficient funds
        ops.add(new Operation("B", "B2", "Deposit", 600));

        Transaction transaction = new Transaction("tx3", ops);
        boolean result = coordinator.processTransaction(transaction);
        assertFalse(result);
        // Ensure account balances remain unchanged after rollback
        assertEquals(500, serverA.getBalance("A2"));
        assertEquals(1500, serverB.getBalance("B2"));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(2);

        Callable<Boolean> task1 = () -> {
            List<Operation> ops = new ArrayList<>();
            ops.add(new Operation("A", "A1", "Withdraw", 200));
            ops.add(new Operation("B", "B1", "Deposit", 200));
            Transaction tx = new Transaction("tx4", ops);
            return coordinator.processTransaction(tx);
        };

        Callable<Boolean> task2 = () -> {
            List<Operation> ops = new ArrayList<>();
            ops.add(new Operation("A", "A2", "Withdraw", 300));
            ops.add(new Operation("B", "B2", "Deposit", 300));
            Transaction tx = new Transaction("tx5", ops);
            return coordinator.processTransaction(tx);
        };

        Future<Boolean> future1 = executor.submit(task1);
        Future<Boolean> future2 = executor.submit(task2);

        boolean result1 = future1.get();
        boolean result2 = future2.get();

        assertTrue(result1);
        assertTrue(result2);
        
        // Validate final balances after concurrent transactions
        assertEquals(800, serverA.getBalance("A1"));
        assertEquals(200, serverA.getBalance("A2"));
        assertEquals(2200, serverB.getBalance("B1"));
        assertEquals(1800, serverB.getBalance("B2"));

        executor.shutdown();
    }

    @Test
    public void testLoggingForTransaction() {
        List<Operation> ops = new ArrayList<>();
        ops.add(new Operation("A", "A1", "Withdraw", 100));
        Transaction t = new Transaction("tx6", ops);
        coordinator.processTransaction(t);
        assertFalse(coordinator.log.isEmpty());
        boolean containsCommitOrRollback = coordinator.log.stream().anyMatch(entry ->
                entry.contains("Committed") || entry.contains("Rolled back"));
        assertTrue(containsCommitOrRollback);
    }
}