public class RoutingDecision {
    private final int requestId;
    private final int serverId;
    private final String status;

    public RoutingDecision(int requestId, int serverId, String status) {
        this.requestId = requestId;
        this.serverId = serverId;
        this.status = status;
    }

    public int getRequestId() {
        return requestId;
    }

    public int getServerId() {
        return serverId;
    }

    public String getStatus() {
        return status;
    }
}