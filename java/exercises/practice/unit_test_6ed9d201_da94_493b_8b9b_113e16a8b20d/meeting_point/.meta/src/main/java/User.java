public class User {
    private final double latitude;
    private final double longitude;
    private final int id;

    public User(double latitude, double longitude, int id) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.id = id;
    }

    public double getLatitude() {
        return latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public int getId() {
        return id;
    }
}