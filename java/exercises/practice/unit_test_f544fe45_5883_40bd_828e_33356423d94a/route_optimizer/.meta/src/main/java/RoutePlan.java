import java.util.ArrayList;
import java.util.List;

public class RoutePlan {
    private List<Route> routes;
    private List<String> unservedLocations;
    private double totalCost;

    public RoutePlan() {
        routes = new ArrayList<>();
        unservedLocations = new ArrayList<>();
        totalCost = 0.0;
    }

    public void addRoute(Route route) {
        routes.add(route);
    }

    public List<Route> getRoutes() {
        return routes;
    }

    public void addUnservedLocation(String locId) {
        unservedLocations.add(locId);
    }

    public List<String> getUnservedLocations() {
        return unservedLocations;
    }

    public double getTotalCost() {
        return totalCost;
    }

    public void addCost(double cost) {
        totalCost += cost;
    }
}