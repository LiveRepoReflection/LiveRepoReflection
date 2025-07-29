public interface MicroserviceOperation {
    boolean prepare(long timeout) throws InterruptedException;
    void commit();
    void rollback();
}