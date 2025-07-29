public interface Service {
    boolean prepare() throws Exception;
    boolean commit() throws Exception;
}