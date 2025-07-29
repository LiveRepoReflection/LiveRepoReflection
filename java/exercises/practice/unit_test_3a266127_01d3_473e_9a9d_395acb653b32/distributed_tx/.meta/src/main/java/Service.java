import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Implementation of a service that can participate in distributed transactions.
 * This class is provided as an example implementation of the ServiceInterface.
 */
public class Service implements ServiceInterface {
    private static final Logger LOGGER = Logger.getLogger(Service.class.getName());
    
    private final int serviceId;
    private final Map<String, Object> data = new ConcurrentHashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    /**
     * Constructs a new Service with the given ID.
     * 
     * @param serviceId the unique identifier for this service
     */
    public Service(int serviceId) {
        this.serviceId = serviceId;
    }
    
    @Override
    public boolean execute(Callable<Boolean> operation) {
        try {
            lock.writeLock().lock();
            return operation.call();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Exception executing operation on service " + serviceId, e);
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    @Override
    public boolean rollback(Callable<Boolean> rollbackOperation) {
        try {
            lock.writeLock().lock();
            return rollbackOperation.call();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Exception rolling back operation on service " + serviceId, e);
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Gets a value from the service's data store.
     * 
     * @param key the key to look up
     * @return the value associated with the key, or null if not found
     */
    public Object getValue(String key) {
        try {
            lock.readLock().lock();
            return data.get(key);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Sets a value in the service's data store.
     * 
     * @param key the key to set
     * @param value the value to associate with the key
     */
    public void setValue(String key, Object value) {
        try {
            lock.writeLock().lock();
            data.put(key, value);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Removes a value from the service's data store.
     * 
     * @param key the key to remove
     * @return the previous value associated with the key, or null if not found
     */
    public Object removeValue(String key) {
        try {
            lock.writeLock().lock();
            return data.remove(key);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Returns the service ID.
     * 
     * @return the service ID
     */
    public int getServiceId() {
        return serviceId;
    }
}