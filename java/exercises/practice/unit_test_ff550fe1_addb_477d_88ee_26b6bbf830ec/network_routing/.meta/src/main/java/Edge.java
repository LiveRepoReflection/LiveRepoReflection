public class Edge {
    private final int server1;
    private final int server2;
    private final int latency;

    public Edge(int server1, int server2, int latency) {
        this.server1 = server1;
        this.server2 = server2;
        this.latency = latency;
    }

    public int getServer1() {
        return server1;
    }

    public int getServer2() {
        return server2;
    }

    public int getLatency() {
        return latency;
    }
}