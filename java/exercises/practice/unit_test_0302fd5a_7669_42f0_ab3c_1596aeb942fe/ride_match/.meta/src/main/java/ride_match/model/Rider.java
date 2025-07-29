package ride_match.model;

public class Rider {
    private String id;
    private double originLatitude;
    private double originLongitude;
    private double destinationLatitude;
    private double destinationLongitude;
    private int pickupStart;
    private int pickupEnd;
    private int requiredCapacity;
    
    public Rider(String id, double originLatitude, double originLongitude,
                 double destinationLatitude, double destinationLongitude,
                 int pickupStart, int pickupEnd, int requiredCapacity) {
        this.id = id;
        this.originLatitude = originLatitude;
        this.originLongitude = originLongitude;
        this.destinationLatitude = destinationLatitude;
        this.destinationLongitude = destinationLongitude;
        this.pickupStart = pickupStart;
        this.pickupEnd = pickupEnd;
        this.requiredCapacity = requiredCapacity;
    }
    
    public String getId() {
        return id;
    }
    
    public double getOriginLatitude() {
        return originLatitude;
    }
    
    public double getOriginLongitude() {
        return originLongitude;
    }
    
    public double getDestinationLatitude() {
        return destinationLatitude;
    }
    
    public double getDestinationLongitude() {
        return destinationLongitude;
    }
    
    public int getPickupStart() {
        return pickupStart;
    }
    
    public int getPickupEnd() {
        return pickupEnd;
    }
    
    public int getRequiredCapacity() {
        return requiredCapacity;
    }
}