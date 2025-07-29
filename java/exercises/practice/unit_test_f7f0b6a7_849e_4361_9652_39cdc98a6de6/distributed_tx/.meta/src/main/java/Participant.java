public interface Participant {
    boolean prepare();
    void commit();
    void rollback();
}