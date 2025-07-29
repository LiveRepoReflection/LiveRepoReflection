import java.util.Map;

public class Machine {
    private String machineId;
    private Map<String, Integer> availableResources;
    private String location;
    
    public Machine(String machineId, Map<String, Integer> availableResources, String location) {
        this.machineId = machineId;
        this.availableResources = availableResources;
        this.location = location;
    }
    
    public String getMachineId() { return machineId; }
    public Map<String, Integer> getAvailableResources() { return availableResources; }
    public String getLocation() { return location; }
}