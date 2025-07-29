import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class InventoryService implements TransactionParticipant {
    private final Map<String, InventoryReservation> preparedReservations = new ConcurrentHashMap<>();
    private final Map<String, InventoryReservation> confirmedReservations = new ConcurrentHashMap<>();

    @Override
    public boolean prepare(String txId) {
        if (preparedReservations.containsKey(txId) || confirmedReservations.containsKey(txId)) {
            return true;
        }
        preparedReservations.put(txId, new InventoryReservation(txId));
        return true;
    }

    @Override
    public boolean commit(String txId) {
        InventoryReservation reservation = preparedReservations.remove(txId);
        if (reservation != null) {
            confirmedReservations.put(txId, reservation);
            return true;
        }
        return confirmedReservations.containsKey(txId);
    }

    @Override
    public boolean rollback(String txId) {
        preparedReservations.remove(txId);
        return true;
    }

    private static class InventoryReservation {
        private final String txId;

        public InventoryReservation(String txId) {
            this.txId = txId;
        }
    }
}