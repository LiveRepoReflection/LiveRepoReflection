package com.adaptivebalancer;

public class BackendServer {
    private String id;
    private int load;
    private int capacity;
    private int latency;
    private boolean healthy;

    public BackendServer(String id, int load, int capacity, int latency) {
        this.id = id;
        this.load = load;
        this.capacity = capacity;
        this.latency = latency;
        this.healthy = true;
    }

    public String getId() {
        return id;
    }

    public int getLoad() {
        return load;
    }

    public void setLoad(int load) {
        this.load = load;
    }

    public int getCapacity() {
        return capacity;
    }

    public void setCapacity(int capacity) {
        this.capacity = capacity;
    }

    public int getLatency() {
        return latency;
    }

    public void setLatency(int latency) {
        this.latency = latency;
    }

    public boolean isHealthy() {
        return healthy;
    }

    public void setHealthy(boolean healthy) {
        this.healthy = healthy;
    }
}