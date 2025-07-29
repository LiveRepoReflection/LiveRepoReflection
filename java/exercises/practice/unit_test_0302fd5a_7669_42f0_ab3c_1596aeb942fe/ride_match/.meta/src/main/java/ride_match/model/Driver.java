package ride_match.model;

public class Driver {
    private String id;
    private double latitude;
    private double longitude;
    private int capacity;
    private int driverScore;
    private int availableStart;
    private int availableEnd;
    
    public Driver(String id, double latitude, double longitude, int capacity,
                  int driverScore, int availableStart, int availableEnd) {
        this.id = id;
        this.latitude = latitude;
        this.longitude = longitude;
        this.capacity = capacity;
        this.driverScore = driverScore;
        this.availableStart = availableStart;
        this.availableEnd = availableEnd;
    }
    
    public String getId() {
        return id;
    }
    
    public double getLatitude() {
        return latitude;
    }
    
    public double getLongitude() {
        return longitude;
    }
    
    public int getCapacity() {
        return capacity;
    }
    
    public int getDriverScore() {
        return driverScore;
    }
    
    public int getAvailableStart() {
        return availableStart;
    }
    
    public int getAvailableEnd() {
        return availableEnd;
    }
}