public class OptimalMeetingPoint {
    private final double latitude;
    private final double longitude;
    private final double totalCommunicationCost;

    public OptimalMeetingPoint(double latitude, double longitude, double totalCommunicationCost) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.totalCommunicationCost = totalCommunicationCost;
    }

    public double getLatitude() {
        return latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public double getTotalCommunicationCost() {
        return totalCommunicationCost;
    }
}