package traffic_master;

import java.util.*;

public class Graph {
    private Map<Integer, Intersection> intersections;
    
    public Graph() {
        intersections = new HashMap<>();
    }
    
    public void addIntersection(int id) {
        if (!intersections.containsKey(id)) {
            intersections.put(id, new Intersection(id));
        }
    }
    
    public void addRoad(int from, int to, int capacity, double travelTime) {
        if (!intersections.containsKey(from)) {
            addIntersection(from);
        }
        if (!intersections.containsKey(to)) {
            addIntersection(to);
        }
        Intersection fromIntersection = intersections.get(from);
        Road road = new Road(from, to, capacity, travelTime);
        fromIntersection.addOutgoingRoad(road);
    }
    
    public Collection<Intersection> getIntersections() {
        return intersections.values();
    }
    
    public List<Road> getAllRoads() {
        List<Road> roads = new ArrayList<>();
        for (Intersection inter : intersections.values()) {
            roads.addAll(inter.getOutgoingRoads());
        }
        return roads;
    }
    
    public Intersection getIntersection(int id) {
        return intersections.get(id);
    }
    
    // Finds the shortest path (minimizing travel time) between source and destination using Dijkstra's algorithm.
    public List<Road> findShortestPath(int source, int destination) {
        Map<Integer, Double> distances = new HashMap<>();
        Map<Integer, Road> previousRoad = new HashMap<>();
        Set<Integer> visited = new HashSet<>();
        
        class Node {
            int id;
            double dist;
            Node(int id, double dist) {
                this.id = id;
                this.dist = dist;
            }
        }
        
        PriorityQueue<Node> queue = new PriorityQueue<>(Comparator.comparingDouble(n -> n.dist));
        
        for (Integer id : intersections.keySet()) {
            distances.put(id, Double.MAX_VALUE);
        }
        distances.put(source, 0.0);
        queue.add(new Node(source, 0.0));
        
        while (!queue.isEmpty()) {
            Node current = queue.poll();
            if (visited.contains(current.id))
                continue;
            visited.add(current.id);
            if (current.id == destination)
                break;
            Intersection inter = intersections.get(current.id);
            for (Road road : inter.getOutgoingRoads()) {
                int neighbor = road.getTo();
                double newDist = distances.get(current.id) + road.getTravelTime();
                if (newDist < distances.getOrDefault(neighbor, Double.MAX_VALUE)) {
                    distances.put(neighbor, newDist);
                    previousRoad.put(neighbor, road);
                    queue.add(new Node(neighbor, newDist));
                }
            }
        }
        
        List<Road> path = new ArrayList<>();
        if (!previousRoad.containsKey(destination)) {
            return path; // return empty path if no route found
        }
        int currentId = destination;
        while (currentId != source) {
            Road road = previousRoad.get(currentId);
            path.add(0, road);
            currentId = road.getFrom();
        }
        return path;
    }
}