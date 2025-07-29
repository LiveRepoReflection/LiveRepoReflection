public class Edge {
    private final int source;
    private final int destination;
    private final int baseTravelTime;
    private double congestionFactor;

    public Edge(int source, int destination, int baseTravelTime, double congestionFactor) {
        this.source = source;
        this.destination = destination;
        this.baseTravelTime = baseTravelTime;
        this.congestionFactor = congestionFactor;
    }

    public int getSource() {
        return source;
    }

    public int getDestination() {
        return destination;
    }

    public int getBaseTravelTime() {
        return baseTravelTime;
    }

    public double getCongestionFactor() {
        return congestionFactor;
    }

    public void setCongestionFactor(double congestionFactor) {
        this.congestionFactor = congestionFactor;
    }

    public double getTravelTime() {
        return baseTravelTime * congestionFactor;
    }
}