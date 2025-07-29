public class WorkerNode {
    private String id;
    private int cpuCapacity;
    private int memoryCapacity;
    private int diskCapacity;

    public WorkerNode(String id, int cpuCapacity, int memoryCapacity, int diskCapacity) {
        this.id = id;
        this.cpuCapacity = cpuCapacity;
        this.memoryCapacity = memoryCapacity;
        this.diskCapacity = diskCapacity;
    }

    public String getId() {
        return id;
    }

    public int getCpuCapacity() {
        return cpuCapacity;
    }

    public int getMemoryCapacity() {
        return memoryCapacity;
    }

    public int getDiskCapacity() {
        return diskCapacity;
    }
}