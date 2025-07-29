package traffic_master;

import java.util.Map;

public class PerformanceMetrics {
    private double averageTravelTime;
    private double totalJerk;
    private Map<String, Double> roadUtilization;
    
    public PerformanceMetrics(double averageTravelTime, double totalJerk, Map<String, Double> roadUtilization) {
        this.averageTravelTime = averageTravelTime;
        this.totalJerk = totalJerk;
        this.roadUtilization = roadUtilization;
    }
    
    public double getAverageTravelTime() {
        return averageTravelTime;
    }
    
    public double getTotalJerk() {
        return totalJerk;
    }
    
    public Map<String, Double> getRoadUtilization() {
        return roadUtilization;
    }
}