package distributed_tx;

public interface ServiceRegistry {
    boolean execute(String service, String operation, String data);
    boolean compensate(String service, String operation, String data);
}