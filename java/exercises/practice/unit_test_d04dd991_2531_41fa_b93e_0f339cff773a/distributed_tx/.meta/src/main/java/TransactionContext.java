import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionContext {
    private final Map<ResourceManager, String> resourceManagers;
    private final Set<ResourceManager> readOnlyResources;

    public TransactionContext() {
        this.resourceManagers = new ConcurrentHashMap<>();
        this.readOnlyResources = Collections.newSetFromMap(new ConcurrentHashMap<>());
    }

    public void addResourceManager(ResourceManager rm, String operationDetails) {
        resourceManagers.put(rm, operationDetails);
    }

    public Map<ResourceManager, String> getResourceManagers() {
        return resourceManagers;
    }

    public void markReadOnly(ResourceManager rm) {
        readOnlyResources.add(rm);
    }

    public boolean isReadOnly(ResourceManager rm) {
        return readOnlyResources.contains(rm);
    }
}