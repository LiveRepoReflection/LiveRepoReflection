import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Graph {
    private Map<String, DeliveryLocation> locations;
    private Map<String, List<RoadSegment>> adjList;

    public Graph() {
        locations = new HashMap<>();
        adjList = new HashMap<>();
    }

    public void addLocation(DeliveryLocation loc) {
        locations.put(loc.getId(), loc);
        if (!adjList.containsKey(loc.getId())) {
            adjList.put(loc.getId(), new ArrayList<>());
        }
    }

    public DeliveryLocation getLocation(String id) {
        return locations.get(id);
    }

    public void addRoadSegment(RoadSegment rs) {
        if (!adjList.containsKey(rs.getSource())) {
            adjList.put(rs.getSource(), new ArrayList<>());
        }
        adjList.get(rs.getSource()).add(rs);
    }

    public List<RoadSegment> getRoadSegmentsFrom(String source) {
        return adjList.getOrDefault(source, new ArrayList<>());
    }

    public Collection<DeliveryLocation> getAllLocations() {
        return locations.values();
    }
}