import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class SocialNetworkGraph {
    private final Map<Long, Set<Long>> network;

    public SocialNetworkGraph() {
        this.network = new HashMap<>();
    }

    public void addUser(long userId) {
        if (userId <= 0) {
            return;
        }
        network.putIfAbsent(userId, new HashSet<>());
    }

    public void addConnection(long userId1, long userId2) {
        if (userId1 <= 0 || userId2 <= 0 || userId1 == userId2) {
            return;
        }
        addUser(userId1);
        addUser(userId2);
        Set<Long> friends1 = network.get(userId1);
        Set<Long> friends2 = network.get(userId2);
        friends1.add(userId2);
        friends2.add(userId1);
    }

    public void removeConnection(long userId1, long userId2) {
        if (userId1 <= 0 || userId2 <= 0 || userId1 == userId2) {
            return;
        }
        Set<Long> friends1 = network.get(userId1);
        Set<Long> friends2 = network.get(userId2);
        if (friends1 != null) {
            friends1.remove(userId2);
        }
        if (friends2 != null) {
            friends2.remove(userId1);
        }
    }

    public List<Long> getFriends(long userId) {
        if (!network.containsKey(userId)) {
            return Collections.emptyList();
        }
        List<Long> friendsList = new ArrayList<>(network.get(userId));
        Collections.sort(friendsList);
        return friendsList;
    }

    public List<Long> getMutualFriends(long userId1, long userId2) {
        if (!network.containsKey(userId1) || !network.containsKey(userId2)) {
            return Collections.emptyList();
        }
        Set<Long> friends1 = network.get(userId1);
        Set<Long> friends2 = network.get(userId2);
        List<Long> mutual = new ArrayList<>();
        for (Long friend : friends1) {
            if (friends2.contains(friend)) {
                mutual.add(friend);
            }
        }
        Collections.sort(mutual);
        return mutual;
    }

    public List<Long> getRecommendedFriends(long userId, int recommendationCount) {
        if (recommendationCount <= 0 || !network.containsKey(userId)) {
            return Collections.emptyList();
        }
        Set<Long> userFriends = network.get(userId);
        Map<Long, Integer> candidateCounts = new HashMap<>();
        // Iterate over user's friends
        for (Long friendId : userFriends) {
            Set<Long> friendsOfFriend = network.get(friendId);
            if (friendsOfFriend != null) {
                for (Long candidate : friendsOfFriend) {
                    if (candidate == userId || userFriends.contains(candidate)) {
                        continue;
                    }
                    candidateCounts.put(candidate, candidateCounts.getOrDefault(candidate, 0) + 1);
                }
            }
        }
        // Create a list of candidates to sort
        List<Long> candidates = new ArrayList<>(candidateCounts.keySet());
        // Sort by mutual friend count descending, then by user id ascending
        Collections.sort(candidates, (a, b) -> {
            int countDiff = candidateCounts.get(b) - candidateCounts.get(a);
            if (countDiff != 0) {
                return countDiff;
            }
            return Long.compare(a, b);
        });
        // Limit the list to recommendationCount and sort final list in the required order:
        // As per the problem, the final list should be sorted in descending order based on mutual friend count.
        List<Long> recommendations = new ArrayList<>();
        for (int i = 0; i < Math.min(recommendationCount, candidates.size()); i++) {
            recommendations.add(candidates.get(i));
        }
        return recommendations;
    }
}