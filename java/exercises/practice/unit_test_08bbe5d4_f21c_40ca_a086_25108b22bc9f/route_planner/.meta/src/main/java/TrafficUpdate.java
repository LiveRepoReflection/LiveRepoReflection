public class TrafficUpdate {
    public final int from;
    public final int to;
    public final int startTime;
    public final int endTime;
    public final double factor;

    public TrafficUpdate(int from, int to, int startTime, int endTime, double factor) {
        this.from = from;
        this.to = to;
        this.startTime = startTime;
        this.endTime = endTime;
        this.factor = factor;
    }
}