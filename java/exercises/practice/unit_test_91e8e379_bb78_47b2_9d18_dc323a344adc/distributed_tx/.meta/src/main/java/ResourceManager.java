package distributed_tx;

public abstract class ResourceManager {
    /**
     * Prepares the resource for the transaction.
     * @param txid The transaction ID.
     * @param operationData Data required for the operation.
     * @return "commit" if prepared successfully, otherwise "abort".
     */
    public abstract String prepare(String txid, String operationData);

    /**
     * Commits the transaction.
     * @param txid The transaction ID.
     */
    public abstract void commit(String txid);

    /**
     * Aborts the transaction.
     * @param txid The transaction ID.
     */
    public abstract void abort(String txid);
}