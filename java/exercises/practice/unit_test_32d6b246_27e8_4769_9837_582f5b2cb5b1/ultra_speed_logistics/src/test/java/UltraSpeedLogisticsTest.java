import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
import java.util.*;

class UltraSpeedLogisticsTest {
    private UltraSpeedLogistics logistics = new UltraSpeedLogistics();

    @Test
    void testBasicRouteWithoutTraffic() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{1, 2, 50}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 2, 150}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).hasSize(1);
        assertThat(result.get(0).get(0)).containsExactly(0, 1, 2);
    }

    @Test
    void testMultiplePathsWithTraffic() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{0, 2, 75},
            new int[]{1, 2, 25},
            new int[]{2, 3, 100},
            new int[]{1, 3, 200}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 3, 300}
        );
        List<int[]> trafficEvents = Arrays.asList(
            new int[]{0, 1, 50, 100, 20},
            new int[]{1, 2, 0, 200, 50}
        );
        int k = 2;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).hasSize(2);
        assertThat(result.get(0).get(0)).containsExactly(0, 2, 3);
        assertThat(result.get(0).get(1)).containsExactly(0, 1, 2, 3);
    }

    @Test
    void testDeadlineConstraint() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 100},
            new int[]{1, 2, 100}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 2, 150}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEmpty();
    }

    @Test
    void testDisconnectedGraph() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{2, 3, 50}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 3, 300}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEmpty();
    }

    @Test
    void testMultipleRequests() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{1, 2, 50},
            new int[]{0, 2, 120}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 2, 150},
            new int[]{1, 2, 100}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 2;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(2);
        assertThat(result.get(0)).hasSize(2);
        assertThat(result.get(1)).hasSize(1);
    }

    @Test
    void testComplexTrafficPatterns() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{1, 2, 50},
            new int[]{0, 2, 90}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 2, 200}
        );
        List<int[]> trafficEvents = Arrays.asList(
            new int[]{0, 1, 0, 100, 50},
            new int[]{1, 2, 0, 100, 50},
            new int[]{0, 2, 0, 100, 20}
        );
        int k = 2;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).hasSizeGreaterThanOrEqualTo(1);
    }

    @Test
    void testEmptyGraph() {
        List<int[]> edges = new ArrayList<>();
        List<int[]> requests = Arrays.asList(
            new int[]{0, 1, 100}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEmpty();
    }

    @Test
    void testSameStartAndEndNode() {
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 50},
            new int[]{1, 0, 50}
        );
        List<int[]> requests = Arrays.asList(
            new int[]{0, 0, 100}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 1024 * 1024;

        List<List<List<Integer>>> result = logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit);
        
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).hasSize(1);
        assertThat(result.get(0).get(0)).containsExactly(0);
    }

    @Test
    void testExceedingCacheLimit() {
        List<int[]> edges = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            edges.add(new int[]{i, i + 1, 1});
        }
        List<int[]> requests = Arrays.asList(
            new int[]{0, 999, 1000}
        );
        List<int[]> trafficEvents = new ArrayList<>();
        int k = 1;
        int cacheLimit = 100; // Very small cache limit

        assertThatThrownBy(() -> 
            logistics.findEfficientRoutes(edges, requests, trafficEvents, k, cacheLimit)
        ).isInstanceOf(RuntimeException.class)
         .hasMessageContaining("Cache limit exceeded");
    }
}