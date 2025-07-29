package com.adaptivebalancer;

import java.util.HashMap;
import java.util.Map;

public class AdaptiveBalancer {
    private Map<String, BackendServer> backends;
    private long totalLatency;
    private long totalRequests;

    public AdaptiveBalancer() {
        backends = new HashMap<>();
        totalLatency = 0;
        totalRequests = 0;
    }

    public void addBackend(BackendServer server) {
        backends.put(server.getId(), server);
    }

    public void removeBackend(String serverId) {
        backends.remove(serverId);
    }

    public void updateServerMetrics(String serverId, int load, int capacity, int latency) {
        BackendServer server = backends.get(serverId);
        if (server != null) {
            server.setLoad(load);
            server.setCapacity(capacity);
            server.setLatency(latency);
        }
    }

    public void updateServerHealth(String serverId, boolean healthy) {
        BackendServer server = backends.get(serverId);
        if (server != null) {
            server.setHealthy(healthy);
        }
    }

    public String routeRequest(String requestId) {
        double bestScore = Double.NEGATIVE_INFINITY;
        BackendServer bestServer = null;

        // First, consider servers that are healthy and not overloaded.
        for (BackendServer server : backends.values()) {
            if (!server.isHealthy() || server.getLoad() >= server.getCapacity()) {
                continue;
            }
            double availableCapacity = server.getCapacity() - server.getLoad();
            double score = (availableCapacity * 1000.0) / (server.getLatency() + 1);
            if (score > bestScore) {
                bestScore = score;
                bestServer = server;
            }
        }

        // If no servers with available capacity, consider healthy servers even if overloaded.
        if (bestServer == null) {
            for (BackendServer server : backends.values()) {
                if (!server.isHealthy()) {
                    continue;
                }
                double score = (server.getCapacity() * 1000.0) / (server.getLatency() + 1);
                if (score > bestScore) {
                    bestScore = score;
                    bestServer = server;
                }
            }
        }

        if (bestServer != null) {
            totalRequests++;
            totalLatency += bestServer.getLatency();
            return bestServer.getId();
        }
        return null;
    }

    public long getAverageLatency() {
        if (totalRequests == 0) {
            return 0;
        }
        return totalLatency / totalRequests;
    }

    public long getThroughput() {
        return totalRequests;
    }
}