package route_optimizer;

public class Edge {
    private String destination;
    private double cost;
    private int time;

    public Edge(String destination, double cost, int time) {
        this.destination = destination;
        this.cost = cost;
        this.time = time;
    }

    public String getDestination() {
        return destination;
    }

    public double getCost() {
        return cost;
    }

    public int getTime() {
        return time;
    }
}