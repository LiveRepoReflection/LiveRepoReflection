package distributed_tx;

public interface DataNode {
    boolean prepareTransaction(String txId) throws Exception;
    void commitTransaction(String txId) throws Exception;
    void abortTransaction(String txId) throws Exception;
    String getNodeName();
}