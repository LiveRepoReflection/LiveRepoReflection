package traffic_master;

import java.util.List;
import java.util.Map;

public class SimulationResult {
    private int throughput;
    private double averageTravelTime;
    private List<VehicleLog> vehicleLogs;
    private Map<Integer, TrafficLightPolicy> finalTrafficPolicies;
    private int maximumQueueLength;
    private PerformanceMetrics performanceMetrics;
    
    public SimulationResult(int throughput, double averageTravelTime, List<VehicleLog> vehicleLogs, 
                            Map<Integer, TrafficLightPolicy> finalTrafficPolicies, int maximumQueueLength,
                            PerformanceMetrics performanceMetrics) {
        this.throughput = throughput;
        this.averageTravelTime = averageTravelTime;
        this.vehicleLogs = vehicleLogs;
        this.finalTrafficPolicies = finalTrafficPolicies;
        this.maximumQueueLength = maximumQueueLength;
        this.performanceMetrics = performanceMetrics;
    }
    
    public int getThroughput() {
        return throughput;
    }
    
    public double getAverageTravelTime() {
        return averageTravelTime;
    }
    
    public List<VehicleLog> getVehicleLogs() {
        return vehicleLogs;
    }
    
    public Map<Integer, TrafficLightPolicy> getFinalTrafficPolicies() {
        return finalTrafficPolicies;
    }
    
    public int getMaximumQueueLength() {
        return maximumQueueLength;
    }
    
    public PerformanceMetrics getPerformanceMetrics() {
        return performanceMetrics;
    }
}