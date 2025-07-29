public class Server {
    private String id;
    private int capacity;
    private int latency;
    private int currentLoad;
    private boolean healthy;

    public Server(String id, int capacity, int latency) {
        this.id = id;
        this.capacity = capacity;
        this.latency = latency;
        this.currentLoad = 0;
        this.healthy = true;
    }

    public String getId() {
        return id;
    }

    public int getCapacity() {
        return capacity;
    }

    public int getLatency() {
        return latency;
    }

    public int getCurrentLoad() {
        return currentLoad;
    }

    public void setCurrentLoad(int load) {
        this.currentLoad = load;
    }

    public boolean isHealthy() {
        return healthy;
    }

    public void setHealthy(boolean healthy) {
        this.healthy = healthy;
    }

    public void incrementLoad() {
        this.currentLoad++;
    }
}