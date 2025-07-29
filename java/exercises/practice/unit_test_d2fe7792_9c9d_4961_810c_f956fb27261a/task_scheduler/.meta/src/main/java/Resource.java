public class Resource {
    private int cpuCores;
    private int memoryMB;

    public Resource(int cpuCores, int memoryMB) {
        this.cpuCores = cpuCores;
        this.memoryMB = memoryMB;
    }

    public int getCpuCores() {
        return cpuCores;
    }

    public int getMemoryMB() {
        return memoryMB;
    }
}