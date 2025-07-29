import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertTimeoutPreemptively;
import static java.time.Duration.ofSeconds;

public class SkylinePerformanceTest {
    
    @Test
    public void testPerformanceWithLargeNumberOfBuildings() {
        assertTimeoutPreemptively(ofSeconds(10), () -> {
            DynamicSkyline skyline = new DynamicSkyline();
            Random random = new Random(42); // Fixed seed for reproducibility
            
            // Add 10,000 random buildings
            for (int i = 0; i < 10_000; i++) {
                int left = random.nextInt(1_000_000);
                int right = left + 1 + random.nextInt(1000);
                int height = 1 + random.nextInt(1000);
                skyline.addBuilding(left, right, height);
                
                // Get skyline occasionally to test performance
                if (i % 1000 == 0) {
                    skyline.getSkyline();
                }
            }
            
            // Remove 5,000 buildings
            for (int i = 0; i < 5_000; i++) {
                int left = random.nextInt(1_000_000);
                int right = left + 1 + random.nextInt(1000);
                int height = 1 + random.nextInt(1000);
                
                try {
                    skyline.removeBuilding(left, right, height);
                } catch (IllegalArgumentException e) {
                    // Ignore if building doesn't exist
                }
                
                // Get skyline occasionally to test performance
                if (i % 500 == 0) {
                    skyline.getSkyline();
                }
            }
            
            // Final skyline check
            List<List<Integer>> result = skyline.getSkyline();
        });
    }
    
    @Test
    public void testPerformanceWithOverlappingBuildings() {
        assertTimeoutPreemptively(ofSeconds(5), () -> {
            DynamicSkyline skyline = new DynamicSkyline();
            
            // Add 1,000 buildings all overlapping in the same area
            for (int i = 0; i < 1_000; i++) {
                int height = 1 + i % 100;
                skyline.addBuilding(1000, 2000, height);
            }
            
            // Get skyline multiple times
            for (int i = 0; i < 10; i++) {
                skyline.getSkyline();
            }
            
            // Remove 500 buildings
            for (int i = 0; i < 500; i++) {
                int height = 1 + i % 100;
                try {
                    skyline.removeBuilding(1000, 2000, height);
                } catch (IllegalArgumentException e) {
                    // Ignore if building doesn't exist
                }
            }
            
            // Final skyline check
            List<List<Integer>> result = skyline.getSkyline();
        });
    }
    
    @Test
    public void testPerformanceWithSparseBuildings() {
        assertTimeoutPreemptively(ofSeconds(5), () -> {
            DynamicSkyline skyline = new DynamicSkyline();
            Random random = new Random(42); // Fixed seed for reproducibility
            
            // Add 10,000 buildings with very sparse distribution
            for (int i = 0; i < 5_000; i++) {
                int left = random.nextInt(100_000_000);
                int right = left + 1 + random.nextInt(100);
                int height = 1 + random.nextInt(1000);
                skyline.addBuilding(left, right, height);
            }
            
            // Get skyline multiple times
            for (int i = 0; i < 5; i++) {
                skyline.getSkyline();
            }
            
            // Final skyline check
            List<List<Integer>> result = skyline.getSkyline();
        });
    }
}