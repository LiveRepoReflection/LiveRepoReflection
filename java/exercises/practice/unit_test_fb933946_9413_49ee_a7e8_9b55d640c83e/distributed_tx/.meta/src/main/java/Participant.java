public interface Participant {
    String prepare();
    void commit();
    void rollback();
    // Returns whether the participant successfully completed the prepare phase.
    boolean isPrepared();
}