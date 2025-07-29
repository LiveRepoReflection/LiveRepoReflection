import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class NetworkProfitTest {

    // Test 1: Single town, no links. Expect profit equal to the town's population.
    @Test
    public void testSingleTownNoLinks() {
        int numTowns = 1;
        int[] townPopulations = {100};
        int[][] linkCosts = {};
        int budget = 10;
        int expectedProfit = 100; // Single town chosen, no cable cost.
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 2: Two towns connected by an edge cannot satisfy two-path reliability,
    // so the optimal solution is to pick the town with the higher population.
    @Test
    public void testTwoTownsSingleLink() {
        int numTowns = 2;
        int[] townPopulations = {50, 60};
        int[][] linkCosts = { {0, 1, 40} };
        int budget = 40;
        int expectedProfit = 60; // Only the higher revenue single town (town 1) is chosen.
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 3: A triangle ensures two distinct paths between any two nodes.
    @Test
    public void testTriangleReliableNetwork() {
        int numTowns = 3;
        int[] townPopulations = {10, 20, 30};
        int[][] linkCosts = { {0, 1, 5}, {1, 2, 5}, {0, 2, 5} };
        int budget = 15;
        // Total revenue = 10+20+30 = 60, total cable cost = 5+5+5 = 15, profit = 60 - 15 = 45.
        int expectedProfit = 45;
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 4: A triangle network is too expensive. Optimal is to use single high-revenue town.
    @Test
    public void testTriangleTooExpensiveForReliableNetwork() {
        int numTowns = 3;
        int[] townPopulations = {100, 10, 10};
        int[][] linkCosts = { {0, 1, 50}, {1, 2, 50}, {0, 2, 50} };
        int budget = 100;
        // Cannot build a reliable two-path network with multiple nodes due to high cable cost.
        // Thus, choose single town with max revenue: 100.
        int expectedProfit = 100;
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 5: Larger graph with two potential triangles. Optimal selection is the triangle with maximum profit.
    @Test
    public void testLargerGraphMultipleReliableGroups() {
        int numTowns = 5;
        int[] townPopulations = {80, 50, 60, 70, 40};
        int[][] linkCosts = {
            // Triangle among towns 0, 1, 2.
            {0, 1, 30}, {1, 2, 30}, {0, 2, 30},
            // Triangle among towns 2, 3, 4.
            {2, 3, 40}, {3, 4, 40}, {2, 4, 40},
            // Extra link connecting the two groups, not sufficient for reliability on its own.
            {1, 3, 60}
        };
        int budget = 150;
        // Considering reliable groups:
        // Group {0,1,2}: revenue = 80+50+60 = 190, cost = 30+30+30 = 90, profit = 100.
        // Group {2,3,4}: revenue = 60+70+40 = 170, cost = 40+40+40 = 120, profit = 50.
        // Individual high revenue town: 80.
        // Optimal profit is 100.
        int expectedProfit = 100;
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 6: Two towns with available cable, reliability constraint forces selection of single node.
    @Test
    public void testTwoTownsReliabilityConstraintNotMet() {
        int numTowns = 2;
        int[] townPopulations = {10, 20};
        int[][] linkCosts = { {0, 1, 5} };
        int budget = 10;
        // With only one link, reliable two-path connectivity cannot be met.
        // Thus, best choice is to pick the town with highest revenue.
        int expectedProfit = 20;
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
    
    // Test 7: Budget is zero, can only pick a single town.
    @Test
    public void testZeroBudget() {
        int numTowns = 4;
        int[] townPopulations = {25, 60, 35, 45};
        int[][] linkCosts = { {0, 1, 10}, {1, 2, 10}, {2, 3, 10}, {0, 3, 10} };
        int budget = 0;
        // Cannot afford any links so best is to choose the single town with highest revenue.
        int expectedProfit = 60;
        
        int result = NetworkProfit.computeMaxProfit(numTowns, townPopulations, linkCosts, budget);
        assertEquals(expectedProfit, result);
    }
}