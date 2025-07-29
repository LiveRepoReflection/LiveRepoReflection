package traffic_master;

public class SimulationParameters {
    private double totalTime;
    private double adaptationFrequency;
    private double minCycleLength;
    private double maxCycleLength;
    
    public SimulationParameters(double totalTime, double adaptationFrequency, double minCycleLength, double maxCycleLength) {
        this.totalTime = totalTime;
        this.adaptationFrequency = adaptationFrequency;
        this.minCycleLength = minCycleLength;
        this.maxCycleLength = maxCycleLength;
    }
    
    public double getTotalTime() {
        return totalTime;
    }
    
    public double getAdaptationFrequency() {
        return adaptationFrequency;
    }
    
    public double getMinCycleLength() {
        return minCycleLength;
    }
    
    public double getMaxCycleLength() {
        return maxCycleLength;
    }
}