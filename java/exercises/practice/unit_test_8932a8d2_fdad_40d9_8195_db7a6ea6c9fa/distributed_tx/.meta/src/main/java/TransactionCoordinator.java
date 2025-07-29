package distributed_tx;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class TransactionCoordinator {
    private final List<BankServer> bankServers;
    private final Set<String> processedTransactions;

    public TransactionCoordinator() {
        bankServers = new ArrayList<>();
        processedTransactions = new HashSet<>();
    }

    public void registerBankServer(BankServer bankServer) {
        bankServers.add(bankServer);
    }

    public boolean initiateTransaction(Transaction tx) {
        synchronized (processedTransactions) {
            if (processedTransactions.contains(tx.getId())) {
                return false;
            }
        }

        BankServer sourceServer = null;
        BankServer destinationServer = null;
        for (BankServer bs : bankServers) {
            if (sourceServer == null && bs.hasAccount(tx.getSource())) {
                sourceServer = bs;
            }
            if (destinationServer == null && bs.hasAccount(tx.getDestination())) {
                destinationServer = bs;
            }
            if (sourceServer != null && destinationServer != null) {
                break;
            }
        }
        if (sourceServer == null || destinationServer == null) {
            return false;
        }

        boolean sourcePrepared = sourceServer.prepareSource(tx.getId(), tx.getSource(), tx.getAmount());
        boolean destPrepared = destinationServer.prepareDestination(tx.getId(), tx.getDestination());

        if (!sourcePrepared || !destPrepared) {
            if (sourcePrepared) {
                sourceServer.abortTransaction(tx.getId(), tx.getSource());
            }
            if (destPrepared) {
                destinationServer.abortTransaction(tx.getId(), tx.getDestination());
            }
            return false;
        }

        // Phase 2: Commit the transaction on both servers.
        sourceServer.commitTransaction(tx.getId(), tx.getSource(), tx.getAmount(), true);
        destinationServer.commitTransaction(tx.getId(), tx.getDestination(), tx.getAmount(), false);

        synchronized (processedTransactions) {
            processedTransactions.add(tx.getId());
        }
        return true;
    }
}