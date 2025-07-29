public interface Service {
    int getId();
    boolean commit();
    boolean rollback();
}