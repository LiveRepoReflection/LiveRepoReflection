import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class NetworkOptimizeTest {

    /**
     * Helper method to validate the distribution matrix.
     * Checks that each file is present in at least k servers 
     * and that no server exceeds its capacity.
     */
    private void validateDistribution(int[][] distribution, int[] serverCapacities, int[] fileSizes, int k) {
        int n = distribution.length;
        int numFiles = fileSizes.length;
        
        // Check each file is stored in at least k servers.
        for (int j = 0; j < numFiles; j++) {
            int count = 0;
            for (int i = 0; i < n; i++) {
                if (distribution[i][j] == 1) {
                    count++;
                }
            }
            assertTrue(count >= k, "File " + j + " is stored in " + count + " servers, which is less than required k=" + k);
        }
        
        // Check each server does not exceed its capacity.
        for (int i = 0; i < n; i++) {
            int totalSize = 0;
            for (int j = 0; j < numFiles; j++) {
                if (distribution[i][j] == 1) {
                    totalSize += fileSizes[j];
                }
            }
            assertTrue(totalSize <= serverCapacities[i], "Server " + i + " holds total file size " + totalSize + ", exceeding its capacity of " + serverCapacities[i]);
        }
    }

    @Test
    public void testValidDistribution() {
        // Scenario with 3 servers and 2 files.
        int n = 3;
        int[][] matrix = {
            {0, 1, 2},
            {1, 0, 1},
            {2, 1, 0}
        };
        int[] serverCapacities = {100, 100, 100};
        int[] fileSizes = {50, 30};
        int k = 2;
        int[][] requests = {
            {0, 0},
            {1, 1},
            {2, 0}
        };

        NetworkOptimize optimizer = new NetworkOptimize();
        int[][] distribution = optimizer.optimizeDistribution(n, matrix, serverCapacities, fileSizes, k, requests);
        assertNotNull(distribution, "Expected a valid distribution matrix, but got null.");

        // Check dimensions of the distribution matrix.
        assertEquals(n, distribution.length, "Distribution matrix must have " + n + " rows.");
        for (int i = 0; i < n; i++) {
            assertEquals(fileSizes.length, distribution[i].length, "Row " + i + " of distribution matrix must have " + fileSizes.length + " columns.");
        }

        // Validate constraints on the distribution.
        validateDistribution(distribution, serverCapacities, fileSizes, k);
    }

    @Test
    public void testUnsolvableDueToCapacity() {
        // Scenario where file size is too large for any server.
        int n = 3;
        int[][] matrix = {
            {0, 1, 1},
            {1, 0, 1},
            {1, 1, 0}
        };
        int[] serverCapacities = {50, 50, 50};
        int[] fileSizes = {100};
        int k = 1;
        int[][] requests = {
            {0, 0}
        };

        NetworkOptimize optimizer = new NetworkOptimize();
        int[][] distribution = optimizer.optimizeDistribution(n, matrix, serverCapacities, fileSizes, k, requests);
        assertNull(distribution, "Expected null distribution since no server can store the file due to capacity constraints.");
    }

    @Test
    public void testDisconnectedNetwork() {
        // Scenario with a disconnected network.
        // Two groups: servers [0,1] connected, and servers [2,3] connected.
        int n = 4;
        int[][] matrix = {
            {0, 1, -1, -1},
            {1, 0, -1, -1},
            {-1, -1, 0, 1},
            {-1, -1, 1, 0}
        };
        int[] serverCapacities = {100, 100, 100, 100};
        int[] fileSizes = {30, 40};
        int k = 2;
        int[][] requests = {
            {0, 0},
            {1, 1},
            {2, 0},
            {3, 1}
        };

        NetworkOptimize optimizer = new NetworkOptimize();
        int[][] distribution = optimizer.optimizeDistribution(n, matrix, serverCapacities, fileSizes, k, requests);
        assertNotNull(distribution, "Expected a valid distribution matrix in a disconnected network scenario.");
        
        // Validate constraints on the distribution.
        validateDistribution(distribution, serverCapacities, fileSizes, k);
    }

    @Test
    public void testHighRequestFrequency() {
        // Scenario with high request frequency for a particular file.
        int n = 5;
        int[][] matrix = {
            {0, 2, 2, 3, 1},
            {2, 0, 1, 2, 2},
            {2, 1, 0, 2, 3},
            {3, 2, 2, 0, 1},
            {1, 2, 3, 1, 0}
        };
        int[] serverCapacities = {50, 50, 50, 50, 50};
        int[] fileSizes = {10, 20, 30};
        int k = 2;
        int[][] requests = {
            {0, 0},
            {0, 0},
            {1, 1},
            {2, 0},
            {3, 2},
            {4, 0},
            {0, 0},
            {1, 0},
            {2, 1},
            {3, 1},
            {4, 2},
            {0, 0},
            {1, 0},
            {2, 0},
            {3, 0},
            {4, 0}
        };

        NetworkOptimize optimizer = new NetworkOptimize();
        int[][] distribution = optimizer.optimizeDistribution(n, matrix, serverCapacities, fileSizes, k, requests);
        assertNotNull(distribution, "Expected a valid distribution matrix for high request frequency scenario.");
        
        // Validate constraints on the distribution.
        validateDistribution(distribution, serverCapacities, fileSizes, k);
    }
}