import org.junit.Test;
import static org.junit.Assert.*;
import java.util.*;

public class MutualFriendsTest {

    private GraphAnalytics getAnalyticsInstance(Map<Integer, List<Integer>> globalGraph) {
        Map<Integer, List<Integer>> partition1 = new HashMap<>();
        Map<Integer, List<Integer>> partition2 = new HashMap<>();
        int count = 0;
        for (Map.Entry<Integer, List<Integer>> entry : globalGraph.entrySet()) {
            if (count % 2 == 0) {
                partition1.put(entry.getKey(), entry.getValue());
            } else {
                partition2.put(entry.getKey(), entry.getValue());
            }
            count++;
        }
        List<Map<Integer, List<Integer>>> partitions = new ArrayList<>();
        partitions.add(partition1);
        partitions.add(partition2);
        return new GraphAnalytics(partitions);
    }

    @Test
    public void testBasicMutualFriends() {
        // Graph:
        // 1: [2, 3, 4]
        // 2: [1, 3]
        // 3: [1, 2, 4]
        // 4: [1, 3]
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(2, 3, 4));
        graph.put(2, Arrays.asList(1, 3));
        graph.put(3, Arrays.asList(1, 2, 4));
        graph.put(4, Arrays.asList(1, 3));
        
        GraphAnalytics analytics = getAnalyticsInstance(graph);
        List<Integer> result = analytics.get_mutual_friends(1, 2);
        
        // Mutual friend counts for user 1:
        // Candidate 2: common with (1: [2,3,4] and 2: [1,3]) = {3} count = 1
        // Candidate 3: common with (1: [2,3,4] and 3: [1,2,4]) = {2,4} count = 2
        // Candidate 4: common with (1: [2,3,4] and 4: [1,3]) = {3} count = 1
        // Sorted by count descending and then user id ascending, expected: [3,2]
        List<Integer> expected = Arrays.asList(3, 2);
        assertEquals(expected, result);
    }

    @Test
    public void testUserNotPresent() {
        // Graph:
        // 1: [2]
        // 2: [1]
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(2));
        graph.put(2, Arrays.asList(1));
        
        GraphAnalytics analytics = getAnalyticsInstance(graph);
        List<Integer> result = analytics.get_mutual_friends(3, 1);
        
        // User 3 is not present, so expect an empty list.
        assertTrue(result.isEmpty());
    }

    @Test
    public void testKExceedsCandidates() {
        // Graph:
        // 1: [2, 3]
        // 2: [1]
        // 3: [1]
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(2, 3));
        graph.put(2, Arrays.asList(1));
        graph.put(3, Arrays.asList(1));
        
        GraphAnalytics analytics = getAnalyticsInstance(graph);
        List<Integer> result = analytics.get_mutual_friends(1, 5);
        
        // Only candidates are 2 and 3 with mutual friend counts of 0.
        // Expected sorted order by ascending user id: [2, 3]
        List<Integer> expected = Arrays.asList(2, 3);
        assertEquals(expected, result);
    }

    @Test
    public void testTieBreaking() {
        // Graph:
        // 1: [2, 3, 4, 5]
        // 2: [1, 3, 5]
        // 3: [1, 2, 4]
        // 4: [1, 3, 5]
        // 5: [1, 2, 4]
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(2, 3, 4, 5));
        graph.put(2, Arrays.asList(1, 3, 5));
        graph.put(3, Arrays.asList(1, 2, 4));
        graph.put(4, Arrays.asList(1, 3, 5));
        graph.put(5, Arrays.asList(1, 2, 4));
        
        GraphAnalytics analytics = getAnalyticsInstance(graph);
        List<Integer> result = analytics.get_mutual_friends(1, 3);
        
        // Mutual friend counts for user 1:
        // Candidate 2: intersection({2,3,4,5}, {1,3,5}) = {3,5} count = 2
        // Candidate 3: intersection({2,3,4,5}, {1,2,4}) = {2,4} count = 2
        // Candidate 4: intersection({2,3,4,5}, {1,3,5}) = {3,5} count = 2
        // Candidate 5: intersection({2,3,4,5}, {1,2,4}) = {2,4} count = 2
        // All candidates have the same count, so order by user id ascending: [2, 3, 4, 5]
        // k = 3, so expected first three: [2, 3, 4]
        List<Integer> expected = Arrays.asList(2, 3, 4);
        assertEquals(expected, result);
    }

    @Test
    public void testLargeKZeroMutualFriends() {
        // Graph:
        // 1: []
        // 2: []
        // 3: []
        // 4: []
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, new ArrayList<>());
        graph.put(2, new ArrayList<>());
        graph.put(3, new ArrayList<>());
        graph.put(4, new ArrayList<>());
        
        GraphAnalytics analytics = getAnalyticsInstance(graph);
        List<Integer> result = analytics.get_mutual_friends(1, 3);
        
        // All other users have 0 mutual friends,
        // expected order by ascending user id: [2, 3, 4]
        List<Integer> expected = Arrays.asList(2, 3, 4);
        assertEquals(expected, result);
    }
}