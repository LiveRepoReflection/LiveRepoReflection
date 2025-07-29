import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Route {
    private List<String> locations;
    private Map<String, Integer> arrivalTimes;
    private String vehicleId;

    public Route(String vehicleId) {
        this.vehicleId = vehicleId;
        locations = new ArrayList<>();
        arrivalTimes = new HashMap<>();
    }

    public void addStop(String locationId, int arrivalTime) {
        locations.add(locationId);
        arrivalTimes.put(locationId, arrivalTime);
    }

    public List<String> getLocations() {
        return locations;
    }

    public int getArrivalTimeAt(String locationId) {
        return arrivalTimes.getOrDefault(locationId, -1);
    }

    public boolean containsLocation(String locationId) {
        return locations.contains(locationId);
    }

    public String getVehicleId() {
        return vehicleId;
    }
}