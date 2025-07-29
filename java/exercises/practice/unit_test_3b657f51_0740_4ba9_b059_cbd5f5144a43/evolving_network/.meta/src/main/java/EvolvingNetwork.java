import java.util.*;

public class EvolvingNetwork {

    // Map from userId to User object.
    private Map<Integer, User> users;

    public EvolvingNetwork() {
        users = new HashMap<>();
    }

    // Adds a new user to the network.
    public void addUser(int userId) {
        if (!users.containsKey(userId)) {
            users.put(userId, new User(userId));
        }
    }

    // Removes a user and all related connections from the network.
    public void removeUser(int userId) {
        if (!users.containsKey(userId)) {
            return;
        }
        // Remove the user from the network.
        users.remove(userId);
        // Remove connections from all other users that point to this user.
        for (User user : users.values()) {
            user.connections.remove(userId);
        }
    }

    // Adds a connection from userId1 to userId2 at the given timestamp.
    public void addConnection(int userId1, int userId2, int timestamp) {
        // Ensure both users exist.
        if (!users.containsKey(userId1) || !users.containsKey(userId2)) {
            return;
        }
        User source = users.get(userId1);
        source.addOrUpdateConnection(userId2, timestamp);
    }

    // Removes a connection from userId1 to userId2 exactly at the given timestamp.
    public void removeConnection(int userId1, int userId2, int timestamp) {
        if (!users.containsKey(userId1) || !users.containsKey(userId2)) {
            return;
        }
        User source = users.get(userId1);
        source.removeConnectionAt(userId2, timestamp);
    }

    // Returns a sorted list of userIds that have a connection from userId at the given timestamp.
    public List<Integer> getConnections(int userId, int timestamp) {
        List<Integer> result = new ArrayList<>();
        if (!users.containsKey(userId)) {
            return result;
        }
        User source = users.get(userId);
        for (Map.Entry<Integer, ConnectionHistory> entry : source.connections.entrySet()) {
            ConnectionHistory history = entry.getValue();
            // Check if there is at least one add event <= timestamp.
            Integer addTime = history.addEvents.floor(timestamp);
            if (addTime != null) {
                // Check if there is a removal event exactly at timestamp.
                if (!history.removalEvents.contains(timestamp)) {
                    result.add(entry.getKey());
                }
            }
        }
        Collections.sort(result);
        return result;
    }

    // Recursively calculates the influence score of a user at a given timestamp.
    // The influence score is 1 + decayFactor * (sum of influence scores of connected users).
    // Cycles in the network are broken by treating the influence score of a node already
    // in the recursion stack as 0.
    public double calculateInfluenceScore(int userId, int timestamp, double decayFactor) {
        if (!users.containsKey(userId)) {
            return 0;
        }
        Map<Integer, Double> memo = new HashMap<>();
        return getInfluence(userId, timestamp, decayFactor, new HashSet<>(), memo);
    }

    // Helper method for influence score calculation using DFS with memoization and cycle detection.
    private double getInfluence(int userId, int timestamp, double decayFactor, Set<Integer> recursionStack, Map<Integer, Double> memo) {
        // Check memoization.
        if (memo.containsKey(userId)) {
            return memo.get(userId);
        }
        // Cycle detection.
        if (recursionStack.contains(userId)) {
            return 0;
        }
        recursionStack.add(userId);

        double score = 1.0;
        List<Integer> connections = getConnections(userId, timestamp);
        for (int neighbor : connections) {
            score += decayFactor * getInfluence(neighbor, timestamp, decayFactor, recursionStack, memo);
        }
        recursionStack.remove(userId);
        memo.put(userId, score);
        return score;
    }

    // Inner class representing a user in the network.
    private static class User {
        int userId;
        // Map of target userId -> ConnectionHistory.
        Map<Integer, ConnectionHistory> connections;

        User(int userId) {
            this.userId = userId;
            this.connections = new HashMap<>();
        }

        // Adds or updates a connection to the target user at the given timestamp.
        void addOrUpdateConnection(int targetUserId, int timestamp) {
            ConnectionHistory history = connections.getOrDefault(targetUserId, new ConnectionHistory());
            history.addEvents.add(timestamp);
            // If the same timestamp existed in removal, remove it.
            history.removalEvents.remove(timestamp);
            connections.put(targetUserId, history);
        }

        // Records a removal event for the connection to the target user at the given timestamp.
        void removeConnectionAt(int targetUserId, int timestamp) {
            ConnectionHistory history = connections.get(targetUserId);
            if (history == null) {
                return;
            }
            // Only add removal if there is an add event <= timestamp.
            if (history.addEvents.floor(timestamp) != null) {
                history.removalEvents.add(timestamp);
            }
        }
    }

    // Inner class representing the history of a connection from one user to another.
    private static class ConnectionHistory {
        // Stores the timestamps when a connection was added.
        TreeSet<Integer> addEvents;
        // Stores the timestamps when a connection was removed (only effective when query timestamp equals removal timestamp).
        Set<Integer> removalEvents;

        ConnectionHistory() {
            addEvents = new TreeSet<>();
            removalEvents = new HashSet<>();
        }
    }
}