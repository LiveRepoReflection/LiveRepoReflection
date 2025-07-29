public interface DistributedTransactionManager {
    /**
     * Executes a transaction involving inventory and order services.
     * 
     * @param itemId The ID of the item being ordered
     * @param quantity The quantity being ordered
     * @param customerId The ID of the customer placing the order
     * @param orderId The ID to be assigned to the new order
     * @return true if the transaction was successful, false otherwise
     */
    boolean executeTransaction(String itemId, int quantity, String customerId, String orderId);
}