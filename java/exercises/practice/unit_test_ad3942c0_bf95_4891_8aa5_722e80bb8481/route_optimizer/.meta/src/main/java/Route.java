package route_optimizer;

import java.util.*;

public class Route {
    private List<String> citySequence;
    private int totalDelivered;
    private int totalTime;
    private double totalCost;
    private Map<String, Integer> deliveries;

    public Route(List<String> citySequence, int totalDelivered, int totalTime, double totalCost, Map<String, Integer> deliveries) {
        this.citySequence = new ArrayList<>(citySequence);
        this.totalDelivered = totalDelivered;
        this.totalTime = totalTime;
        this.totalCost = totalCost;
        this.deliveries = new HashMap<>(deliveries);
    }

    public List<String> getCitySequence() {
        return citySequence;
    }

    public int getTotalDelivered() {
        return totalDelivered;
    }

    public int getTotalTime() {
        return totalTime;
    }

    public double getTotalCost() {
        return totalCost;
    }

    public int getDeliveredForCity(String city) {
        return deliveries.getOrDefault(city, 0);
    }
}