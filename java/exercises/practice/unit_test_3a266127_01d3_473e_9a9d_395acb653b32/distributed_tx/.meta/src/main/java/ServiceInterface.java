import java.util.concurrent.Callable;

/**
 * Interface defining the operations that services must support for the distributed transaction manager.
 */
public interface ServiceInterface {
    /**
     * Executes an operation on the service.
     * 
     * @param operation the operation to execute
     * @return the result of the operation execution
     */
    boolean execute(Callable<Boolean> operation);
    
    /**
     * Executes a rollback operation on the service.
     * 
     * @param rollbackOperation the rollback operation to execute
     * @return the result of the rollback operation execution
     */
    boolean rollback(Callable<Boolean> rollbackOperation);
}