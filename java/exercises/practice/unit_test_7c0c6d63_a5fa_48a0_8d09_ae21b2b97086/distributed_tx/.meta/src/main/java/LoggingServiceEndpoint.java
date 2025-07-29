import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * An example implementation of ServiceEndpoint that logs all operations.
 * This can be used as a reference for creating custom service endpoints.
 */
public class LoggingServiceEndpoint implements ServiceEndpoint {
    private static final Logger LOGGER = Logger.getLogger(LoggingServiceEndpoint.class.getName());
    
    private final String name;
    private final ServiceResponse prepareResponse;
    private boolean prepareWasCalled = false;
    private boolean commitWasCalled = false;
    private boolean rollbackWasCalled = false;
    
    /**
     * Creates a new logging service endpoint with a random name that will
     * return the specified response during prepare.
     *
     * @param prepareResponse The response to return during prepare
     */
    public LoggingServiceEndpoint(ServiceResponse prepareResponse) {
        this.name = "Service-" + UUID.randomUUID().toString().substring(0, 8);
        this.prepareResponse = prepareResponse;
    }
    
    /**
     * Creates a new logging service endpoint with the specified name that will
     * return the specified response during prepare.
     *
     * @param name The name of the service endpoint
     * @param prepareResponse The response to return during prepare
     */
    public LoggingServiceEndpoint(String name, ServiceResponse prepareResponse) {
        this.name = name;
        this.prepareResponse = prepareResponse;
    }
    
    @Override
    public ServiceResponse prepare() {
        LOGGER.log(Level.INFO, "{0}: Prepare called", name);
        prepareWasCalled = true;
        return prepareResponse;
    }
    
    @Override
    public void commit() {
        LOGGER.log(Level.INFO, "{0}: Commit called", name);
        commitWasCalled = true;
    }
    
    @Override
    public void rollback() {
        LOGGER.log(Level.INFO, "{0}: Rollback called", name);
        rollbackWasCalled = true;
    }
    
    public boolean wasPrepareInvoked() {
        return prepareWasCalled;
    }
    
    public boolean wasCommitInvoked() {
        return commitWasCalled;
    }
    
    public boolean wasRollbackInvoked() {
        return rollbackWasCalled;
    }
    
    public String getName() {
        return name;
    }
}