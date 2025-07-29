public class DeliveryLocation {
    private String id;
    private double x;
    private double y;
    private int demand;
    private int startTime;
    private int endTime;

    public DeliveryLocation(String id, double x, double y, int demand, int startTime, int endTime) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.demand = demand;
        this.startTime = startTime;
        this.endTime = endTime;
    }

    public String getId() {
        return id;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public int getDemand() {
        return demand;
    }

    public int getStartTime() {
        return startTime;
    }

    public int getEndTime() {
        return endTime;
    }
}