public interface Participant {
    Vote prepare() throws Exception;
    void commit();
    void rollback();
}