import java.util.Map;
import java.util.HashMap;
import java.util.Objects;

public class WorkerNode {
    private final String nodeId;
    private final Map<String, Integer> resourceCapacity;
    private final Map<String, Integer> currentResourceAllocation;

    public WorkerNode(String nodeId, Map<String, Integer> resourceCapacity) {
        this.nodeId = nodeId;
        this.resourceCapacity = new HashMap<>(resourceCapacity);
        this.currentResourceAllocation = new HashMap<>();
        resourceCapacity.keySet().forEach(k -> currentResourceAllocation.put(k, 0));
    }

    public String getNodeId() { return nodeId; }
    public Map<String, Integer> getResourceCapacity() { return new HashMap<>(resourceCapacity); }
    public Map<String, Integer> getCurrentResourceAllocation() { return new HashMap<>(currentResourceAllocation); }

    public void setCurrentResourceAllocation(Map<String, Integer> allocation) {
        currentResourceAllocation.clear();
        currentResourceAllocation.putAll(allocation);
    }

    public boolean canAllocateResources(Map<String, Integer> requirements) {
        return requirements.entrySet().stream()
            .allMatch(entry -> {
                int available = resourceCapacity.getOrDefault(entry.getKey(), 0) - 
                              currentResourceAllocation.getOrDefault(entry.getKey(), 0);
                return available >= entry.getValue();
            });
    }

    public void allocateResources(Map<String, Integer> requirements) {
        requirements.forEach((key, value) -> 
            currentResourceAllocation.merge(key, value, Integer::sum)
        );
    }

    public void releaseResources(Map<String, Integer> requirements) {
        requirements.forEach((key, value) -> 
            currentResourceAllocation.merge(key, value, (oldVal, newVal) -> oldVal - newVal)
        );
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        WorkerNode that = (WorkerNode) o;
        return nodeId.equals(that.nodeId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(nodeId);
    }
}