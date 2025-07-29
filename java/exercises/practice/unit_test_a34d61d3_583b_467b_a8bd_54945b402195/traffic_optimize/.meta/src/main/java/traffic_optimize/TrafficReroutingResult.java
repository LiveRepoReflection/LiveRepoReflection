package traffic_optimize;

public class TrafficReroutingResult {
    private double afterTotalTime;
    private double reroutedFlow;
    private double originalFlow;

    public TrafficReroutingResult(double afterTotalTime, double reroutedFlow, double originalFlow) {
        this.afterTotalTime = afterTotalTime;
        this.reroutedFlow = reroutedFlow;
        this.originalFlow = originalFlow;
    }

    public double getAfterTotalTime() {
        return afterTotalTime;
    }

    public double getReroutedFlow() {
        return reroutedFlow;
    }

    public double getOriginalFlow() {
        return originalFlow;
    }
}