package traffic_optimize;

public class Road {
    private int from;
    private int to;
    private double baseTravelTime;
    private int capacity;
    private int trafficFlow;

    public Road(int from, int to, double baseTravelTime, int capacity) {
        this.from = from;
        this.to = to;
        this.baseTravelTime = baseTravelTime;
        this.capacity = capacity;
        this.trafficFlow = 0;
    }

    public int getFrom() {
        return from;
    }

    public int getTo() {
        return to;
    }

    public double getBaseTravelTime() {
        return baseTravelTime;
    }

    public int getCapacity() {
        return capacity;
    }

    public int getTrafficFlow() {
        return trafficFlow;
    }

    public void setTrafficFlow(int trafficFlow) {
        this.trafficFlow = trafficFlow;
    }

    public double getActualTravelTime() {
        double ratio = ((double) trafficFlow) / capacity;
        return baseTravelTime * (1 + ratio * ratio);
    }
}