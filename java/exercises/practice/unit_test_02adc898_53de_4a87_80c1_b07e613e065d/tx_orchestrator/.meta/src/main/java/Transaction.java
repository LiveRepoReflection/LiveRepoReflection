public interface Transaction {
    boolean commit();
    boolean rollback();
}