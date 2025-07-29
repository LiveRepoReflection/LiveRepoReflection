package traffic_optimize;

import java.util.*;

public class TrafficNetwork {
    private Map<Integer, List<Road>> graph;

    public TrafficNetwork() {
        graph = new HashMap<>();
    }

    public void addIntersection(int id) {
        if (!graph.containsKey(id)) {
            graph.put(id, new ArrayList<>());
        }
    }

    public void addRoad(int from, int to, double baseTravelTime, int capacity) {
        addIntersection(from);
        addIntersection(to);
        Road road = new Road(from, to, baseTravelTime, capacity);
        graph.get(from).add(road);
    }

    public void updateTrafficFlow(int from, int to, int flow) {
        List<Road> roads = graph.get(from);
        if (roads != null) {
            for (Road road : roads) {
                if (road.getTo() == to) {
                    road.setTrafficFlow(flow);
                    break;
                }
            }
        }
    }

    public List<Integer> shortestPath(int source, int destination) {
        Map<Integer, Double> dist = new HashMap<>();
        Map<Integer, Integer> prev = new HashMap<>();
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingDouble(n -> n.priority));
        for (Integer intersection : graph.keySet()) {
            dist.put(intersection, Double.POSITIVE_INFINITY);
        }
        dist.put(source, 0.0);
        pq.offer(new Node(source, 0.0));
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            if (current.id == destination) {
                break;
            }
            if (current.priority > dist.get(current.id)) {
                continue;
            }
            List<Road> neighbors = graph.get(current.id);
            if (neighbors == null) continue;
            for (Road road : neighbors) {
                double alt = dist.get(current.id) + road.getActualTravelTime();
                if (alt < dist.get(road.getTo())) {
                    dist.put(road.getTo(), alt);
                    prev.put(road.getTo(), current.id);
                    pq.offer(new Node(road.getTo(), alt));
                }
            }
        }
        if (!prev.containsKey(destination) && source != destination) {
            return null;
        }
        LinkedList<Integer> path = new LinkedList<>();
        int curr = destination;
        path.addFirst(curr);
        while (prev.containsKey(curr)) {
            curr = prev.get(curr);
            path.addFirst(curr);
        }
        return path;
    }

    public double getPathTravelTime(List<Integer> path) {
        if (path == null || path.size() <= 1) {
            return 0.0;
        }
        double total = 0.0;
        for (int i = 0; i < path.size() - 1; i++) {
            int from = path.get(i);
            int to = path.get(i + 1);
            Road road = getRoad(from, to);
            if (road != null) {
                total += road.getActualTravelTime();
            }
        }
        return total;
    }
    
    private Road getRoad(int from, int to) {
        List<Road> roads = graph.get(from);
        if (roads != null) {
            for (Road road : roads) {
                if (road.getTo() == to) {
                    return road;
                }
            }
        }
        return null;
    }

    public double getTotalNetworkTravelTime() {
        double total = 0.0;
        for (List<Road> roads : graph.values()) {
            for (Road road : roads) {
                total += road.getActualTravelTime() * road.getTrafficFlow();
            }
        }
        return total;
    }

    public TrafficReroutingResult rerouteTraffic(int origin, int destination, double percentageThreshold) {
        List<Integer> candidatePath = shortestPath(origin, destination);
        if (candidatePath == null || candidatePath.size() < 2) {
            return new TrafficReroutingResult(getTotalNetworkTravelTime(), 0.0, 0.0);
        }
        double originalFlow = 0.0;
        int edgeCount = candidatePath.size() - 1;
        for (int i = 0; i < edgeCount; i++) {
            Road road = getRoad(candidatePath.get(i), candidatePath.get(i + 1));
            if (road != null) {
                originalFlow += road.getTrafficFlow();
            }
        }
        double reroutedFlow = (percentageThreshold / 100.0) * originalFlow;
        double totalImprovement = 0.0;
        for (int i = 0; i < edgeCount; i++) {
            Road road = getRoad(candidatePath.get(i), candidatePath.get(i + 1));
            if (road != null) {
                double flowToReroute = reroutedFlow / edgeCount;
                double improvement = flowToReroute * (road.getActualTravelTime() - road.getBaseTravelTime());
                totalImprovement += improvement;
            }
        }
        double newTotalTime = getTotalNetworkTravelTime() - totalImprovement;
        return new TrafficReroutingResult(newTotalTime, reroutedFlow, originalFlow);
    }
    
    private static class Node {
        int id;
        double priority;

        public Node(int id, double priority) {
            this.id = id;
            this.priority = priority;
        }
    }
}