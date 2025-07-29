public class Stream {
    private int streamId;
    private int priority;
    private int dataSize;

    public Stream(int streamId, int priority, int dataSize) {
        this.streamId = streamId;
        this.priority = priority;
        this.dataSize = dataSize;
    }

    public int getStreamId() {
        return streamId;
    }

    public int getPriority() {
        return priority;
    }

    public int getDataSize() {
        return dataSize;
    }
}