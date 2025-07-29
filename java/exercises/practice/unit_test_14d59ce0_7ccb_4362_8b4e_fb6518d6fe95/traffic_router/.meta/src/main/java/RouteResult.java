import java.util.List;

public class RouteResult {
    private final List<Integer> route;
    private final double travelTime;

    public RouteResult(List<Integer> route, double travelTime) {
        this.route = route;
        this.travelTime = travelTime;
    }

    public List<Integer> getRoute() {
        return route;
    }

    public double getTravelTime() {
        return travelTime;
    }
}