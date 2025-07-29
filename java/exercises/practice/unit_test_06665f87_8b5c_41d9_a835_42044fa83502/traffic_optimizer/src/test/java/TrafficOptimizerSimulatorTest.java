package traffic_optimizer;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class TrafficOptimizerSimulatorTest {

    /**
     * Helper classes for testing
     */
    static class Phase {
        List<Integer> allowedIncomingRoads;
        int duration;

        Phase(List<Integer> allowedIncomingRoads, int duration) {
            this.allowedIncomingRoads = allowedIncomingRoads;
            this.duration = duration;
        }
    }

    static class TrafficLightCycle {
        List<Phase> phases;
        int totalDuration; // must remain constant

        TrafficLightCycle(List<Phase> phases) {
            this.phases = phases;
            this.totalDuration = phases.stream().mapToInt(phase -> phase.duration).sum();
        }
    }

    /**
     * This is a stub for the main simulation and optimization method.
     * In an actual implementation, this method would simulate the traffic flow over
     * simulationTime and adjust the phase durations of each cycle dynamically.
     *
     * For testing purposes we mimic an optimization that redistributes durations
     * among phases ensuring:
     * - The total duration remains constant.
     * - Each phase duration remains non-negative.
     * - In some cases, the durations are slightly adjusted away from the initial cycle.
     */
    static class TrafficOptimizerSimulator {
        public static List<TrafficLightCycle> optimizeTrafficCycles(
                int N,
                int[][] capacities,
                List<TrafficLightCycle> initialTrafficLightCycles,
                int[][] arrivalRates,
                int simulationTime) {
            
            // In this dummy implementation, we simulate optimization by increasing the duration
            // of the first phase by 1 and decreasing the duration of a subsequent phase by 1
            // if possible, to mimic a dynamic adjustment while keeping total duration constant.
            List<TrafficLightCycle> optimizedCycles = new ArrayList<>();
            for (TrafficLightCycle cycle : initialTrafficLightCycles) {
                List<Phase> newPhases = new ArrayList<>();
                if (cycle.phases.size() > 1) {
                    // adjust the first two phases if possible
                    Phase first = cycle.phases.get(0);
                    Phase second = cycle.phases.get(1);
                    int newFirstDuration = first.duration + 1;
                    int newSecondDuration = Math.max(second.duration - 1, 0);
                    newPhases.add(new Phase(first.allowedIncomingRoads, newFirstDuration));
                    newPhases.add(new Phase(second.allowedIncomingRoads, newSecondDuration));
                    // copy remaining phases unchanged
                    for (int i = 2; i < cycle.phases.size(); i++) {
                        Phase p = cycle.phases.get(i);
                        newPhases.add(new Phase(p.allowedIncomingRoads, p.duration));
                    }
                    // ensure that total duration remains as original. If reduction in second phase was clamped to 0,
                    // adjust the first phase's duration accordingly.
                    int sum = newPhases.stream().mapToInt(p -> p.duration).sum();
                    int diff = cycle.totalDuration - sum;
                    if (diff != 0 && !newPhases.isEmpty()) {
                        Phase p0 = newPhases.get(0);
                        newPhases.set(0, new Phase(p0.allowedIncomingRoads, p0.duration + diff));
                    }
                } else {
                    // For cycles with one phase, leave unchanged.
                    newPhases.add(new Phase(cycle.phases.get(0).allowedIncomingRoads, cycle.phases.get(0).duration));
                }
                optimizedCycles.add(new TrafficLightCycle(newPhases));
            }
            return optimizedCycles;
        }
    }

    @Test
    void testOptimizedCyclesMaintainTotalDuration() {
        // Setup: Create 3 intersections with varying phase configurations.
        // Intersection 0 and 1: 2-phase cycle; Intersection 2: 1-phase cycle.
        TrafficLightCycle cycle0 = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(1), 15),
                new Phase(Arrays.asList(2), 10)
        ));

        TrafficLightCycle cycle1 = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(0, 2), 20),
                new Phase(Arrays.asList(0), 5)
        ));

        TrafficLightCycle cycle2 = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(1), 25)
        ));

        List<TrafficLightCycle> initialCycles = Arrays.asList(cycle0, cycle1, cycle2);

        // Create dummy capacities and arrivalRates matrices for a graph with 3 intersections.
        int[][] capacities = {
                {0, 50, 30},
                {40, 0, 20},
                {10, 60, 0}
        };
        int[][] arrivalRates = {
                {0, 10, 5},
                {15, 0, 7},
                {3, 8, 0}
        };

        int simulationTime = 200;

        List<TrafficLightCycle> optimizedCycles = TrafficOptimizerSimulator.optimizeTrafficCycles(
                3, capacities, initialCycles, arrivalRates, simulationTime);

        // Check that for each cycle, the total duration remains unchanged.
        for (int i = 0; i < initialCycles.size(); i++) {
            TrafficLightCycle initial = initialCycles.get(i);
            TrafficLightCycle optimized = optimizedCycles.get(i);
            int initialTotal = initial.totalDuration;
            int optimizedTotal = optimized.phases.stream().mapToInt(phase -> phase.duration).sum();
            assertEquals(initialTotal, optimizedTotal, "Total duration should remain constant for cycle " + i);
        }
    }

    @Test
    void testOptimizedCyclesNonNegativeDurations() {
        // Setup: Create a cycle with two phases.
        TrafficLightCycle cycle = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(1, 2), 5),
                new Phase(Arrays.asList(0), 3)
        ));

        List<TrafficLightCycle> initialCycles = new ArrayList<>();
        initialCycles.add(cycle);

        int[][] capacities = {
                {0, 20, 20},
                {20, 0, 20},
                {20, 20, 0}
        };
        int[][] arrivalRates = {
                {0, 5, 5},
                {5, 0, 5},
                {5, 5, 0}
        };
        int simulationTime = 150;

        List<TrafficLightCycle> optimizedCycles = TrafficOptimizerSimulator.optimizeTrafficCycles(
                3, capacities, initialCycles, arrivalRates, simulationTime);

        // Verify that none of the phase durations are negative.
        TrafficLightCycle optimized = optimizedCycles.get(0);
        for (int i = 0; i < optimized.phases.size(); i++) {
            Phase phase = optimized.phases.get(i);
            assertTrue(phase.duration >= 0, "Phase duration should be non-negative at index " + i);
        }
    }

    @Test
    void testOptimizedCyclesDifferentFromInitialWhenPossible() {
        // Setup: Create a cycle with two phases.
        TrafficLightCycle cycle = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(1), 12),
                new Phase(Arrays.asList(2), 8)
        ));

        List<TrafficLightCycle> initialCycles = new ArrayList<>();
        initialCycles.add(cycle);

        int[][] capacities = {
                {0, 100, 50},
                {30, 0, 60},
                {40, 20, 0}
        };
        int[][] arrivalRates = {
                {0, 25, 15},
                {20, 0, 10},
                {5, 30, 0}
        };
        int simulationTime = 300;

        List<TrafficLightCycle> optimizedCycles = TrafficOptimizerSimulator.optimizeTrafficCycles(
                3, capacities, initialCycles, arrivalRates, simulationTime);

        // For cycles with more than one phase, the simulator should adjust the durations.
        TrafficLightCycle optimized = optimizedCycles.get(0);
        // Check that at least one phase has a different duration compared to the initial cycle.
        boolean isDifferent = false;
        for (int i = 0; i < cycle.phases.size(); i++) {
            if (cycle.phases.get(i).duration != optimized.phases.get(i).duration) {
                isDifferent = true;
                break;
            }
        }
        assertTrue(isDifferent, "Expected at least one phase duration to be adjusted.");
    }

    @Test
    void testSimulationWithSinglePhaseCycle() {
        // Setup: Create a cycle with a single phase.
        TrafficLightCycle cycle = new TrafficLightCycle(Arrays.asList(
                new Phase(Arrays.asList(0, 1), 30)
        ));

        List<TrafficLightCycle> initialCycles = new ArrayList<>();
        initialCycles.add(cycle);

        int[][] capacities = {
                {0, 40},
                {40, 0}
        };
        int[][] arrivalRates = {
                {0, 20},
                {20, 0}
        };
        int simulationTime = 250;

        List<TrafficLightCycle> optimizedCycles = TrafficOptimizerSimulator.optimizeTrafficCycles(
                2, capacities, initialCycles, arrivalRates, simulationTime);

        // For a single phase cycle, there should be no change.
        TrafficLightCycle optimized = optimizedCycles.get(0);
        assertEquals(cycle.phases.get(0).duration, optimized.phases.get(0).duration,
                "Single-phase cycle should remain unchanged.");
        int optimizedTotal = optimized.phases.get(0).duration;
        assertEquals(cycle.totalDuration, optimizedTotal,
                "Total duration should remain constant for a single phase cycle.");
    }
}