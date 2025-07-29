package traffic_master;

import java.util.HashMap;
import java.util.Map;

public class TrafficLightPolicy {
    private double cycleLength;
    private Map<Integer, Double> greenDurations;
    
    public TrafficLightPolicy(double cycleLength, Map<Integer, Double> greenDurations) {
        this.cycleLength = cycleLength;
        this.greenDurations = new HashMap<>(greenDurations);
    }
    
    public double getCycleLength() {
        return cycleLength;
    }
    
    public Map<Integer, Double> getGreenDurations() {
        return greenDurations;
    }
}