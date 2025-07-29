package traffic_master;

public class VehicleRequest {
    private int start;
    private int destination;
    private double arrivalTime;
    
    public VehicleRequest(int start, int destination, double arrivalTime) {
        this.start = start;
        this.destination = destination;
        this.arrivalTime = arrivalTime;
    }
    
    public int getStart() {
        return start;
    }
    
    public int getDestination() {
        return destination;
    }
    
    public double getArrivalTime() {
        return arrivalTime;
    }
}