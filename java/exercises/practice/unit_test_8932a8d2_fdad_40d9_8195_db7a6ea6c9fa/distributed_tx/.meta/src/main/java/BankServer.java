package distributed_tx;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class BankServer {
    private final String name;
    private final Map<String, Integer> accounts;
    private final Map<String, String> lockedAccounts;
    private final Set<String> executedTransactions;
    private boolean available;

    public BankServer(String name) {
        this.name = name;
        this.accounts = new HashMap<>();
        this.lockedAccounts = new HashMap<>();
        this.executedTransactions = new HashSet<>();
        this.available = true;
    }

    public synchronized void createAccount(String accountId, int initialBalance) {
        accounts.put(accountId, initialBalance);
    }

    public synchronized boolean hasAccount(String accountId) {
        return accounts.containsKey(accountId);
    }

    public synchronized int getBalance(String accountId) {
        return accounts.getOrDefault(accountId, 0);
    }

    public synchronized void updateBalance(String accountId, int newBalance) {
        if (accounts.containsKey(accountId)) {
            accounts.put(accountId, newBalance);
        }
    }

    public synchronized void setAvailable(boolean available) {
        this.available = available;
    }

    public synchronized boolean isAvailable() {
        return available;
    }

    public synchronized boolean prepareSource(String transactionId, String accountId, int amount) {
        if (!available) {
            return false;
        }
        if (executedTransactions.contains(transactionId)) {
            return false;
        }
        if (!accounts.containsKey(accountId)) {
            return false;
        }
        if (lockedAccounts.containsKey(accountId)) {
            return false;
        }
        int currentBalance = accounts.get(accountId);
        if (currentBalance < amount) {
            return false;
        }
        // Lock the account by recording the transaction id.
        lockedAccounts.put(accountId, transactionId);
        return true;
    }

    public synchronized boolean prepareDestination(String transactionId, String accountId) {
        if (!available) {
            return false;
        }
        if (executedTransactions.contains(transactionId)) {
            return false;
        }
        if (!accounts.containsKey(accountId)) {
            return false;
        }
        // For destination account, check lock only if already locked by a different transaction.
        if (lockedAccounts.containsKey(accountId)) {
            return false;
        }
        lockedAccounts.put(accountId, transactionId);
        return true;
    }

    public synchronized void commitTransaction(String transactionId, String accountId, int amount, boolean isSource) {
        if (isSource) {
            int currentBalance = accounts.get(accountId);
            accounts.put(accountId, currentBalance - amount);
        } else {
            int currentBalance = accounts.get(accountId);
            accounts.put(accountId, currentBalance + amount);
        }
        executedTransactions.add(transactionId);
        // Release the lock if this transaction holds it.
        if (lockedAccounts.containsKey(accountId) && lockedAccounts.get(accountId).equals(transactionId)) {
            lockedAccounts.remove(accountId);
        }
    }

    public synchronized void abortTransaction(String transactionId, String accountId) {
        // Release the lock if held by this transaction.
        if (lockedAccounts.containsKey(accountId) && lockedAccounts.get(accountId).equals(transactionId)) {
            lockedAccounts.remove(accountId);
        }
    }
}