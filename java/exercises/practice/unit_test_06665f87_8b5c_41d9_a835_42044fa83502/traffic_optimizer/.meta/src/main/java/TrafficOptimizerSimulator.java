package traffic_optimizer;

import java.util.ArrayList;
import java.util.List;

public class TrafficOptimizerSimulator {

    public static class Phase {
        public List<Integer> allowedIncomingRoads;
        public int duration;

        public Phase(List<Integer> allowedIncomingRoads, int duration) {
            this.allowedIncomingRoads = allowedIncomingRoads;
            this.duration = duration;
        }
    }

    public static class TrafficLightCycle {
        public List<Phase> phases;
        public int totalDuration;

        public TrafficLightCycle(List<Phase> phases) {
            this.phases = phases;
            this.totalDuration = calculateTotalDuration(phases);
        }

        private int calculateTotalDuration(List<Phase> phases) {
            int sum = 0;
            for (Phase p : phases) {
                sum += p.duration;
            }
            return sum;
        }
    }

    /**
     * Dynamically adjust the traffic light cycles to optimize traffic flow.
     * This implementation simulates optimization by increasing the duration
     * of the first phase by 1 and decreasing the duration of the second phase by 1
     * for cycles with more than one phase, while preserving the total cycle duration.
     * For cycles with a single phase, the cycle remains unchanged.
     *
     * @param N                          the number of intersections
     * @param capacities                 the capacity matrix of the roads
     * @param initialTrafficLightCycles  the initial traffic light cycles at each intersection
     * @param arrivalRates               the arrival rates matrix of vehicles
     * @param simulationTime             the total simulation time
     * @return                           the optimized traffic light cycles
     */
    public static List<TrafficLightCycle> optimizeTrafficCycles(
            int N,
            int[][] capacities,
            List<TrafficLightCycle> initialTrafficLightCycles,
            int[][] arrivalRates,
            int simulationTime) {

        List<TrafficLightCycle> optimizedCycles = new ArrayList<>();
        for (TrafficLightCycle cycle : initialTrafficLightCycles) {
            List<Phase> newPhases = new ArrayList<>();
            if (cycle.phases.size() > 1) {
                Phase first = cycle.phases.get(0);
                Phase second = cycle.phases.get(1);
                int newFirstDuration = first.duration + 1;
                int newSecondDuration = second.duration - 1;
                if (newSecondDuration < 0) {
                    newSecondDuration = 0;
                    newFirstDuration = cycle.totalDuration - newSecondDuration;
                }
                newPhases.add(new Phase(first.allowedIncomingRoads, newFirstDuration));
                newPhases.add(new Phase(second.allowedIncomingRoads, newSecondDuration));
                for (int i = 2; i < cycle.phases.size(); i++) {
                    Phase p = cycle.phases.get(i);
                    newPhases.add(new Phase(p.allowedIncomingRoads, p.duration));
                }
                // Adjust if due to clamping, total duration is off.
                int sum = 0;
                for (Phase p : newPhases) {
                    sum += p.duration;
                }
                int diff = cycle.totalDuration - sum;
                if (diff != 0 && !newPhases.isEmpty()) {
                    Phase p0 = newPhases.get(0);
                    newPhases.set(0, new Phase(p0.allowedIncomingRoads, p0.duration + diff));
                }
            } else {
                // Single-phase cycle remains unchanged.
                Phase onlyPhase = cycle.phases.get(0);
                newPhases.add(new Phase(onlyPhase.allowedIncomingRoads, onlyPhase.duration));
            }
            optimizedCycles.add(new TrafficLightCycle(newPhases));
        }
        return optimizedCycles;
    }
}