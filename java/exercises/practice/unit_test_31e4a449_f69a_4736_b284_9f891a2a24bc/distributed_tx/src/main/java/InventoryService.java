public interface InventoryService {
    /**
     * Attempts to decrement the stock of the item by the specified quantity.
     * @param itemId The ID of the item.
     * @param quantity The quantity to decrement.
     * @param transactionId The unique ID of the transaction.
     * @return true if the decrement was successful, false otherwise (e.g., due to insufficient stock or optimistic lock failure).
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    boolean decrementStock(String itemId, int quantity, String transactionId) throws ServiceUnavailableException;

    /**
     * Attempts to compensate for a previous decrementStock operation.
     * @param itemId The ID of the item.
     * @param quantity The quantity to increment back.
     * @param transactionId The unique ID of the transaction.
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    void compensateDecrementStock(String itemId, int quantity, String transactionId) throws ServiceUnavailableException;
}