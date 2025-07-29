package traffic_master;

import java.util.PriorityQueue;

public class Road {
    private int from;
    private int to;
    private int capacity;
    private double travelTime;
    private PriorityQueue<Double> ongoingVehicles;
    private int vehicleCount;
    private int maxQueueLength;
    
    public Road(int from, int to, int capacity, double travelTime) {
        this.from = from;
        this.to = to;
        this.capacity = capacity;
        this.travelTime = travelTime;
        this.ongoingVehicles = new PriorityQueue<>();
        this.vehicleCount = 0;
        this.maxQueueLength = 0;
    }
    
    public int getFrom() {
        return from;
    }
    
    public int getTo() {
        return to;
    }
    
    public int getCapacity() {
        return capacity;
    }
    
    public double getTravelTime() {
        return travelTime;
    }
    
    public int getVehicleCount() {
        return vehicleCount;
    }
    
    public int getMaxQueueLength() {
        return maxQueueLength;
    }
    
    // Simulate a vehicle entering this road at the given arrivalTime.
    // Returns the finish time when the vehicle leaves the road.
    public double simulateVehicle(double arrivalTime) {
        while (!ongoingVehicles.isEmpty() && ongoingVehicles.peek() <= arrivalTime) {
            ongoingVehicles.poll();
        }
        double startTime = arrivalTime;
        if (ongoingVehicles.size() >= capacity) {
            startTime = ongoingVehicles.peek();
        }
        double waitingTime = startTime - arrivalTime;
        if (waitingTime > 0) {
            int currentQueue = ongoingVehicles.size() - capacity + 1;
            if (currentQueue > maxQueueLength) {
                maxQueueLength = currentQueue;
            }
        }
        double finishTime = startTime + travelTime;
        ongoingVehicles.add(finishTime);
        vehicleCount++;
        return finishTime;
    }
}