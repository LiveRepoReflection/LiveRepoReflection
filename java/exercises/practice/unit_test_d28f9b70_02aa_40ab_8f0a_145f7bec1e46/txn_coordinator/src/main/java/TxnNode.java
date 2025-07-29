import java.util.List;
import java.util.concurrent.CompletableFuture;

public interface TxnNode {
    /**
     * Prepare the given operations.
     * @param transactionId The transaction identifier.
     * @param operations List of operations for this node.
     * @return A CompletableFuture with the node's response.
     */
    CompletableFuture<NodeResponse> prepare(String transactionId, List<Operation> operations);

    /**
     * Commit the transaction.
     * @param transactionId The transaction identifier.
     * @return A CompletableFuture that completes when commit is done.
     */
    CompletableFuture<Void> commit(String transactionId);

    /**
     * Abort the transaction.
     * @param transactionId The transaction identifier.
     * @return A CompletableFuture that completes when abort is done.
     */
    CompletableFuture<Void> abort(String transactionId);
}