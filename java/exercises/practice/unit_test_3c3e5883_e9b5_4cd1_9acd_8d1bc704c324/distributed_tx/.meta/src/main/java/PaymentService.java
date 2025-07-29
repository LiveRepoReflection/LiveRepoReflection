import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class PaymentService implements TransactionParticipant {
    private final Map<String, Payment> preparedPayments = new ConcurrentHashMap<>();
    private final Map<String, Payment> confirmedPayments = new ConcurrentHashMap<>();

    @Override
    public boolean prepare(String txId) {
        if (preparedPayments.containsKey(txId) || confirmedPayments.containsKey(txId)) {
            return true;
        }
        preparedPayments.put(txId, new Payment(txId));
        return true;
    }

    @Override
    public boolean commit(String txId) {
        Payment payment = preparedPayments.remove(txId);
        if (payment != null) {
            confirmedPayments.put(txId, payment);
            return true;
        }
        return confirmedPayments.containsKey(txId);
    }

    @Override
    public boolean rollback(String txId) {
        preparedPayments.remove(txId);
        return true;
    }

    private static class Payment {
        private final String txId;

        public Payment(String txId) {
            this.txId = txId;
        }
    }
}