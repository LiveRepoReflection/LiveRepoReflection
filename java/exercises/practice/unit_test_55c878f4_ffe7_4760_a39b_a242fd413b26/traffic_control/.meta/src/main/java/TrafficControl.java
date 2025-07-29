package traffic_control;

import java.util.*;

public class TrafficControl {
    // Map to hold intersections
    private Map<Integer, Intersection> intersections;
    // List to hold traffic demands
    private List<TrafficDemand> demands;

    public TrafficControl() {
        intersections = new HashMap<>();
        demands = new ArrayList<>();
    }

    // Represents an intersection node in the graph
    private static class Intersection {
        int id;
        List<Road> roads;

        public Intersection(int id) {
            this.id = id;
            this.roads = new ArrayList<>();
        }
    }

    // Represents a directed road (edge) in the graph
    private static class Road {
        int from;
        int to;
        int capacity;
        int flow;

        public Road(int from, int to, int capacity) {
            this.from = from;
            this.to = to;
            this.capacity = capacity;
            this.flow = 0;
        }

        public int availableCapacity() {
            return capacity - flow;
        }
    }

    // Represents a traffic demand between two intersections
    private static class TrafficDemand {
        int source;
        int destination;
        int demand;

        public TrafficDemand(int source, int destination, int demand) {
            this.source = source;
            this.destination = destination;
            this.demand = demand;
        }
    }

    // Public API methods

    // Adds an intersection to the network
    public void addIntersection(int id) {
        if (!intersections.containsKey(id)) {
            intersections.put(id, new Intersection(id));
        }
    }

    // Adds a directed road from 'from' to 'to' with the given capacity
    public void addRoad(int from, int to, int capacity) {
        // Ensure both intersections exist
        addIntersection(from);
        addIntersection(to);
        Intersection fromIntersection = intersections.get(from);
        fromIntersection.roads.add(new Road(from, to, capacity));
    }

    // Update the capacity of a road (if there are multiple roads between nodes, update the first found)
    public void updateRoadCapacity(int from, int to, int newCapacity) {
        if (intersections.containsKey(from)) {
            for (Road road : intersections.get(from).roads) {
                if (road.to == to) {
                    road.capacity = newCapacity;
                    // Ensure current flow does not exceed new capacity
                    if (road.flow > newCapacity) {
                        road.flow = newCapacity;
                    }
                    break;
                }
            }
        }
    }

    // Remove a road from the network
    public void removeRoad(int from, int to) {
        if (intersections.containsKey(from)) {
            Iterator<Road> it = intersections.get(from).roads.iterator();
            while (it.hasNext()) {
                Road road = it.next();
                if (road.to == to) {
                    it.remove();
                    break;
                }
            }
        }
    }

    // Adds a traffic demand between source and destination
    public void addTrafficDemand(int source, int destination, int demand) {
        addIntersection(source);
        addIntersection(destination);
        demands.add(new TrafficDemand(source, destination, demand));
    }

    // Update an existing traffic demand (updates the first matching demand for the given source-destination pair)
    public void updateTrafficDemand(int source, int destination, int newDemand) {
        for (TrafficDemand td : demands) {
            if (td.source == source && td.destination == destination) {
                td.demand = newDemand;
                break;
            }
        }
    }

    // Routes all traffic demands through the network.
    // Returns true if all demands can be satisfied, false otherwise.
    public boolean routeTraffic() {
        // Reset flows on all roads
        for (Intersection inter : intersections.values()) {
            for (Road road : inter.roads) {
                road.flow = 0;
            }
        }

        // For each traffic demand, attempt to find a valid path and update flows accordingly.
        // We use a BFS approach for each demand.
        for (TrafficDemand demand : demands) {
            if (!augmentFlow(demand.source, demand.destination, demand.demand)) {
                return false;
            }
        }
        return true;
    }

    // Calculate congestion metric as the sum of squares of utilization ratios multiplied by capacity.
    // In our simplified metric, we use sum(flow^2) over all roads.
    public int getCongestionMetric() {
        int metric = 0;
        for (Intersection inter : intersections.values()) {
            for (Road road : inter.roads) {
                metric += road.flow * road.flow;
            }
        }
        return metric;
    }

    // Helper method: finds a path from source to destination that can support the required flow
    // and updates flow along the found path.
    private boolean augmentFlow(int source, int destination, int requiredFlow) {
        // Map to keep track of the road used to reach a node
        Map<Integer, Road> parentRoad = new HashMap<>();
        // Set to keep track of visited intersections
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();

        queue.add(source);
        visited.add(source);

        while (!queue.isEmpty()) {
            int current = queue.poll();
            if (current == destination) {
                break;
            }
            Intersection inter = intersections.get(current);
            for (Road road : inter.roads) {
                int next = road.to;
                if (!visited.contains(next) && road.availableCapacity() >= requiredFlow) {
                    visited.add(next);
                    parentRoad.put(next, road);
                    queue.add(next);
                }
            }
        }

        // If destination was not reached, return false (demand cannot be met)
        if (!visited.contains(destination)) {
            return false;
        }

        // Update the flows along the path backwards from destination to source
        int node = destination;
        while (node != source) {
            Road road = parentRoad.get(node);
            road.flow += requiredFlow;
            node = road.from;
        }
        return true;
    }
}