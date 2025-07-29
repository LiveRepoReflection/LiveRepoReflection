import java.util.*;

public class TransactionCoordinatorMain {
    public static void main(String[] args) {
        List<Shard> shards = new ArrayList<>();
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());

        Coordinator coordinator = new Coordinator(shards, 1000);
        String txId = "tx_main";
        boolean result = coordinator.executeTransaction(txId, "update order");

        System.out.println("Transaction " + txId + " result: " + (result ? "COMMITTED" : "ABORTED"));
        System.out.println("Coordinator log status: " + coordinator.getTransactionStatus(txId));
        for (Shard shard : shards) {
            System.out.println("Shard status for " + txId + ": " + shard.getStatus(txId));
        }
    }
}