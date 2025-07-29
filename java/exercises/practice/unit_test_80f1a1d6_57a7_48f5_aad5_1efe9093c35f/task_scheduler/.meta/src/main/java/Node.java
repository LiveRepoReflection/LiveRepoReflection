public class Node {
    private final int cpuCores;
    private final int memoryGB;
    private final int gpuCount;

    public Node(int cpuCores, int memoryGB, int gpuCount) {
        this.cpuCores = cpuCores;
        this.memoryGB = memoryGB;
        this.gpuCount = gpuCount;
    }

    public int getCpuCores() {
        return cpuCores;
    }

    public int getMemoryGB() {
        return memoryGB;
    }

    public int getGpuCount() {
        return gpuCount;
    }
}