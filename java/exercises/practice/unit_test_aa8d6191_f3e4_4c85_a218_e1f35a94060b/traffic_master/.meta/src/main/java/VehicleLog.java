package traffic_master;

public class VehicleLog {
    private double arrivalTimeSource;
    private double departureTimeSource;
    private double arrivalTimeDestination;
    
    public VehicleLog(double arrivalTimeSource, double departureTimeSource, double arrivalTimeDestination) {
        this.arrivalTimeSource = arrivalTimeSource;
        this.departureTimeSource = departureTimeSource;
        this.arrivalTimeDestination = arrivalTimeDestination;
    }
    
    public double getArrivalTimeSource() {
        return arrivalTimeSource;
    }
    
    public double getDepartureTimeSource() {
        return departureTimeSource;
    }
    
    public double getArrivalTimeDestination() {
        return arrivalTimeDestination;
    }
}