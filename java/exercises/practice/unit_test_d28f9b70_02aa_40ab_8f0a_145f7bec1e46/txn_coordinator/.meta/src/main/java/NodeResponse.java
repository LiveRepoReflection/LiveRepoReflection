public class NodeResponse {
    private final boolean ack;
    private final String reason;

    public NodeResponse(boolean ack, String reason) {
        this.ack = ack;
        this.reason = reason;
    }

    public boolean isAck() {
        return ack;
    }

    public String getReason() {
        return reason;
    }
}