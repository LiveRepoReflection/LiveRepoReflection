public interface DataNode {
    boolean prepare(int transactionId) throws RemoteException; // Returns true for vote-commit, false for vote-abort
    void commit(int transactionId) throws RemoteException;
    void abort(int transactionId) throws RemoteException;
    boolean isAvailable();
}