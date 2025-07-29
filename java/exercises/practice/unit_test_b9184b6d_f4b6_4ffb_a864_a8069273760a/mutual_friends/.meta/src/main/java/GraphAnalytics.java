import java.util.*;

public class GraphAnalytics {

    private List<Map<Integer, List<Integer>>> partitions;
    private Map<Integer, List<Integer>> globalGraph;

    public GraphAnalytics(List<Map<Integer, List<Integer>>> partitions) {
        this.partitions = partitions;
        // Combine partitions into a global graph view. 
        globalGraph = new HashMap<>();
        for (Map<Integer, List<Integer>> part : partitions) {
            for (Map.Entry<Integer, List<Integer>> entry : part.entrySet()) {
                // Assuming each user only appears in one partition.
                globalGraph.put(entry.getKey(), new ArrayList<>(entry.getValue()));
            }
        }
    }

    public List<Integer> get_mutual_friends(int userId, int k) {
        if (!globalGraph.containsKey(userId)) {
            return new ArrayList<>();
        }
        
        // Retrieve user's friend list as a set for efficient lookup.
        Set<Integer> userFriends = new HashSet<>(globalGraph.get(userId));
        
        // Store candidate mutual friend counts.
        List<Candidate> candidates = new ArrayList<>();
        
        for (Map.Entry<Integer, List<Integer>> entry : globalGraph.entrySet()) {
            int candidateId = entry.getKey();
            if (candidateId == userId) {
                continue;
            }
            
            List<Integer> candidateFriends = entry.getValue();
            int mutualCount = 0;
            
            // Count mutual friends using userFriends set.
            for (Integer friend : candidateFriends) {
                if (userFriends.contains(friend)) {
                    mutualCount++;
                }
            }
            
            candidates.add(new Candidate(candidateId, mutualCount));
        }
        
        // Sort candidates: descending by mutual count, then ascending by candidateId.
        candidates.sort(new Comparator<Candidate>() {
            @Override
            public int compare(Candidate a, Candidate b) {
                if (b.mutualCount != a.mutualCount) {
                    return Integer.compare(b.mutualCount, a.mutualCount);
                }
                return Integer.compare(a.userId, b.userId);
            }
        });
        
        // Select the top k candidates.
        List<Integer> result = new ArrayList<>();
        int limit = Math.min(k, candidates.size());
        for (int i = 0; i < limit; i++) {
            result.add(candidates.get(i).userId);
        }
        return result;
    }
    
    // Private inner class to hold candidate information.
    private static class Candidate {
        int userId;
        int mutualCount;
        
        Candidate(int userId, int mutualCount) {
            this.userId = userId;
            this.mutualCount = mutualCount;
        }
    }
}