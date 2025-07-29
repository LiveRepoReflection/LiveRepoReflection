public interface OrderService {
    /**
     * Attempts to create a new order record.
     * @param orderDetails The details of the order.
     * @param transactionId The unique ID of the transaction.
     * @return true if the order creation was successful, false otherwise (e.g., due to optimistic lock failure or data validation failure).
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    boolean createOrder(OrderDetails orderDetails, String transactionId) throws ServiceUnavailableException;

    /**
     * Attempts to compensate for a previous createOrder operation by deleting the order record.
     * @param orderId The ID of the order to delete.
     * @param transactionId The unique ID of the transaction.
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    void compensateCreateOrder(String orderId, String transactionId) throws ServiceUnavailableException;
}