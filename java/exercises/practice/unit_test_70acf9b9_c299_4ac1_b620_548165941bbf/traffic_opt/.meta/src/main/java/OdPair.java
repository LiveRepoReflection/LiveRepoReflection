public class OdPair {
    private final int origin;
    private final int destination;
    private final int demand;

    public OdPair(int origin, int destination, int demand) {
        this.origin = origin;
        this.destination = destination;
        this.demand = demand;
    }

    public int getOrigin() {
        return origin;
    }

    public int getDestination() {
        return destination;
    }

    public int getDemand() {
        return demand;
    }
}