package tx_coordinator;

import java.util.Map;

public interface StorageNode {
    boolean prepare(Operation op);

    void commit(Operation op);

    void abort(Operation op);

    String getNodeId();

    void sendGossip(String transactionId, Map<String, Boolean> statusMap);
}