import java.util.HashMap;
import java.util.Map;

public class AdaptiveBalancer {
    private Map<String, Server> servers;

    public AdaptiveBalancer() {
        servers = new HashMap<>();
    }

    public void registerServer(Server server) {
        servers.put(server.getId(), server);
    }

    public void deregisterServer(String id) {
        servers.remove(id);
    }

    public void updateServerHealth(String id, boolean healthy) {
        Server server = servers.get(id);
        if (server != null) {
            server.setHealthy(healthy);
        }
    }

    public void updateServerLoad(String id, int load) {
        Server server = servers.get(id);
        if (server != null) {
            server.setCurrentLoad(load);
        }
    }

    public String routeRequest(Request request) {
        Server bestServer = null;
        double bestScore = -1;
        for (Server s : servers.values()) {
            if (!s.isHealthy()) {
                continue;
            }
            int available = s.getCapacity() - s.getCurrentLoad();
            if (available <= 0) {
                continue;
            }
            double score = (double) available / s.getLatency();
            if (request.getPriority() == Priority.HIGH) {
                score *= 1.2;
            } else if (request.getPriority() == Priority.LOW) {
                score *= 0.8;
            }
            if (score > bestScore) {
                bestScore = score;
                bestServer = s;
            }
        }
        if (bestServer == null) {
            return "REJECTED";
        }
        bestServer.incrementLoad();
        return bestServer.getId();
    }
}