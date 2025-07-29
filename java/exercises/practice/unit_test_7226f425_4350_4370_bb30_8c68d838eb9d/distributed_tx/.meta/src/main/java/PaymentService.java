package distributed_tx;

public class PaymentService {

    public boolean processPayment(Order order) {
        if (order.isSimulatePaymentFailure()) {
            return false;
        }
        return true;
    }
    
    public void refundPayment(Order order) {
        // Simulate refund processing (no actual operation)
    }
}