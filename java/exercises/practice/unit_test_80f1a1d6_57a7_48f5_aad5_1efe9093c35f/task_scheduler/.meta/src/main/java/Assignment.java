public class Assignment {
    private final Node node;
    private final int startTimeSeconds;

    public Assignment(Node node, int startTimeSeconds) {
        this.node = node;
        this.startTimeSeconds = startTimeSeconds;
    }

    public Node getNode() {
        return node;
    }

    public int getStartTimeSeconds() {
        return startTimeSeconds;
    }
}