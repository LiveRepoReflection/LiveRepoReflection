public class Road {
    private final int source;
    private final int destination;
    private final int capacity;
    private final int travelTime;

    public Road(int source, int destination, int capacity, int travelTime) {
        this.source = source;
        this.destination = destination;
        this.capacity = capacity;
        this.travelTime = travelTime;
    }

    public int getSource() {
        return source;
    }

    public int getDestination() {
        return destination;
    }

    public int getCapacity() {
        return capacity;
    }

    public int getTravelTime() {
        return travelTime;
    }
}