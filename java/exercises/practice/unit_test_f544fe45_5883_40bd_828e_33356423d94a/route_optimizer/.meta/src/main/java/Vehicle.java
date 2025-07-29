public class Vehicle {
    private String id;
    private int capacity;
    private double operatingCostPerUnit;

    public Vehicle(String id, int capacity, double operatingCostPerUnit) {
        this.id = id;
        this.capacity = capacity;
        this.operatingCostPerUnit = operatingCostPerUnit;
    }

    public String getId() {
        return id;
    }

    public int getCapacity() {
        return capacity;
    }

    public double getOperatingCostPerUnit() {
        return operatingCostPerUnit;
    }
}