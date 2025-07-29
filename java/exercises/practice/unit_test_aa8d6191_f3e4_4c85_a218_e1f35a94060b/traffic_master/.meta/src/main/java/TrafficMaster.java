package traffic_master;

import java.util.*;

public class TrafficMaster {
    private Graph graph;
    private List<VehicleRequest> vehicleRequests;
    private SimulationParameters simulationParameters;
    
    public TrafficMaster(Graph graph, List<VehicleRequest> vehicleRequests, SimulationParameters simulationParameters) {
        this.graph = graph;
        this.vehicleRequests = vehicleRequests;
        this.simulationParameters = simulationParameters;
    }
    
    public SimulationResult runSimulation() {
        List<VehicleLog> logs = new ArrayList<>();
        double totalTravelTime = 0.0;
        int throughput = 0;
        int globalMaxQueue = 0;
        
        // Sort vehicle requests by arrival time.
        vehicleRequests.sort(Comparator.comparingDouble(VehicleRequest::getArrivalTime));
        
        for (VehicleRequest req : vehicleRequests) {
            List<Road> path = graph.findShortestPath(req.getStart(), req.getDestination());
            if (path.isEmpty()) {
                continue; // skip vehicle if no path found.
            }
            double currentTime = req.getArrivalTime();
            double departureTimeSource = currentTime;
            
            // Simulate travel along the computed path.
            for (Road road : path) {
                currentTime = road.simulateVehicle(currentTime);
                if (road.getMaxQueueLength() > globalMaxQueue) {
                    globalMaxQueue = road.getMaxQueueLength();
                }
            }
            
            double arrivalAtDestination = currentTime;
            VehicleLog log = new VehicleLog(req.getArrivalTime(), departureTimeSource, arrivalAtDestination);
            logs.add(log);
            totalTravelTime += (arrivalAtDestination - departureTimeSource);
            throughput++;
        }
        
        double avgTravelTime = throughput > 0 ? totalTravelTime / throughput : 0.0;
        
        // Assign a basic fixed traffic light policy for every intersection that has outgoing roads.
        Map<Integer, TrafficLightPolicy> finalPolicies = new HashMap<>();
        for (Intersection intersection : graph.getIntersections()) {
            List<Road> outgoing = intersection.getOutgoingRoads();
            if (!outgoing.isEmpty()) {
                double cycleLength = simulationParameters.getMinCycleLength();
                Map<Integer, Double> greenDurations = new HashMap<>();
                double equalDuration = cycleLength / outgoing.size();
                for (Road road : outgoing) {
                    greenDurations.put(road.getTo(), equalDuration);
                }
                finalPolicies.put(intersection.getId(), new TrafficLightPolicy(cycleLength, greenDurations));
            }
        }
        
        // Calculate road utilization: (number of vehicles * travelTime) / (simulationTime * capacity)
        Map<String, Double> roadUtilization = new HashMap<>();
        for (Road road : graph.getAllRoads()) {
            int count = road.getVehicleCount();
            double utilization = (count * road.getTravelTime()) / (simulationParameters.getTotalTime() * road.getCapacity());
            if (utilization > 1.0) {
                utilization = 1.0;
            }
            String key = road.getFrom() + "->" + road.getTo();
            roadUtilization.put(key, utilization);
        }
        
        // For this implementation, totalJerk is 0 as we did not change traffic policies during simulation.
        PerformanceMetrics metrics = new PerformanceMetrics(avgTravelTime, 0.0, roadUtilization);
        
        return new SimulationResult(throughput, avgTravelTime, logs, finalPolicies, globalMaxQueue, metrics);
    }
}