import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RouteOptimizer {
    private final int turnAroundTime = 1; // fixed turnaround time per location
    private final int waitingCostPerUnit = 1; // cost per unit waiting time
    private final int penaltyForMissedDelivery = 1000; // penalty for each unserved delivery

    public RoutePlan planRoutes(DeliveryLocation depot, List<Vehicle> vehicles, Graph graph) {
        RoutePlan plan = new RoutePlan();
        // Collect all delivery locations except the depot
        Map<String, DeliveryLocation> deliveries = new HashMap<>();
        for (DeliveryLocation loc : graph.getAllLocations()) {
            if (!loc.getId().equals(depot.getId())) {
                deliveries.put(loc.getId(), loc);
            }
        }

        // Process each vehicle individually
        for (Vehicle vehicle : vehicles) {
            int remainingCapacity = vehicle.getCapacity();
            int currentTime = 0;
            String currentLocation = depot.getId();
            Route route = new Route(vehicle.getId());
            // Start route at depot with time 0
            route.addStop(depot.getId(), currentTime);
            boolean assigned = false;

            while (true) {
                DeliveryCandidate bestCandidate = null;
                // Search through available deliveries for candidate fits
                for (DeliveryLocation candidate : deliveries.values()) {
                    if (candidate.getDemand() > remainingCapacity) {
                        continue;
                    }
                    RoadSegment road = getCheapestRoadSegment(graph.getRoadSegmentsFrom(currentLocation), candidate.getId());
                    if (road == null) {
                        continue;
                    }
                    int travelTime = road.getCost();
                    int arrivalTime = currentTime + travelTime;
                    int waitingTime = 0;
                    if (arrivalTime < candidate.getStartTime()) {
                        waitingTime = candidate.getStartTime() - arrivalTime;
                        arrivalTime = candidate.getStartTime();
                    }
                    if (arrivalTime > candidate.getEndTime()) {
                        continue;
                    }
                    int totalTimeCost = travelTime + waitingTime;
                    DeliveryCandidate dc = new DeliveryCandidate(candidate, road, totalTimeCost, arrivalTime);
                    if (bestCandidate == null || dc.totalTimeCost < bestCandidate.totalTimeCost) {
                        bestCandidate = dc;
                    }
                }

                if (bestCandidate == null) {
                    break; // no candidate can be assigned
                }

                // Accept the candidate and update cost and route details
                DeliveryLocation selected = bestCandidate.location;
                double travelCost = bestCandidate.road.getCost() * vehicle.getOperatingCostPerUnit();
                plan.addCost(travelCost);
                int waitingTime = Math.max(0, selected.getStartTime() - (currentTime + bestCandidate.road.getCost()));
                plan.addCost(waitingTime * waitingCostPerUnit);

                currentTime = bestCandidate.arrivalTime + turnAroundTime;
                remainingCapacity -= selected.getDemand();
                currentLocation = selected.getId();
                route.addStop(selected.getId(), bestCandidate.arrivalTime);
                deliveries.remove(selected.getId());
                assigned = true;
            }

            // Include the return trip to the depot if a road exists
            RoadSegment returnRoad = getCheapestRoadSegment(graph.getRoadSegmentsFrom(currentLocation), depot.getId());
            if (returnRoad != null) {
                double returnCost = returnRoad.getCost() * vehicle.getOperatingCostPerUnit();
                plan.addCost(returnCost);
                currentTime += returnRoad.getCost();
                route.addStop(depot.getId(), currentTime);
            }
            if (assigned) {
                plan.addRoute(route);
            }
        }

        // For all unserved deliveries, add penalty and mark as unserved.
        for (DeliveryLocation loc : deliveries.values()) {
            plan.addUnservedLocation(loc.getId());
            plan.addCost(penaltyForMissedDelivery);
        }
        return plan;
    }

    // Helper method returns the cheapest road segment from a list that goes to the target destination
    private RoadSegment getCheapestRoadSegment(List<RoadSegment> segments, String target) {
        RoadSegment best = null;
        for (RoadSegment rs : segments) {
            if (rs.getDestination().equals(target)) {
                if (best == null || rs.getCost() < best.getCost()) {
                    best = rs;
                }
            }
        }
        return best;
    }

    // Inner helper class to represent a candidate delivery option during planning
    private class DeliveryCandidate {
        DeliveryLocation location;
        RoadSegment road;
        int totalTimeCost;
        int arrivalTime;

        public DeliveryCandidate(DeliveryLocation location, RoadSegment road, int totalTimeCost, int arrivalTime) {
            this.location = location;
            this.road = road;
            this.totalTimeCost = totalTimeCost;
            this.arrivalTime = arrivalTime;
        }
    }
}