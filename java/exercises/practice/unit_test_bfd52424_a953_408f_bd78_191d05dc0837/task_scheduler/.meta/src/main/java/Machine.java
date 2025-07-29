public class Machine {
    public String id;
    public int totalCpu;
    public int totalMemory;
    public int availableCpu;
    public int availableMemory;

    public Machine(String id, int totalCpu, int totalMemory) {
        this.id = id;
        this.totalCpu = totalCpu;
        this.totalMemory = totalMemory;
        this.availableCpu = totalCpu;
        this.availableMemory = totalMemory;
    }
}