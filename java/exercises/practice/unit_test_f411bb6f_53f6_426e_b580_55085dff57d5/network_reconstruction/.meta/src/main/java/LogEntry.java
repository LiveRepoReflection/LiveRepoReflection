public class LogEntry {
    private final long timestamp;
    private final int serverId1;
    private final int serverId2;

    public LogEntry(long timestamp, int serverId1, int serverId2) {
        this.timestamp = timestamp;
        this.serverId1 = serverId1;
        this.serverId2 = serverId2;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public int getServerId1() {
        return serverId1;
    }

    public int getServerId2() {
        return serverId2;
    }
}