import java.util.LinkedList;
import java.util.Queue;

public class LoadBalancer {
    private int[] serverCapacities;
    private final Queue<Request> requestQueue;

    public LoadBalancer(int[] capacities) {
        this.serverCapacities = new int[capacities.length];
        System.arraycopy(capacities, 0, this.serverCapacities, 0, capacities.length);
        this.requestQueue = new LinkedList<>();
    }

    public int routeRequest(int requestPriority, int arrivalTime, int starvationThreshold) {
        int availableServer = getFirstAvailableServer();
        if (availableServer != -1) {
            decrementCapacity(availableServer);
            return availableServer;
        } else {
            requestQueue.add(new Request(requestPriority, arrivalTime, starvationThreshold));
            return -1;
        }
    }

    public void updateCapacity(int[] capacities) {
        if (capacities == null || capacities.length != serverCapacities.length) {
            throw new IllegalArgumentException("Invalid capacities array");
        }
        System.arraycopy(capacities, 0, this.serverCapacities, 0, capacities.length);
    }

    public int processQueue(int currentTime) {
        int availableServer = getFirstAvailableServer();
        if (availableServer == -1 || requestQueue.isEmpty()) {
            return -1;
        }
        Request selected = null;
        for (Request req : requestQueue) {
            int effectivePriority = req.getEffectivePriority(currentTime);
            if (selected == null) {
                selected = req;
            } else {
                int selectedEffective = selected.getEffectivePriority(currentTime);
                if (effectivePriority > selectedEffective) {
                    selected = req;
                } else if (effectivePriority == selectedEffective && req.arrivalTime < selected.arrivalTime) {
                    selected = req;
                }
            }
        }
        requestQueue.remove(selected);
        decrementCapacity(availableServer);
        return availableServer;
    }

    private int getFirstAvailableServer() {
        for (int i = 0; i < serverCapacities.length; i++) {
            if (serverCapacities[i] > 0) {
                return i;
            }
        }
        return -1;
    }

    private void decrementCapacity(int serverIndex) {
        if (serverCapacities[serverIndex] > 0) {
            serverCapacities[serverIndex]--;
        }
    }

    private static class Request {
        private final int requestPriority;
        private final int arrivalTime;
        private final int starvationThreshold;

        public Request(int requestPriority, int arrivalTime, int starvationThreshold) {
            this.requestPriority = requestPriority;
            this.arrivalTime = arrivalTime;
            this.starvationThreshold = starvationThreshold;
        }

        public int getEffectivePriority(int currentTime) {
            if (currentTime - arrivalTime >= starvationThreshold) {
                return 11;
            }
            return requestPriority;
        }
    }
}