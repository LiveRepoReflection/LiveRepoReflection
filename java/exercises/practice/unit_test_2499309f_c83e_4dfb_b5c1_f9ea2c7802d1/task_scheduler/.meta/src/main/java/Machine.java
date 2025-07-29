public class Machine {
    public final String id;
    public final int cpuCores;
    public final long memory;
    public final long diskSpace;
    
    public Machine(String id, int cpuCores, long memory, long diskSpace) {
        this.id = id;
        this.cpuCores = cpuCores;
        this.memory = memory;
        this.diskSpace = diskSpace;
    }
}