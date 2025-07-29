package traffic_master;

import java.util.*;

public class Intersection {
    private int id;
    private List<Road> outgoingRoads;
    
    public Intersection(int id) {
        this.id = id;
        outgoingRoads = new ArrayList<>();
    }
    
    public int getId() {
        return id;
    }
    
    public void addOutgoingRoad(Road road) {
        outgoingRoads.add(road);
    }
    
    public List<Road> getOutgoingRoads() {
        return outgoingRoads;
    }
}