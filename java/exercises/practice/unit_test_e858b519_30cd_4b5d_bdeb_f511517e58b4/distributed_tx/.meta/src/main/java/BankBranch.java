package distributed_tx;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Map;

public class BankBranch {
    private String branchId;
    private Map<String, Double> accounts;
    private Map<String, Transaction> preparedTransactions;
    private Map<String, ReentrantLock> accountLocks;

    public BankBranch(String branchId) {
        this.branchId = branchId;
        accounts = new ConcurrentHashMap<>();
        preparedTransactions = new ConcurrentHashMap<>();
        accountLocks = new ConcurrentHashMap<>();
    }

    public String getBranchId() {
        return branchId;
    }

    public void createAccount(String accountId, double initialBalance) {
        accounts.put(accountId, initialBalance);
        accountLocks.put(accountId, new ReentrantLock());
    }

    public double getAccountBalance(String accountId) {
        Double balance = accounts.get(accountId);
        return balance == null ? 0.0 : balance;
    }

    public boolean prepare(Transaction tx) {
        boolean isDebit = tx.getSourceAccountId().startsWith(branchId);
        boolean isCredit = tx.getDestinationAccountId().startsWith(branchId);

        if (!isDebit && !isCredit) {
            return true;
        }

        // Lock debit account if applicable.
        if (isDebit) {
            ReentrantLock debitLock = accountLocks.get(tx.getSourceAccountId());
            if (debitLock == null) {
                return false;
            }
            debitLock.lock();
            Double currentBalance = accounts.get(tx.getSourceAccountId());
            if (currentBalance == null || currentBalance < tx.getAmount()) {
                debitLock.unlock();
                return false;
            }
        }

        // Lock credit account if applicable.
        if (isCredit) {
            ReentrantLock creditLock = accountLocks.get(tx.getDestinationAccountId());
            if (creditLock == null) {
                if (isDebit) {
                    accountLocks.get(tx.getSourceAccountId()).unlock();
                }
                return false;
            }
            creditLock.lock();
            if (!accounts.containsKey(tx.getDestinationAccountId())) {
                if (isDebit) {
                    accountLocks.get(tx.getSourceAccountId()).unlock();
                }
                creditLock.unlock();
                return false;
            }
        }

        preparedTransactions.put(tx.getTransactionId(), tx);
        return true;
    }

    public void commit(Transaction tx) {
        boolean isDebit = tx.getSourceAccountId().startsWith(branchId);
        boolean isCredit = tx.getDestinationAccountId().startsWith(branchId);

        if (isDebit) {
            ReentrantLock debitLock = accountLocks.get(tx.getSourceAccountId());
            Double currentBalance = accounts.get(tx.getSourceAccountId());
            accounts.put(tx.getSourceAccountId(), currentBalance - tx.getAmount());
            debitLock.unlock();
        }

        if (isCredit) {
            ReentrantLock creditLock = accountLocks.get(tx.getDestinationAccountId());
            Double currentBalance = accounts.get(tx.getDestinationAccountId());
            accounts.put(tx.getDestinationAccountId(), currentBalance + tx.getAmount());
            creditLock.unlock();
        }

        preparedTransactions.remove(tx.getTransactionId());
    }

    public void abort(Transaction tx) {
        boolean isDebit = tx.getSourceAccountId().startsWith(branchId);
        boolean isCredit = tx.getDestinationAccountId().startsWith(branchId);

        if (isDebit) {
            ReentrantLock debitLock = accountLocks.get(tx.getSourceAccountId());
            debitLock.unlock();
        }
        if (isCredit) {
            ReentrantLock creditLock = accountLocks.get(tx.getDestinationAccountId());
            creditLock.unlock();
        }

        preparedTransactions.remove(tx.getTransactionId());
    }
}