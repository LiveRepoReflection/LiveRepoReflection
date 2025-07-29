package network_sim;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

public class NetworkSimulation {

    private final Map<String, Server> servers;
    private final Map<String, List<Connection>> connections;
    private final Map<String, Task> tasks;
    private final List<String> securityBreaches;
    private double totalLatency;
    private int completedTaskCount;
    private int failedTaskCount;

    public NetworkSimulation() {
        this.servers = new HashMap<>();
        this.connections = new HashMap<>();
        this.tasks = new HashMap<>();
        this.securityBreaches = new ArrayList<>();
        this.totalLatency = 0;
        this.completedTaskCount = 0;
        this.failedTaskCount = 0;
    }

    public void addServer(String id, int processingCapacity, int processingSpeed, int securityLevel) {
        servers.put(id, new Server(id, processingCapacity, processingSpeed, securityLevel));
    }

    public void addConnection(String sourceServerId, String targetServerId, int latency) {
        Connection conn = new Connection(sourceServerId, targetServerId, latency);
        connections.computeIfAbsent(sourceServerId, k -> new ArrayList<>()).add(conn);
    }

    public void addTask(String id, int size, int securityRequirement, int priority, String sourceServerId, String destinationServerId) {
        Task task = new Task(id, size, securityRequirement, priority, sourceServerId, destinationServerId);
        tasks.put(id, task);
    }

    public void processTasks() {
        for (Task task : tasks.values()) {
            if (!task.status.equals("PENDING")) {
                continue;
            }
            Server source = servers.get(task.sourceServerId);
            Server destination = servers.get(task.destinationServerId);

            // Check if source and destination exist and are active.
            if (source == null || destination == null || !source.active || !destination.active) {
                task.status = "FAILED";
                failedTaskCount++;
                continue;
            }
            // Check if source meets security requirement.
            if (source.securityLevel < task.securityRequirement) {
                task.status = "FAILED";
                securityBreaches.add(task.id);
                failedTaskCount++;
                continue;
            }
            // Find the optimal route using Dijkstra's algorithm.
            DijkstraResult result = dijkstra(task);
            if (!result.found) {
                task.status = "FAILED";
                failedTaskCount++;
                continue;
            }
            // Simulate task processing at destination.
            int processingTime = (task.size + destination.processingSpeed - 1) / destination.processingSpeed;
            int totalTaskLatency = result.distance + processingTime;
            task.completionLatency = totalTaskLatency;
            totalLatency += totalTaskLatency;
            completedTaskCount++;
            task.status = "COMPLETED";
            destination.taskCount++;
            destination.taskIds.add(task.id);
        }
    }

    public String getTaskStatus(String taskId) {
        Task task = tasks.get(taskId);
        if (task == null) {
            return "UNKNOWN";
        }
        return task.status;
    }

    public List<String> getOverloadedServers() {
        List<String> overloaded = new ArrayList<>();
        for (Server server : servers.values()) {
            if (!server.active) {
                continue;
            }
            if (server.taskCount > server.processingCapacity) {
                overloaded.add(server.id);
            }
        }
        return overloaded;
    }

    public List<String> getSecurityBreaches() {
        return new ArrayList<>(securityBreaches);
    }

    public double getAverageLatency() {
        if (completedTaskCount == 0) {
            return 0;
        }
        return totalLatency / completedTaskCount;
    }

    public int getFailedTaskCount() {
        return failedTaskCount;
    }

    public void failServer(String serverId) {
        Server server = servers.get(serverId);
        if (server != null) {
            server.active = false;
        }
    }

    public void recoverServer(String serverId) {
        Server server = servers.get(serverId);
        if (server != null) {
            server.active = true;
        }
    }

    public void failConnection(String sourceServerId, String targetServerId) {
        List<Connection> connList = connections.get(sourceServerId);
        if (connList != null) {
            for (Connection conn : connList) {
                if (conn.target.equals(targetServerId)) {
                    conn.active = false;
                }
            }
        }
    }

    public void recoverConnection(String sourceServerId, String targetServerId, int latency) {
        List<Connection> connList = connections.get(sourceServerId);
        boolean found = false;
        if (connList != null) {
            for (Connection conn : connList) {
                if (conn.target.equals(targetServerId)) {
                    conn.active = true;
                    conn.latency = latency;
                    found = true;
                }
            }
        }
        if (!found) {
            addConnection(sourceServerId, targetServerId, latency);
        }
    }

    // Dijkstra's algorithm to find lowest latency path satisfying security requirements.
    private DijkstraResult dijkstra(Task task) {
        Map<String, Integer> dist = new HashMap<>();
        for (String id : servers.keySet()) {
            dist.put(id, Integer.MAX_VALUE);
        }
        dist.put(task.sourceServerId, 0);
        PriorityQueue<Pair> pq = new PriorityQueue<>((a, b) -> a.distance - b.distance);
        pq.add(new Pair(task.sourceServerId, 0));

        while (!pq.isEmpty()) {
            Pair current = pq.poll();
            if (current.distance > dist.get(current.serverId)) {
                continue;
            }
            if (current.serverId.equals(task.destinationServerId)) {
                return new DijkstraResult(true, current.distance);
            }
            List<Connection> connList = connections.getOrDefault(current.serverId, new ArrayList<>());
            for (Connection conn : connList) {
                if (!conn.active) {
                    continue;
                }
                Server neighbor = servers.get(conn.target);
                if (neighbor == null || !neighbor.active) {
                    continue;
                }
                if (neighbor.securityLevel < task.securityRequirement) {
                    continue;
                }
                int newDist = current.distance + conn.latency;
                if (newDist < dist.get(conn.target)) {
                    dist.put(conn.target, newDist);
                    pq.add(new Pair(conn.target, newDist));
                }
            }
        }
        return new DijkstraResult(false, -1);
    }

    private static class Pair {
        String serverId;
        int distance;

        Pair(String serverId, int distance) {
            this.serverId = serverId;
            this.distance = distance;
        }
    }

    private static class DijkstraResult {
        boolean found;
        int distance;

        DijkstraResult(boolean found, int distance) {
            this.found = found;
            this.distance = distance;
        }
    }

    private static class Server {
        String id;
        int processingCapacity;
        int processingSpeed;
        int securityLevel;
        boolean active;
        int taskCount;
        List<String> taskIds;

        Server(String id, int processingCapacity, int processingSpeed, int securityLevel) {
            this.id = id;
            this.processingCapacity = processingCapacity;
            this.processingSpeed = processingSpeed;
            this.securityLevel = securityLevel;
            this.active = true;
            this.taskCount = 0;
            this.taskIds = new ArrayList<>();
        }
    }

    private static class Task {
        String id;
        int size;
        int securityRequirement;
        int priority;
        String sourceServerId;
        String destinationServerId;
        String status;
        int completionLatency;

        Task(String id, int size, int securityRequirement, int priority, String sourceServerId, String destinationServerId) {
            this.id = id;
            this.size = size;
            this.securityRequirement = securityRequirement;
            this.priority = priority;
            this.sourceServerId = sourceServerId;
            this.destinationServerId = destinationServerId;
            this.status = "PENDING";
            this.completionLatency = 0;
        }
    }

    private static class Connection {
        String source;
        String target;
        int latency;
        boolean active;

        Connection(String source, String target, int latency) {
            this.source = source;
            this.target = target;
            this.latency = latency;
            this.active = true;
        }
    }
}