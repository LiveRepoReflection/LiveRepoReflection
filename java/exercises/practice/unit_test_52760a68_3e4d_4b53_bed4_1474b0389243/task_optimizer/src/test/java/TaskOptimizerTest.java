import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.*;

public class TaskOptimizerTest {

    // Helper method to compare doubles within a tolerance.
    private void assertDoubleEquals(double expected, double actual) {
        double tolerance = 1e-6;
        assertEquals(expected, actual, tolerance);
    }

    @Test
    public void testSingleTaskSingleEngineer() {
        int n = 1;
        int m = 1;
        // Engineer has skill 5 in category 0.
        int[][] skills = { {5} };
        // Task: category 0, duration 5.
        int[][] tasks = { {0, 5} };
        // No dependencies.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        // Engineer available for 10 hours.
        int[] availability = {10};
        int deadline = 10;

        // Expected cost = 5 / 5 = 1.0
        double expectedCost = 1.0;
        double result = TaskOptimizer.getMinimumCost(n, m, skills, tasks, dependencies, availability, deadline);
        assertDoubleEquals(expectedCost, result);
    }

    @Test
    public void testMultipleEngineersNoDependencies() {
        int n = 2;
        int m = 2;
        
        // Engineer 0: skills [0, 3]; Engineer 1: skills [4, 5]
        int[][] skills = {
            {0, 3},
            {4, 5}
        };
        
        // Task 0: category 0, duration 4; Task 1: category 1, duration 6.
        int[][] tasks = {
            {0, 4},
            {1, 6}
        };
        
        // No dependencies for both tasks.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        dependencies.add(new ArrayList<>());
        
        // Each engineer available for 10 hours.
        int[] availability = {10, 10};
        int deadline = 10;
        
        // Only engineer 1 can do Task0 since engineer 0 has skill 0 for category 0.
        // Cost for Task0 for engineer 1 = 4 / 4 = 1.0.
        // For Task1, best cost is for engineer 1: 6 / 5 = 1.2 
        // Total expected cost = 1.0 + 1.2 = 2.2.
        double expectedCost = 2.2;
        double result = TaskOptimizer.getMinimumCost(n, m, skills, tasks, dependencies, availability, deadline);
        assertDoubleEquals(expectedCost, result);
    }

    @Test
    public void testDependenciesComplex() {
        int n = 2;
        int m = 3;
        // Assume two categories: 0 and 1.
        // Engineer 0: skills [5, 3]; Engineer 1: skills [6, 1]
        int[][] skills = {
            {5, 3},
            {6, 1}
        };
        // Tasks:
        // Task 0: category 0, duration 3.
        // Task 1: category 1, duration 6.
        // Task 2: category 0, duration 4.
        int[][] tasks = {
            {0, 3},
            {1, 6},
            {0, 4}
        };
        // Dependencies:
        // Task 0: no dependencies.
        // Task 1: no dependencies.
        // Task 2 depends on Task 0 and Task 1.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>()); // Task 0
        dependencies.add(new ArrayList<>()); // Task 1
        List<Integer> depForTask2 = new ArrayList<>();
        depForTask2.add(0);
        depForTask2.add(1);
        dependencies.add(depForTask2);
        
        // Each engineer available for 10 hours.
        int[] availability = {10, 10};
        int deadline = 15;
        
        // Optimal assignment:
        // Task 0: Best with Engineer 1: cost = 3/6 = 0.5
        // Task 1: Best with Engineer 0: cost = 6/3 = 2.0
        // Task 2: Best with Engineer 1: cost = 4/6 = 0.666667 (Engineer 1 has enough availability: 10-3=7 hours remaining)
        // Total expected cost: 0.5 + 2.0 + 0.666667 = 3.166667 approximately.
        double expectedCost = 3.166667;
        double result = TaskOptimizer.getMinimumCost(n, m, skills, tasks, dependencies, availability, deadline);
        assertDoubleEquals(expectedCost, result);
    }
    
    @Test
    public void testInsufficientAvailability() {
        int n = 1;
        int m = 1;
        // Engineer with skill 5 in category 0.
        int[][] skills = { {5} };
        // Task: category 0, duration 10.
        int[][] tasks = { {0, 10} };
        // No dependencies.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        // Engineer available for only 5 hours.
        int[] availability = {5};
        int deadline = 10;
        
        // Not enough availability despite deadline being met in isolation.
        double expectedCost = -1.0;
        double result = TaskOptimizer.getMinimumCost(n, m, skills, tasks, dependencies, availability, deadline);
        assertDoubleEquals(expectedCost, result);
    }
    
    @Test
    public void testMultipleAssignmentsAndScheduling() {
        int n = 3;
        int m = 4;
        // Engineers:
        // Engineer 0: skills in categories 0,1: [4, 2]
        // Engineer 1: skills in categories 0,1: [3, 5]
        // Engineer 2: skills in categories 0,1: [6, 1]
        int[][] skills = {
            {4, 2},
            {3, 5},
            {6, 1}
        };
        // Tasks:
        // Task 0: category 0, duration 3.
        // Task 1: category 1, duration 4.
        // Task 2: category 0, duration 5.
        // Task 3: category 1, duration 2.
        int[][] tasks = {
            {0, 3},
            {1, 4},
            {0, 5},
            {1, 2}
        };
        // Dependencies:
        // Task 0: no dependencies.
        // Task 1: depends on Task 0.
        // Task 2: depends on Task 0.
        // Task 3: depends on Task 1 and Task 2.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());  // Task 0
        List<Integer> dep1 = new ArrayList<>();
        dep1.add(0);
        dependencies.add(dep1);  // Task 1
        List<Integer> dep2 = new ArrayList<>();
        dep2.add(0);
        dependencies.add(dep2);  // Task 2
        List<Integer> dep3 = new ArrayList<>();
        dep3.add(1);
        dep3.add(2);
        dependencies.add(dep3);  // Task 3
        
        // Each engineer available for enough hours.
        int[] availability = {10, 10, 10};
        int deadline = 20;
        
        // A possible optimal assignment:
        // Task 0 (cat 0, dur 3): Engineer 2 -> cost = 3/6 = 0.5
        // Task 1 (cat 1, dur 4): Engineer 1 -> cost = 4/5 = 0.8
        // Task 2 (cat 0, dur 5): Engineer 2 -> cost = 5/6 ≈ 0.833333
        // Task 3 (cat 1, dur 2): Engineer 1 -> cost = 2/5 = 0.4 
        // Total expected cost = 0.5 + 0.8 + 0.833333 + 0.4 = 2.533333
        double expectedCost = 2.533333;
        double result = TaskOptimizer.getMinimumCost(n, m, skills, tasks, dependencies, availability, deadline);
        assertDoubleEquals(expectedCost, result);
    }
}