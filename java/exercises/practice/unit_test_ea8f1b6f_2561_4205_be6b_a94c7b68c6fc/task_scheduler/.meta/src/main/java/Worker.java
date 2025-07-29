public class Worker {
    private int workerId;
    private int cpuCapacity;
    private int memoryCapacity;
    private int networkBandwidthCapacity;

    public Worker(int workerId, int cpuCapacity, int memoryCapacity, int networkBandwidthCapacity) {
        this.workerId = workerId;
        this.cpuCapacity = cpuCapacity;
        this.memoryCapacity = memoryCapacity;
        this.networkBandwidthCapacity = networkBandwidthCapacity;
    }

    public int getWorkerId() {
        return workerId;
    }

    public int getCpuCapacity() {
        return cpuCapacity;
    }

    public int getMemoryCapacity() {
        return memoryCapacity;
    }

    public int getNetworkBandwidthCapacity() {
        return networkBandwidthCapacity;
    }

    public boolean canRun(Task task) {
        return cpuCapacity >= task.getCpuRequired() &&
               memoryCapacity >= task.getMemoryRequired() &&
               networkBandwidthCapacity >= task.getNetworkBandwidthRequired();
    }
}