import java.util.Map;

public class OptimizationResult {
    private final int cycleTime;
    private final Map<Integer, Map<Integer, Integer>> schedule;
    private final double averageTravelTime;
    private final String errorMessage;

    public OptimizationResult(int cycleTime, Map<Integer, Map<Integer, Integer>> schedule, double averageTravelTime, String errorMessage) {
        this.cycleTime = cycleTime;
        this.schedule = schedule;
        this.averageTravelTime = averageTravelTime;
        this.errorMessage = errorMessage;
    }

    public int getCycleTime() {
        return cycleTime;
    }

    public Map<Integer, Map<Integer, Integer>> getSchedule() {
        return schedule;
    }

    public double getAverageTravelTime() {
        return averageTravelTime;
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}